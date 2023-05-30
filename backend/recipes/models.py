from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

UserFoodgram = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = "Ингридиент"
        verbose_name_plural = "Ингридиенты"

    def __str__(self):
        return (
            f'Название ингредиента : {self.name}, '
            f'Единица измерения: {self.measurement_unit}'
        )


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Тэг",
        help_text="Введите название тэга"
    )
    color = models.CharField(
        max_length=7,
        default="#ffffff",
        verbose_name="Цвет",
        help_text="Укажите цвет тега в HEX коде,например:#2200fe ",
        validators=[
            RegexValidator(
                regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Введенное значение не является цветом в формате HEX!'
            )
        ]
    )
    slug = models.SlugField(
        verbose_name="Слаг",
        unique=True,
        help_text="Укажите уникальный слаг для тэга"
    )

    class Meta:
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        UserFoodgram,
        verbose_name="Автор рецепта",
        related_name='recipes',
        on_delete=models.CASCADE

    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        through_fields=('recipe', 'ingredient'),
        verbose_name="Ингредиенты",
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Список id тегов",
        related_name="tags",
    )
    image = models.ImageField(
        upload_to="api/images",
        verbose_name="Картинка,закодированная в Base64",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Название",
    )
    text = models.TextField(
        verbose_name="Описание"
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления (в минутах)"
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="recipeingredients",

    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ингредиент",
        related_name="recipeingredients",
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name="Количество",
        validators=[
            MinValueValidator(
                1, "Количество ингредиентов не может быть меньше 1"
            )
        ]
    )

    class Meta:
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецепте"
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_combination'
            )
        ]

    def __str__(self):
        return (f'{self.recipe.name}: '
                f'{self.ingredient.name} - '
                f'{self.amount} '
                f'{self.ingredient.measurement_unit}')


class Favourite(models.Model):
    user = models.ForeignKey(
        UserFoodgram,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Рецепт",
    )

    class Meta:
        ordering = ["-id"]
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"

    def __str__(self):
        return f"{self.user.username} добавил {self.recipe.name} в избраннное"


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        UserFoodgram,
        on_delete=models.CASCADE,
        related_name="carts",
        verbose_name="Пользователь"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="carts",
        verbose_name="Рецепт"
    )

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"

    def __str__(self):
        return (
            f"{self.user.username} добавил"
            f"{self.recipe.name} в список покупок"
        )
