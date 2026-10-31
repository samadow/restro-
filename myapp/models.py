from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
from decimal import Decimal

# =========================
# 1. ACCOUNTS
# =========================

ROLE_CHOICES = [
    ("customer", "customer"),
    ("owner", "owner"),
    ("manager", "manager"),
    ("waiter", "waiter"),
    ("chef", "chef"),
    ("cashier", "cashier"),
    ("delivery", "delivery"),
]

BRON_STATUS = [
    ("pending", "pending"),
    ("confirmed", "confirmed"),
    ("cancelled", "cancelled"),
    ("completed", "completed"),
    ("no_show", "no_show"),
]

ORDER_STATUS = [
    ("new", "new"),
    ("confirmed", "confirmed"),
    ("preparing", "preparing"),
    ("ready", "ready"),
    ("served", "served"),
    ("completed", "completed"),
    ("cancelled", "cancelled"),
]

PAYMENT_METHOD = [
    ("cash", "cash"),
    ("card", "card"),
    ("online", "online"),
]

STAFF_POSITION = [
    ("owner", "owner"),
    ("manager", "manager"),
    ("waiter", "waiter"),
    ("chef", "chef"),
    ("cashier", "cashier"),
    ("delivery", "delivery"),
]

STOL_STATUS = [
    ("free", "free"),
    ("busy", "busy"),
    ("reserved", "reserved"),
]

KITCHEN_STATUS = [
    ("pending", "pending"),
    ("preparing", "preparing"),
    ("ready", "ready"),
]

DELIVERY_STATUS = [
    ("pending", "pending"),
    ("assigned", "assigned"),
    ("picked_up", "picked_up"),
    ("delivered", "delivered"),
    ("cancelled", "cancelled"),
]

SHIFT_STATUS = [
    ("active", "active"),
    ("finished", "finished"),
]

ATTENDANCE_STATUS = [
    ("present", "present"),
    ("late", "late"),
    ("absent", "absent"),
    ("leave", "leave"),
]

MOVEMENT_TYPE = [
    ("in", "in"),
    ("out", "out"),
    ("order", "order"),
]

DISCOUNT_TYPE = [
    ("percent", "percent"),
    ("fixed", "fixed"),
]

LOYALTY_TYPE = [
    ("earn", "earn"),
    ("redeem", "redeem"),
    ("return", "return"),
]

# 1 point for every 10 TJS, 1 point = 0.50 TJS discount
POINTS_PER_AMOUNT = 10
POINT_PRICE = Decimal("0.50")

SUBSCRIPTION_STATUS = [
    ("active", "active"),
    ("expired", "expired"),
    ("cancelled", "cancelled"),
]

PAYMENT_STATUS = [
    ("pending", "pending"),
    ("paid", "paid"),
    ("failed", "failed"),
    ("partially_refunded", "partially_refunded"),
    ("refunded", "refunded"),
]


class Custumer(AbstractUser):
    fullname = models.CharField(max_length=100)
    phon_number = models.CharField(max_length=20)
    img = models.ImageField(upload_to="users/", null=True, blank=True)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default="customer")
    cr_at = models.DateTimeField(auto_now_add=True)
    
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    fullname = models.CharField(max_length=100)
    phon_number = models.CharField(max_length=20)
    img = models.ImageField(upload_to="users/", null=True, blank=True)
    role = models.CharField(max_length=30, default="customer")
    cr_at = models.DateTimeField(auto_now_add=True)
    bio = models.TextField()
    



# =========================
# 2. RESTAURANT
# =========================

