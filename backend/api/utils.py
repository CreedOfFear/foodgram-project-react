from django.shortcuts import get_object_or_404
from django.db.models import F, Sum

from recipes.models import Ingredient, RecipeIngredient


def get_list_ingredients(user):
    """
    Cуммирование позиций из разных рецептов.
    """

    ingredients = RecipeIngredient.objects.filter(
        recipe__carts__user=user).values(
        name=F("ingredient__name"),
        measurement_unit=F("ingredient__measurent_unit")
    ).annotate(amount=Sum("amount")).values_list(
        "ingredient__name",
        "amount",
        "ingredient__measurent_unit"
    )
    return ingredients


def create_ingredients(ingredients, recipe):
    """Вспомогательная функция для добавления ингредиентов.
    Используется при создании/редактировании рецепта."""
    ingredient_list = []
    for ingredient in ingredients:
        current_ingredient = get_object_or_404(
            Ingredient,
            id=ingredient.get("id")
        )
        amount = ingredient.get("amount")
        ingredient_list.append(
            RecipeIngredient(
                recipe=recipe,
                ingredient=current_ingredient,
                amount=amount
            )
        )
    RecipeIngredient.objects.bulk_create(ingredient_list)
