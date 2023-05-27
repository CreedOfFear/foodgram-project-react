from django.contrib import admin
from recipes.models import Ingredient, Recipe, Tag
from users.models import UserFoodgram

admin.site.register(Tag)
admin.site.register(Recipe)
admin.site.register(UserFoodgram)
admin.site.register(Ingredient)
