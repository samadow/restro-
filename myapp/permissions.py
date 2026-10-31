from django.db.models import Q
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.exceptions import PermissionDenied


def is_admin(user):
    return user.is_authenticated and user.is_superuser


def has_role(user, roles):
    return is_admin(user) or getattr(user, "role", None) in roles


class IsOwner(BasePermission):

    def has_permission(self, request, view):
        return has_role(request.user, ["owner"])


class IsManager(BasePermission):

    def has_permission(self, request, view):
        return has_role(request.user, ["owner", "manager"])

class IsChef(BasePermission):

    def has_permission(self, request, view):
        return has_role(request.user, ["owner", "manager", "chef"])


class IsCashier(BasePermission):

    def has_permission(self, request, view):
        return has_role(request.user, ["owner", "manager", "cashier"])


class IsWaiter(BasePermission):

    def has_permission(self, request, view):
        return has_role(request.user, ["owner", "manager", "waiter", "cashier"])


class IsDelivery(BasePermission):

    def has_permission(self, request, view):
        return has_role(request.user, ["owner", "manager", "delivery"])


class IsSuperAdmin(BasePermission):

    def has_permission(self, request, view):
        return is_admin(request.user)


# object level: what restaurant / filial / order this user can see

def my_restaurants(user):
    from .models import Restaurant

    if is_admin(user):
        return Restaurant.objects.all()

    return Restaurant.objects.filter(
        Q(owner=user) | Q(staff__user=user, staff__is_active=True)
    ).distinct()


def my_owned_restaurants(user):
    from .models import Restaurant

    if is_admin(user):
        return Restaurant.objects.all()

    return Restaurant.objects.filter(owner=user)


def my_filials(user):
    from .models import filial

    if is_admin(user):
        return filial.objects.all()

    return filial.objects.filter(
        Q(restaurant__owner=user) | Q(staff__user=user, staff__is_active=True)
    ).distinct()


def my_orders(user):
    from .models import Order

    if is_admin(user):
        return Order.objects.all()

    return Order.objects.filter(
        Q(user=user) | Q(filial__in=my_filials(user))
    ).distinct()


def check_restaurant(user, restaurant, owner_only=False):
    restaurants = my_owned_restaurants(user) if owner_only else my_restaurants(user)

    if not restaurants.filter(pk=restaurant.pk).exists():
        raise PermissionDenied("You have no access to this restaurant")


def check_filial(user, item):
    if not my_filials(user).filter(pk=item.pk).exists():
        raise PermissionDenied("You have no access to this filial")


def is_read(request):
    return request.method in SAFE_METHODS
