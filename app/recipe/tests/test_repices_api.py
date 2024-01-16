"""
Test for recipe APIs.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Recipe,
    Tag,
)

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)

RECIPES_URL = reverse('recipe:recipe-list')

def detail_url(recipe_id):
    """Create and return a recipe detail URL."""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user, **params):
    """Create and return a sample recipe."""
    defaults = {
        'title': 'Sample recipe title.',
        'time_in_minutes': 20,
        'price': Decimal('5.25'),
        'description': 'Description for the sample recipe',
        'link': 'http://example.com/recipe.pdf',
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicRecipeAPITest(TestCase):
    """Test unauthenticated Recipe API tests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test authentication is required to call API."""
        resp = self.client.get(RECIPES_URL)

        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """Test authenticated Recipe API tests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='user@example.com',
            password='testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes."""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        resp = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated users."""
        other_user = create_user(
            email='other@example.com',
            password='testpass123',
        )
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        resp = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, serializer.data)

    def test_get_recipe_details(self):
        """Test retrieving details of a recipe object."""
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe_id=recipe.id)

        resp = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(resp.data, serializer.data)

    def test_create_recipe(self):
        """Test creating a new recipe is successful."""

        payload = {
            'title': 'Sample recipe title.',
            'time_in_minutes': 20,
            'price': Decimal('5.25'),
            'description': 'Description for the sample recipe',
            'link': 'http://example.com/recipe.pdf',
        }
        resp = self.client.post(RECIPES_URL, payload)

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=resp.data.get('id'))
        for key, value in payload.items():
            self.assertEqual(getattr(recipe, key), value)
        self.assertEqual(recipe.user, self.user)

    def test_partial_update_recipe(self):
        """Test partial update of a recipe."""
        original_link = 'https://example.com/recipe.pdf'
        recipe = create_recipe(
            user=self.user,
            title='Sample recipe title.',
            link=original_link,
        )

        payload = {
            'title': 'New recipe title',
        }
        url =  detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload.get('title'))
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update_recipe(self):
        """Test full update of a recipe."""
        recipe = create_recipe(
            user=self.user,
            title='Sample test recipe',
            link='http://example.com/recipe.pdf',
            description='Sampe recipe description.',
        )
        payload = {
            'title': 'New recipe title',
            'link': 'http:/example.com/new-recipe.pdf',
            'description': 'New recipe description.',
            'time_in_minutes': 10,
            'price': Decimal('2.50'),
        }
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()
        for key, value in payload.items():
            self.assertEqual(getattr(recipe, key), value)
        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the user results in an error."""
        new_user = create_user(
            email='user2@example.com',
            password='testpass123',
        )
        recipe = create_recipe(user=self.user)
        payload = {'user': new_user.id}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)
        recipe.refresh_from_db()

        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test a recipe can be deleted successfully."""
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_delete_recipe_another_user_error(self):
        """Test deleting recipe from another user returns error."""
        another_user = create_user(
            email='another.user@example.com',
            password='testpass123'
        )
        recipe = create_recipe(user=another_user)
        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_create_recipe_with_new_tags(self):
        """Test create new recipe with new tags."""
        payload = {
            'title': 'Sample recipe title.',
            'time_in_minutes': 20,
            'price': Decimal('5.25'),
            'description': 'Description for the sample recipe',
            'link': 'http://example.com/recipe.pdf',
            'tags': [
                {'name': 'beef'},
                {'name': 'pasta'},
            ],
        }
        res = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEquals(recipes.count(), 1)

        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)

        for tag in payload.get('tags'):
            exists = recipe.tags.filter(
                name=tag.get('name'),
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_tags_with_existing_tags(self):
        """Test creating new recipe with existing tags."""
        existing_tag = Tag.objects.create(user=self.user, name='Indian')
        payload = {
            'title': 'Sample recipe title.',
            'time_in_minutes': 20,
            'price': Decimal('5.25'),
            'description': 'Description for the sample recipe',
            'link': 'http://example.com/recipe.pdf',
            'tags': [
                {'name': 'Indian'},
                {'name': 'Dinner'},
            ],
        }
        res = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEquals(recipes.count(), 1)

        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(existing_tag, recipe.tags.all())
        for tag in payload.get('tags'):
            exists = recipe.tags.filter(
                name=tag.get('name'),
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update_recipe(self):
        """Test creating a tag when updating a recipe."""
        recipe = create_recipe(user=self.user)
        payload = {
            'tags': [
                {'name': 'lunch'}
            ]
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='lunch')
        self.assertIn(new_tag, recipe.tags.all())

    def test_assign_tag_on_update_recipe(self):
        """Test successfully assigning a tag on updating a recipe."""
        tag_breakfast = Tag.objects.create(
            user=self.user,
            name='breakfast',
        )
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        tag_lunch = Tag.objects.create(
            user=self.user,
            name='lunch',
        )
        payload = {
            'tags': [
                {'name': 'lunch'}
            ]
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())

    def test_clear_recipe_tags(self):
        """Test clearing the tags of a recipe."""
        tag_breakfast = Tag.objects.create(
            user=self.user,
            name='breakfast',
        )
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        payload = {'tags': []}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

