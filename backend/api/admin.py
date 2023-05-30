from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.urls import reverse
from django.utils.html import format_html
from recipes.models import Ingredient, Recipe, Tag
from users.models import UserFoodgram

admin.site.register(Tag)
admin.site.register(Recipe)
admin.site.register(Ingredient)


@admin.register(UserFoodgram)
class CustomUserAdmin(UserAdmin):
    readonly_fields = ("last_login",)

    def change_password(self, obj):
        return format_html(
            '<a class="button" href="{}">Change password</a>',
            reverse('admin:auth_user_password_change', args=[obj.pk])
        )
    change_password.short_description = 'Change password'
