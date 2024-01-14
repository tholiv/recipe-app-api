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
