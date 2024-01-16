"""
Test for the Tags API.
"""
from core.models import Tag
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from recipe.serializers import TagSerializer
from rest_framework import status
from rest_framework.test import APIClient

TAGS_URL = reverse("recipe:tag-list")


def detail_url(tag_id):
    """Create and return a tag detail URL."""
    return reverse("recipe:tag-detail", args=[tag_id])


def create_tag(user, **params):
    """Create and return a tag object."""
    defaults = {"name": "Beef,"}
    defaults.update(**params)

    tag = Tag.objects.create(user=user, **defaults)
    return tag


def create_user(email="user@example.com", password="testpass123"):
    """Create and return a new user."""
    user = get_user_model().objects.create_user(email=email, password=password)
    return user


class PublicTagsAPITest(TestCase):
    """Test unauthorized Tags API tests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test authenticate is required to call Tags API."""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITests(TestCase):
    """Test authenticated Tags API tests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving a list of tags is successful."""
        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Dessert")

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by("-name")
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tag_list_limited_to_user(self):
        """Test list of tags is limited to logged in user."""
        new_user = create_user(
            email="new_user@example.com",
            password="testpass123",
        )
        Tag.objects.create(user=self.user, name="Meat")
        Tag.objects.create(user=new_user, name="Vegan")
        Tag.objects.create(user=new_user, name="Cauliflower")

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.filter(user=self.user)
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_update_tag(self):
        """Test updating a tab object."""
        tag = Tag.objects.create(
            user=self.user,
            name="After Dinner",
        )
        payload = {
            "name": "Dessert",
        }
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(res.data.get("name"), payload.get("name"))
        self.assertEqual(tag.name, payload.get("name"))

    def test_delete_tag(self):
        """Test deleting a tag is successful."""
        tag = create_tag(user=self.user)
        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tag_exists = Tag.objects.filter(id=tag.id).exists()
        self.assertFalse(tag_exists)

    # def test_create_tag(self):
    #     """Test creating a new tag is successful."""
    #     payload = {
    #         'name': 'Beef'
    #     }
    #     res = self.client.post(TAGS_URL, payload)

    #     self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    #     tag = Tag.objects.get(id=res.data.get('id'))
    #     for key, value in payload.items():
    #         self.assertEqual(getattr(tag, key), value)
    #      self.assertEqual(tag.user, self.user)
