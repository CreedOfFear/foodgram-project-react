from django.shortcuts import get_object_or_404
from django.db.models import F, Sum
from rest_framework import status
from rest_framework.response import Response

from recipes.models import Ingredient, RecipeIngredient


def get_list_ingredients(user):
    """
    Cуммирование позиций из разных рецептов.
    """

    ingredients = RecipeIngredient.objects.filter(
        recipe__carts__user=user).values(
        name=F('ingredient__name'),
        measurement_unit=F('ingredient__measurent_unit')
    ).annotate(amount=Sum('amount')).values_list(
        'ingredient__name', 'amount', 'ingredient__measurent_unit')
    return ingredients


def create_ingredients(ingredients, recipe):
    """Вспомогательная функция для добавления ингредиентов.
    Используется при создании/редактировании рецепта."""
    ingredient_list = []
    for ingredient in ingredients:
        current_ingredient = get_object_or_404(
            Ingredient,
            id=ingredient.get('id')
        )
        amount = ingredient.get('amount')
        ingredient_list.append(
            RecipeIngredient(
                recipe=recipe,
                ingredient=current_ingredient,
                amount=amount
            )
        )
    RecipeIngredient.objects.bulk_create(ingredient_list)


def create_model_instance(request, instance, serializer_name):
    """Вспомогательная функция для добавления
    рецепта в избранное либо список покупок.
    """
    serializer = serializer_name(
        data={'user': request.user.id, 'recipe': instance.id, },
        context={'request': request}
    )
    return save_model_instance(serializer)


def save_model_instance(serializer):
    """Выдата ответа 201"""
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def delete_model_instance(request, model_name, instance, error_message):
    """Вспомогательная функция для удаления рецепта
    из избранного либо из списка покупок.
    """
    if not model_name.objects.filter(
        user=request.user,
        recipe=instance).exists(
            ):
        return bad_request_response(error_message)
    delete_instance(model_name, request.user, instance)
    return no_content_response()


def bad_request_response(error_message):
    """Выдача ответа 400"""
    return Response(
        {'errors': error_message},
        status=status.HTTP_400_BAD_REQUEST
        )


def no_content_response():
    """Выдача ответа 204"""
    return Response(status=status.HTTP_204_NO_CONTENT)


def delete_instance(model_name, user, instance):
    """Удаление инстанса"""
    model_name.objects.filter(user=user, recipe=instance).delete()
