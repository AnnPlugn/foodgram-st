from rest_framework.validators import UniqueTogetherValidator
from django.db import transaction
from ingredients.models import IngredientModel
from recipes.models import Dish, ComponentRecipe, FavoriteDish, ShoppingCart, ShortUrl
from users.models import SubscriptionPlan, BlogerUser
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class ProfileImageSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(allow_null=True, required=False)

    class Meta:
        model = User
        fields = ("avatar",)


class EnhancedUserSerializer(ProfileImageSerializer, UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "avatar",
        )
        read_only_fields = ("id", "is_subscribed")

    def get_is_subscribed(self, profile):
        current_user = self.context.get("request").user
        if current_user.is_anonymous:
            return False
        return current_user.subscriptions.filter(author=profile).exists()


class ComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientModel
        fields = ("id", "name", "measurement_unit")


class RecipeComponentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="ingredient.id")
    name = serializers.CharField(source="ingredient.name", read_only=True)
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit", read_only=True
    )
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = ComponentRecipe
        fields = ("id", "name", "measurement_unit", "amount")


class DishSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    ingredients = RecipeComponentSerializer(many=True, source="ingredient_recipes")
    author = EnhancedUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Dish
        fields = (
            "id",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        read_only_fields = ("is_favorited", "is_in_shopping_cart")

    def validate_image(self, image):
        if not image:
            raise serializers.ValidationError("Image is required.")
        return image

    def validate(self, attrs):
        ingredients = attrs.get("ingredient_recipes", [])
        if not ingredients:
            raise serializers.ValidationError("At least one ingredient is required.")
        return super().validate(attrs)

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError("Specify at least one ingredient.")
        ingredient_ids = [ing["ingredient"]["id"] for ing in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError("Ingredients must be unique.")
        existing_ids = set(IngredientModel.objects.values_list("id", flat=True))
        missing_ids = set(ingredient_ids) - existing_ids
        if missing_ids:
            raise serializers.ValidationError(
                f"Ingredients with IDs {', '.join(map(str, missing_ids))} not found."
            )
        return ingredients

    def _check_relation(self, dish, relation_type):
        current_user = self.context.get("request").user
        if current_user.is_anonymous:
            return False
        return getattr(current_user, relation_type).filter(recipe=dish).exists()

    def get_is_favorited(self, dish):
        return self._check_relation(dish, "favorites")

    def get_is_in_shopping_cart(self, dish):
        return self._check_relation(dish, "shopping_cart")

    def _store_ingredients(self, dish, ingredient_data):
        ComponentRecipe.objects.bulk_create(
            [
                ComponentRecipe(
                    recipe=dish,
                    ingredient_id=item["ingredient"]["id"],
                    amount=item["amount"],
                )
                for item in ingredient_data
            ]
        )

    @transaction.atomic
    def create(self, validated_data):
        ingredient_data = validated_data.pop("ingredient_recipes", None)
        dish = Dish.objects.create(
            author=self.context["request"].user, **validated_data
        )
        self._store_ingredients(dish, ingredient_data)
        return dish

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredient_data = validated_data.pop("ingredient_recipes", None)
        instance.ingredients.clear()
        instance = super().update(instance, validated_data)
        self._store_ingredients(instance, ingredient_data)
        return instance


class CompactDishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = ("id", "name", "image", "cooking_time")


class BaseCartFavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("user", "recipe")
        abstract = True

    @classmethod
    def create_validator(cls, model_class, message):
        return [
            UniqueTogetherValidator(
                queryset=model_class.objects.all(),
                fields=("recipe", "user"),
                message=message,
            )
        ]

    def to_representation(self, instance):
        return CompactDishSerializer(instance.recipe, context=self.context).data


class CartSerializer(BaseCartFavoriteSerializer):
    class Meta(BaseCartFavoriteSerializer.Meta):
        model = ShoppingCart
        validators = BaseCartFavoriteSerializer.create_validator(
            ShoppingCart, "Recipe already in cart"
        )


class FavoriteDishSerializer(BaseCartFavoriteSerializer):
    class Meta(BaseCartFavoriteSerializer.Meta):
        model = FavoriteDish
        validators = BaseCartFavoriteSerializer.create_validator(
            FavoriteDish, "Recipe already favorited"
        )


class FollowSerializer(EnhancedUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(EnhancedUserSerializer.Meta):
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
            "avatar",
        )

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        request = self.context.get("request")
        limit = int(request.query_params.get("recipes_limit", len(recipes)))
        recipes = recipes[:limit]
        return CompactDishSerializer(
            recipes, many=True, context={"request": request}
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.all().count()


class SubscriptionHandlerSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ("author", "user")
        validators = [
            UniqueTogetherValidator(
                queryset=SubscriptionPlan.objects.all(),
                fields=("author", "user"),
                message="Already subscribed to this user",
            )
        ]

    def validate_author(self, author):
        if self.context["request"].user == author:
            raise serializers.ValidationError("Cannot subscribe to yourself")
        return author

    def to_representation(self, instance):
        return FollowSerializer(instance.author, context=self.context).data
