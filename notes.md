# Notes To Self

## Steps to create a new API within the application:

1 - Tests first (test_models)
2 - Run a watch test fail
3 - Create new model in models.py
4 - Run and watch test pass
5 - Create and run migration of new model
6 - Create new app (with `startapp <api_name>`)
7 - Cleanup sub-directories
8 - Append new app to settings.INSTALLED_APPS


## Adding Tags API (high level)

1 - add tags model
    - edit test_models.py
    - run test and watch failing
    - models.py
    - make migration
    - migrate
    - rerun test and watch pass
    - register new model in admin.py

2 - add list tags api functionality
    - add test_tags_api.py
    - see test failing
    - add the TagSerializer to recipe/serializers.py
    - add TagView to recipe/views.py
    - register new TagViewSet inside recipes/urls.py

3 - add update tags api functionality
    - edit test_tags_api.py
    - run test and watch fail
    - edit the viewset in recipe/views.py (hint: mixins class param)
    - rerun tests and watch them pass

4  - implement delete functionality
    - edit test_tags_api.py
    - run test and watch fail
    - edit the viewset in recipe/views.py (hint: mixins class param)
    - rerun tests and watch them pass

5 - managing tags when creating a new recipe
    - edit test_recipe_apis.py
    - watch test fail
    - add nested serialization functionality (recipe/serializers.py)
    - watch them succeed
    - also add functionality to attach existing tags to new recipe

6 - updating tags assigned to existing recipes
    - add tests to test_recipe.api.py