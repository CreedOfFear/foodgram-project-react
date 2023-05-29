from django.contrib.auth.models import AbstractUser
from django.db import models


class UserFoodgram(AbstractUser):
    email = models.EmailField(max_length=254, blank=False)


class Subscription(models.Model):
    user = models.ForeignKey(
        UserFoodgram,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь',
    )
    author = models.ForeignKey(
        UserFoodgram,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'
