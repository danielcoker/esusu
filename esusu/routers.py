from rest_framework import routers

from authentication.views import AuthViewSet
from groups.views import GroupViewSet

router = routers.DefaultRouter(trailing_slash=False)

# Auth Routes
router.register(r'users/auth', AuthViewSet, basename='auth')

# Group Routes
router.register(r'groups', GroupViewSet, basename='groups')
