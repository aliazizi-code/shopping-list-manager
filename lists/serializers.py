from rest_framework import serializers

from lists.models import ShoppingList, Item


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('name', 'price', 'quantity', 'total_price', 'is_purchased')
        read_only_fields = ('total_price',)


class ListSerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True, read_only=True)

    class Meta:
        model = ShoppingList
        fields = (
            'name', 'description', 'total_price', 'total_price_purchased', 'total_price_pending', 'total_items',
            'purchased_items', 'pending_items', 'items'
        )

        read_only_fields = (
            'total_items', 'total_price', 'purchased_items', 'pending_items', 'total_price_purchased',
            'total_price_pending', 'items'
        )
