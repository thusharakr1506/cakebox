from rest_framework import serializers
from django.contrib.auth.models import User
from creamy.models import Cake,Weight,Category,Type,Basket,BasketItem,Order


class UserSerializer(serializers.ModelSerializer):

    password1=serializers.CharField(write_only=True)
    password2=serializers.CharField(write_only=True)

    class Meta:

        model=User
        fields=["username","email","password1","password2","password"]
        read_only_fields=["id","password"]

    def create(self, validated_data):

        password1=validated_data.pop("password1")
        password2=validated_data.pop("password2")

        if password1!=password2:
            raise serializers.ValidationError("password mismatch")
        return User.objects.create_user(**validated_data,password="password2")


class CategorySerializer(serializers.ModelSerializer):

    class Meta:

        model=Category  
        fields=["id","name"]


class TypeSerializer(serializers.ModelSerializer):

    class Meta:

        model=Type
        fields=["id","name"]


class WeightSerializer(serializers.ModelSerializer):

    class Meta:

        model=Weight
        fields=["id","name"]


class CakeSerializer(serializers.ModelSerializer):

    category_object=CategorySerializer(read_only=True)
    
    type_object=TypeSerializer(read_only=True)

    weight_object=WeightSerializer(read_only=True,many=True)

    class Meta:

        model=Cake
        fields="__all__"


class CartCakeSerializer(serializers.ModelSerializer):

    class Meta:

        model=Cake
        fields=["id","title","price","image"]
        

class BasketItemSerializer(serializers.ModelSerializer):

    item_total=serializers.CharField(read_only=True)
    cake_object=CartCakeSerializer(read_only=True)
    weight_object=serializers.StringRelatedField()

    class Meta:

        model=BasketItem
        fields=[
            "id",
            "cake_object",
            "weight_object",
            "qty",
            "item_total",
            "created_date",
        ]


class BasketSerializer(serializers.ModelSerializer):

    cart_items=BasketItemSerializer(many=True)
    basket_total=serializers.CharField()
    owner=serializers.StringRelatedField()

    class Meta:

        model=Basket
        fields=[
            "id",
            "owner",
            "cart_items",
            "basket_total"
        ]



class OrderSerializer(serializers.ModelSerializer):

    get_order_total=serializers.CharField(read_only=True)
    basket_item_objects=BasketItemSerializer(many=True,read_only=True)

    class Meta:

        model=Order
        fields="__all__"