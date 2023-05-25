from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets, exceptions
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.filters import IngredientFilter, RecipeFilter
from api.serializers import (
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeGetSerializer,
    TagSerialiser,
    UserSubscribeRepresentSerializer,
    UserSubscribeSerializer,
    RecipeSmallSerializer
    )
from api.utils import get_list_ingredients
from recipes.models import (
    Favourite,
    Ingredient,
    Recipe,
    ShoppingCart,
    Tag
    )
from users.models import Subscription, UserFoodgram

from .permission import IsAdminAuthorOrReadOnly


class UserSubscribeView(APIView):
    """Создание/удаление подписки на пользователя."""
    def post(self, request, user_id):
        author = get_object_or_404(UserFoodgram, id=user_id)
        serializer = UserSubscribeSerializer(
            data={"user": request.user.id, "author": author.id},
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        author = get_object_or_404(UserFoodgram, id=user_id)
        if not Subscription.objects.filter(
            user=request.user,
            author=author
        ).exists():
            return Response(
                {"errors": "Вы не подписаны на этого пользователя"},
                status=status.HTTP_400_BAD_REQUEST
            )
        Subscription.objects.get(
            user=request.user.id,
            author=user_id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserSubscriptionsViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """Получение списка всех подписок на пользователей."""
    serializer_class = UserSubscribeRepresentSerializer

    def get_queryset(self):
        return UserFoodgram.objects.filter(following__user=self.request.user)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение информации о тегах."""
    queryset = Tag.objects.all()
    serializer_class = TagSerialiser
    permission_classes = (AllowAny, )
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение информации об ингредиентах."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Работа с рецептами. Создание/изменение/удаление рецепта.
    Получение информации о рецептах.
    Добавление рецептов в избранное и список покупок.
    Отправка файла со списком рецептов.
    """
    queryset = Recipe.objects.all()
    permission_classes = (IsAdminAuthorOrReadOnly, )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ["get", "post", "patch", "delete"]

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return RecipeGetSerializer
        return RecipeCreateSerializer

    @action(
        methods=["POST", "DELETE"],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        """Работа с избранными рецептами.
        Удаление/добавление в избранное.
        """
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if self.request.method == "POST":
            self.add_to_favorites(user, recipe)
        elif self.request.method == "DELETE":
            self.remove_from_favorites(user, recipe)
        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        serializer = RecipeSmallSerializer(
            recipe,
            context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def add_to_favorites(self, user, recipe):
        """Создание инстанса"""
        if Favourite.objects.filter(user=user, recipe=recipe).exists():
            raise exceptions.ValidationError("Рецепт уже в избранном.")
        Favourite.objects.create(user=user, recipe=recipe)

    def remove_from_favorites(self, user, recipe):
        """Удаление инстанса"""
        if not Favourite.objects.filter(user=user, recipe=recipe).exists():
            raise exceptions.ValidationError(
                "Рецепта нет в избранном, либо он уже удален."
            )
        favorite = get_object_or_404(Favourite, user=user, recipe=recipe)
        favorite.delete()

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated, ]
    )
    def shopping_cart(self, request, pk=None):
        """Работа со списком покупок.
        Удаление/Добавление в список покупок.
        """
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if self.request.method == "POST":
            self.create_shopping_cart(user, recipe)
            serializer = RecipeSmallSerializer(
                recipe,
                context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif self.request.method == "DELETE":
            self.delete_shopping_cart(user, recipe)
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def create_shopping_cart(self, user, recipe):
        """Создание инстанса"""
        if ShoppingCart.objects.filter(
            user=user,
            recipe=recipe
        ).exists():
            raise exceptions.ValidationError(
                "Рецепт уже в списке покупок."
            )

        ShoppingCart.objects.create(user=user, recipe=recipe)

    def delete_shopping_cart(self, user, recipe):
        """Удаление инстанса"""
        if not ShoppingCart.objects.filter(
            user=user,
            recipe=recipe
        ).exists():
            raise exceptions.ValidationError(
                "Рецепта нет в списке покупок, либо он уже удален."
            )

        shopping_cart = get_object_or_404(
            ShoppingCart,
            user=user,
            recipe=recipe
        )
        shopping_cart.delete()

    @action(
        detail=False,
    )
    def download_shopping_cart(self, request):
        """Отправка файла со списком покупок."""
        text = get_list_ingredients(request.user)

        response = HttpResponse(text, content_type="text/plain")
        response["Content-Disposition"] = (
            'attachment;filename="shopping_cart.txt"'
            )
        return response