class Restaurant(models.Model):
    owner = models.ForeignKey(Custumer, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    img = models.ImageField(upload_to="restaurant/")
    address = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    cr_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class filial(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    img = models.ImageField(upload_to="filial/")
    phone_number = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    cr_at = models.DateTimeField(auto_now_add=True)


class RestaurantSettings(models.Model):
    restaurant = models.OneToOneField(Restaurant, on_delete=models.CASCADE)
    currency = models.CharField(max_length=10, default="TJS")
    language = models.CharField(max_length=10, default="ru")
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    delivery_enabled = models.BooleanField(default=False)
    reservation_enabled = models.BooleanField(default=True)
    cr_at = models.DateTimeField(auto_now_add=True)


# =========================
# 3. TABLES
# =========================

class Stol(models.Model):
    filial = models.ForeignKey(filial, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    capacity = models.IntegerField(default=4)
    status = models.CharField(max_length=20, choices=STOL_STATUS, default="free")
    cr_at = models.DateTimeField(auto_now_add=True)


# =========================
# 4. RESERVATION
# =========================

class dron_stol(models.Model):
    user = models.ForeignKey(Custumer, on_delete=models.CASCADE)
    filial = models.ForeignKey(filial, on_delete=models.CASCADE)
    stol = models.ForeignKey(Stol, on_delete=models.CASCADE)
    date = models.DateField()
    vakt = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    guests = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=BRON_STATUS, default="pending")
    comment = models.TextField(blank=True)
    cr_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        old = dron_stol.objects.filter(pk=self.pk).first() if self.pk else None
        super().save(*args, **kwargs)

        restaurant = self.filial.restaurant
        text = f"Table {self.stol.name}, {self.date} {self.vakt.strftime('%H:%M')}, guests: {self.guests}"

        if old is None:
            notify(self.user, "Reservation created", text, "reservation")
            notify_restaurant(restaurant, "New reservation", f"{self.user.username}: {text}", "reservation")

        elif old.status != self.status:
            notify(self.user, "Reservation status changed", f"{text} - {old.status} -> {self.status}", "reservation")

            if self.status == "cancelled":
                notify_restaurant(restaurant, "Reservation cancelled", f"{self.user.username}: {text}", "reservation")


# =========================
# 5. MENU
# =========================

class Category(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    img = models.ImageField(upload_to="category/")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    cr_at = models.DateTimeField(auto_now_add=True)


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    decription = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    img = models.ImageField(upload_to="product/")
    is_available = models.BooleanField(default=True)
    preparation_time = models.IntegerField(default=15)
    cr_at = models.DateTimeField(auto_now_add=True)


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)


class ProductExtra(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)


# =========================
# 6. ORDERS
# =========================

class Order(models.Model):
    user = models.ForeignKey(Custumer, on_delete=models.CASCADE)
    filial = models.ForeignKey(filial, on_delete=models.CASCADE)
    stol = models.ForeignKey(
        Stol,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    reservation = models.ForeignKey(
        dron_stol,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    order_number = models.CharField(max_length=50)
    order_type = models.CharField(max_length=30, default="dine_in")
    status = models.CharField(max_length=30, choices=ORDER_STATUS, default="new")
    total_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coupon = models.ForeignKey(
        "Coupon",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    points_used = models.IntegerField(default=0)
    comment = models.TextField(blank=True)
    cr_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_order_total(self):
        products = self.dron_product_set.all()

        total = 0

        for product in products:
            total += product.total_price

        delivery = Delivery.objects.filter(order=self).first()
        if delivery:
            total += delivery.delivery_price

        return total

    def calculate_discount(self):
        # discount comes only from coupon and loyalty points, never from the client
        discount = Decimal(self.points_used) * POINT_PRICE

        if self.coupon:
            discount += self.coupon.calculate_discount(self.total_price)

        return max(min(discount, self.total_price), Decimal("0"))


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        self.total_price = self.calculate_order_total()
        self.discount = self.calculate_discount()

        super().save(update_fields=["total_price", "discount"])


class dron_product(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    product_name = models.CharField(max_length=200, blank=True)
    kalichestvo = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    comment = models.TextField(blank=True)

    def calculate_total(self):
        return self.price * self.kalichestvo

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.variant.price if self.variant else self.product.price

        if not self.product_name:
            self.product_name = self.product.name
            if self.variant:
                self.product_name += f" ({self.variant.name})"

        self.total_price = self.calculate_total()
        super().save(*args, **kwargs)

        self.order.save()

    def delete(self, *args, **kwargs):
        order = self.order
        result = super().delete(*args, **kwargs)

        order.save()

        return result


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    old_status = models.CharField(max_length=30)
    new_status = models.CharField(max_length=30)
    changed_by = models.ForeignKey(
        Custumer,
        on_delete=models.SET_NULL,
        null=True
    )
    cr_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            order = self.order
            text = f"Order {order.order_number}: {self.old_status} -> {self.new_status}"

            notify(order.user, "Order status changed", text, "order_status")

            if self.new_status == "cancelled":
                notify_restaurant(order.filial.restaurant, "Order cancelled", text, "order_status")

            if self.new_status == "completed":
                loyalty_earn(order)

            if self.new_status == "cancelled" and order.points_used:
                loyalty_return(order)

            if self.new_status in ["completed", "cancelled"] and order.stol:
                order.stol.status = "free"
                order.stol.save()


# =========================
# 7. KITCHEN
# =========================

class Kitchen(models.Model):
    filial = models.ForeignKey(filial, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)


class KitchenOrder(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    kitchen = models.ForeignKey(Kitchen, on_delete=models.CASCADE)
    status = models.CharField(max_length=30, choices=KITCHEN_STATUS, default="pending")
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    cr_at = models.DateTimeField(auto_now_add=True)


class KitchenOrderItem(models.Model):
    kitchen_order = models.ForeignKey(KitchenOrder, on_delete=models.CASCADE)
    order_item = models.ForeignKey(dron_product, on_delete=models.CASCADE)
    status = models.CharField(max_length=30, choices=KITCHEN_STATUS, default="pending")
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)


# =========================
# 8. PAYMENTS
# =========================

class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    user = models.ForeignKey(Custumer, on_delete=models.CASCADE)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD)
    status = models.CharField(max_length=30, choices=PAYMENT_STATUS, default="pending")

    transaction_id = models.CharField(max_length=100, blank=True)
    cr_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Refund(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=30, default="pending")
    cr_at = models.DateTimeField(auto_now_add=True)


# =========================
# 9. INVENTORY
# =========================

class Ingredient(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=20)

    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    min_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    cr_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        old = Ingredient.objects.filter(pk=self.pk).first() if self.pk else None
        super().save(*args, **kwargs)

        was_low = old is not None and old.quantity <= old.min_quantity
        is_low = self.quantity <= self.min_quantity

        if is_low and not was_low:
            notify_restaurant(
                self.restaurant,
                "Low stock",
                f"{self.name}: {self.quantity} {self.unit} left (min {self.min_quantity} {self.unit})",
                "low_stock"
            )


class ProductIngredient(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)


class Supplier(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=200)
    cr_at = models.DateTimeField(auto_now_add=True)


class StockMovement(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    comment = models.TextField(blank=True)
    cr_at = models.DateTimeField(auto_now_add=True)


# =========================
# 10. STAFF
# =========================

class Staff(models.Model):
    user = models.ForeignKey(Custumer, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    filial = models.ForeignKey(filial, on_delete=models.CASCADE)

    position = models.CharField(max_length=50, choices=STAFF_POSITION)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    cr_at = models.DateTimeField(auto_now_add=True)


class StaffShift(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=SHIFT_STATUS, default="active")
    cr_at = models.DateTimeField(auto_now_add=True)


class StaffAttendance(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.DateField()

    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)

    status = models.CharField(max_length=30, choices=ATTENDANCE_STATUS, default="present")


# =========================
# 11. CUSTOMER
# =========================

class CustomerAddress(models.Model):
    user = models.ForeignKey(Custumer, on_delete=models.CASCADE)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)


class CustomerFavorite(models.Model):
    user = models.ForeignKey(Custumer, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    cr_at = models.DateTimeField(auto_now_add=True)


class Review(models.Model):
    user = models.ForeignKey(Custumer, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    rating = models.IntegerField()
    comment = models.TextField(blank=True)
    cr_at = models.DateTimeField(auto_now_add=True)


# =========================
# 12. NOTIFICATIONS
# =========================

NOTIFICATION_TYPE = [
    ("order", "order"),
    ("order_status", "order_status"),
    ("reservation", "reservation"),
    ("low_stock", "low_stock"),
    ("subscription", "subscription"),
]


class Notification(models.Model):
    user = models.ForeignKey(Custumer, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    message = models.TextField()
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPE)

    is_read = models.BooleanField(default=False)
    cr_at = models.DateTimeField(auto_now_add=True)


class RestaurantNotification(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    message = models.TextField()
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPE, default="order")

    is_read = models.BooleanField(default=False)
    cr_at = models.DateTimeField(auto_now_add=True)


def notify(user, title, message, notification_type):
    return Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type
    )


def notify_restaurant(restaurant, title, message, notification_type):
    return RestaurantNotification.objects.create(
        restaurant=restaurant,
        title=title,
        message=message,
        notification_type=notification_type
    )


# =========================
# 13. SUBSCRIPTION
# =========================

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField(default=30)

    max_filial = models.IntegerField(default=1)
    max_staff = models.IntegerField(default=5)

    is_active = models.BooleanField(default=True)


class RestaurantSubscription(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)

    start_date = models.DateField()
    end_date = models.DateField()

    status = models.CharField(max_length=30, choices=SUBSCRIPTION_STATUS, default="active")
    cr_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        old = RestaurantSubscription.objects.filter(pk=self.pk).first() if self.pk else None
        super().save(*args, **kwargs)

        if old is None:
            notify_restaurant(
                self.restaurant,
                "Subscription activated",
                f"Plan {self.plan.name}: {self.start_date} - {self.end_date}",
                "subscription"
            )

        elif old.status != self.status:
            notify_restaurant(
                self.restaurant,
                "Subscription status changed",
                f"Plan {self.plan.name}: {old.status} -> {self.status}",
                "subscription"
            )


class SubscriptionPayment(models.Model):
    subscription = models.ForeignKey(
        RestaurantSubscription,
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD)

    status = models.CharField(max_length=30, choices=PAYMENT_STATUS, default="pending")
    transaction_id = models.CharField(max_length=100, blank=True)

    cr_at = models.DateTimeField(auto_now_add=True)


# =========================
# 14. REPORTS
# =========================

class DailyReport(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    filial = models.ForeignKey(filial, on_delete=models.CASCADE)

    date = models.DateField()
    total_orders = models.IntegerField(default=0)

    total_sales = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    total_payments = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    cr_at = models.DateTimeField(auto_now_add=True)


class Expense(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    filial = models.ForeignKey(filial, on_delete=models.CASCADE)

    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    category = models.CharField(max_length=50)
    comment = models.TextField(blank=True)

    date = models.DateField()
    cr_at = models.DateTimeField(auto_now_add=True)


# =========================
# 15. DELIVERY
# =========================

class DeliveryStaff(models.Model):
    user = models.ForeignKey(Custumer, on_delete=models.CASCADE)
    filial = models.ForeignKey(filial, on_delete=models.CASCADE)

    vehicle = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)


class Delivery(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    delivery_staff = models.ForeignKey(
        DeliveryStaff,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    address = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20)

    delivery_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=30, choices=DELIVERY_STATUS, default="pending")

    picked_up_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    cr_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# =========================
# 16. COUPON
# =========================

class Coupon(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

    code = models.CharField(max_length=50)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE)

    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    is_active = models.BooleanField(default=True)
    cr_at = models.DateTimeField(auto_now_add=True)

    def check_valid(self, restaurant, amount):
        now = timezone.now()

        if not self.is_active:
            return "Coupon is not active"
        if now < self.start_date:
            return "Coupon is not started yet"
        if now > self.end_date:
            return "Coupon is expired"
        if self.restaurant_id != restaurant.id:
            return "Coupon is not for this restaurant"
        if amount < self.min_order_price:
            return f"Minimum order price for this coupon is {self.min_order_price}"

        return None

    def calculate_discount(self, amount):
        if self.discount_type == "percent":
            discount = amount * self.discount_value / 100
        else:
            discount = self.discount_value

        return min(round(discount, 2), amount)


# =========================
# 17. LOYALTY
# =========================

class LoyaltyAccount(models.Model):
    user = models.ForeignKey(Custumer, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

    points = models.IntegerField(default=0)
    cr_at = models.DateTimeField(auto_now_add=True)


class LoyaltyTransaction(models.Model):
    account = models.ForeignKey(LoyaltyAccount, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)

    points = models.IntegerField()
    transaction_type = models.CharField(max_length=30, choices=LOYALTY_TYPE)

    cr_at = models.DateTimeField(auto_now_add=True)


def loyalty_account(user, restaurant):
    account, created = LoyaltyAccount.objects.get_or_create(user=user, restaurant=restaurant)
    return account


def loyalty_earn(order):
    if LoyaltyTransaction.objects.filter(order=order, transaction_type="earn").exists():
        return

    points = int((order.total_price - order.discount) // POINTS_PER_AMOUNT)

    if points <= 0:
        return

    account = loyalty_account(order.user, order.filial.restaurant)
    account.points += points
    account.save()

    LoyaltyTransaction.objects.create(account=account, order=order, points=points, transaction_type="earn")
    notify(order.user, "Loyalty points", f"+{points} points for order {order.order_number}", "order")


def loyalty_return(order):
    account = loyalty_account(order.user, order.filial.restaurant)
    account.points += order.points_used
    account.save()

    LoyaltyTransaction.objects.create(account=account, order=order, points=order.points_used, transaction_type="return")

    order.points_used = 0
    order.discount = 0
    order.save()


# =========================
# 18. AUDIT LOG
# =========================

class AuditLog(models.Model):
    user = models.ForeignKey(
        Custumer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    action = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    object_id = models.IntegerField(null=True, blank=True)

    description = models.TextField(blank=True)
    cr_at = models.DateTimeField(auto_now_add=True)