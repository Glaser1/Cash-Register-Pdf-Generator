from django.contrib import admin

from pdf_generator.models import Item


class ItemAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "price")
    list_editable = ("title", "price")
    search_fields = ("title",)
    empty_value_display = '-пусто-'


admin.site.register(Item, ItemAdmin)
