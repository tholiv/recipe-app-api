"""Serializers for Recipe APIs."""
from core.models import Recipe, Tag
from rest_framework import serializers


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for Tag.
    """

    class Meta:
        model = Tag
        fields = [
            "id",
            "name",
        ]
        read_only_fields = ["id"]


class RecipeSerializer(serializers.ModelSerializer):
    """
    Serializer for the recipe object.
    """

    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = [
            "id",
            "title",
            "time_in_minutes",
            "price",
            "link",
            "tags",
        ]
        read_only_fields = ["id"]

    def _get_or_create_tags(self, tags, recipe):
        """Handle getting or creatig tags as needed."""
        auth_user = self.context.get("request").user
        for tag in tags:
            tag_obj, _ = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            recipe.tags.add(tag_obj)

    def create(self, validated_data):
        """
        Create a recipe while also handling new or existing tags.
        """
        tags = validated_data.pop("tags", [])
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        """
        update and return a recipe while handligh new or existing tags.
        """
        tags = validated_data.pop("tags", None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """
    Serializer for the recipe details.
    """

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ["description"]
