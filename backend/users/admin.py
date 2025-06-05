from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import BlogerUser, SubscriptionPlan

@admin.register(BlogerUser)
class CustomUserAdmin(UserAdmin):
    search_fields = ("username", "email")
    search_help_text = "Поиск по юзернейму или емейлу"

@admin.register(SubscriptionPlan)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "author",
    )
    search_fields = ("user__username", "author__username")