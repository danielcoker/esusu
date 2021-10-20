from rest_framework import routers

from authentication.views import AuthViewSet
from groups.views import GroupViewSet, MembershipViewSet

router = routers.DefaultRouter(trailing_slash=False)

# Auth Routes
router.register(r'users/auth', AuthViewSet, basename='auth')

# Group Routes
router.register(r'groups', GroupViewSet, basename='groups')
router.register(r'memberships', MembershipViewSet, basename='memberships')
