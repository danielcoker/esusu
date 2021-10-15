from rest_framework import routers

from authentication.views import AuthViewSet

router = routers.DefaultRouter(trailing_slash=False)

# Auth Routes
router.register(r'users/auth', AuthViewSet, basename='auth')
