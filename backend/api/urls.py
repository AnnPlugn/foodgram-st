from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views import ComponentViewSet, DishViewSet, ProfileViewSet, ShortLinkRedirectView

app_name = "api"

router_v1 = DefaultRouter()
router_v1.register("ingredients", ComponentViewSet, basename="ingredients")
router_v1.register("recipes", DishViewSet, basename="recipes")
router_v1.register("users", ProfileViewSet, basename="users")

urlpatterns = [
    path("", include(router_v1.urls)),
    path("s/<str:token>/", ShortLinkRedirectView.as_view(), name="short-url-redirect"),
    path("auth/", include("djoser.urls.authtoken")),
    path("", include("djoser.urls")),
]