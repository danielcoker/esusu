from rest_framework import routers

from authentication.views import AuthViewSet
from groups.views import CycleViewSet, GroupViewSet, MembershipViewSet
from transactions.views import BankViewset, CardViewSet

router = routers.DefaultRouter(trailing_slash=False)

# Auth Routes
router.register(r'users/auth', AuthViewSet, basename='auth')

# Group Routes
router.register(r'groups', GroupViewSet, basename='groups')
router.register(r'memberships', MembershipViewSet, basename='memberships')
router.register(r'cycles', CycleViewSet, basename='cycles')

# Transaction Routes
router.register(r'banks', BankViewset, basename='banks')
router.register(r'cards', CardViewSet, basename='cards')
