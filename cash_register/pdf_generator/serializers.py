from rest_framework import serializers

from .models import Item


class Itemserializer(serializers.Serializer):
    class Meta:
        model = Item
        fields = ["id", "title", "price"]
