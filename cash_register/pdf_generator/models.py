from django.core.validators import MinValueValidator
from django.db import models


class Item(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="Описание товара",
        help_text="Введите описание товара",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена товара",
        help_text="Введите цену товара",
        validators=(MinValueValidator(0.01, "Минимальная цена товара: 0.01"),),
    )

    class Meta:
        ordering = ("-id",)
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.title
