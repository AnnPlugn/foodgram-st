from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404, redirect
from django.http import FileResponse
from djoser.views import UserViewSet
from ingredients.models import IngredientModel
from recipes.models import Dish, FavoriteDish, ShoppingCart, ShortUrl
from users.models import SubscriptionPlan, BlogerUser
from core.permissons import IsAuthorOrReadOnlyPermisson
from api.filters import ComponentFilter, DishFilter
from api.serializers import (
    ComponentSerializer,
    DishSerializer,
    CartSerializer,
    FavoriteDishSerializer,
    EnhancedUserSerializer,
    SubscriptionHandlerSerializer,
    FollowSerializer,
    ProfileImageSerializer,
)
from api.services import DishManager
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


class ComponentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = IngredientModel.objects.all()
    serializer_class = ComponentSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ComponentFilter
    permission_classes = (AllowAny,)
    pagination_class = None


class DishViewSet(viewsets.ModelViewSet):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer
    permission_classes = (IsAuthorOrReadOnlyPermisson,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("author",)
    filterset_class = DishFilter

    @action(methods=("GET",), detail=True, url_path="get-link", url_name="get-link")
    def fetch_short_link(self, request, pk=None):
        origin_url = f"/recipes/{pk}/"
        short_url_obj, _ = ShortUrl.objects.get_or_create(origin_url=origin_url)
        return Response(
            {"short-link": request.build_absolute_uri(short_url_obj.short_url)}
        )

    @action(
        methods=("POST",),
        detail=True,
        permission_classes=(IsAuthenticated,),
        url_path="shopping_cart",
    )
    def add_to_cart(self, request, pk):
        return DishManager.add_link(request, pk, CartSerializer)

    @add_to_cart.mapping.delete
    def remove_from_cart(self, request, pk):
        return DishManager.remove_link(request, pk, ShoppingCart)

    @action(
        methods=("POST",),
        detail=True,
        permission_classes=(IsAuthenticated,),
        url_path="favorite",
    )
    def add_favorite(self, request, pk):
        return DishManager.add_link(request, pk, FavoriteDishSerializer)

    @add_favorite.mapping.delete
    def remove_favorite(self, request, pk):
        return DishManager.remove_link(request, pk, FavoriteDish)

    @action(
        methods=("GET",),
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path="download_shopping_cart",
    )
    def download_cart(self, request):
        return FileResponse(
            DishManager.generate_pdf(request),
            as_attachment=True,
            filename=f"{settings.NAME_SHOPPING_CART_LIST_FILE}.pdf",
        )


class ProfileViewSet(UserViewSet):
    @action(
        methods=("PUT",),
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path="me/avatar",
    )
    def update_image(self, request):
        data = request.data
        if "avatar" not in data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = ProfileImageSerializer(request.user, data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(serializer.data)

    @update_image.mapping.delete
    def delete_image(self, request):
        serializer = ProfileImageSerializer(request.user, data={"avatar": None})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=("GET",),
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path="subscriptions",
    )
    def get_follows(self, request):
        authors = User.objects.filter(subscribers__user=request.user)
        page = self.paginate_queryset(authors)
        serializer = FollowSerializer(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)

    @action(
        methods=("POST",),
        detail=True,
        permission_classes=(IsAuthenticated,),
        url_path="subscribe",
    )
    def follow(self, request, id):
        get_object_or_404(User, pk=id)
        serializer = SubscriptionHandlerSerializer(
            data={"author": id, "user": request.user.id},
            context={"request": request},
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @follow.mapping.delete
    def unfollow(self, request, id):
        deleted, _ = SubscriptionPlan.objects.filter(
            author=self.get_object(), user=request.user
        ).delete()
        if not deleted:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShortLinkRedirectView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, token):
        short_url = f"/s/{token}/"
        obj = get_object_or_404(ShortUrl, short_url=short_url)
        return redirect(obj.origin_url)
