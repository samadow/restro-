import io
import tempfile
from datetime import date, timedelta
from decimal import Decimal

from django.test import override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework.test import APITestCase

from .models import *
from . import ai
from unittest.mock import patch


def image():
    file = io.BytesIO()
    Image.new("RGB", (5, 5)).save(file, "PNG")
    return SimpleUploadedFile("test.png", file.getvalue(), content_type="image/png")


@override_settings(
    MEDIA_ROOT=tempfile.mkdtemp(),
    PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"],
)
class RestoraTestCase(APITestCase):

    def setUp(self):
        self.owner = Custumer.objects.create_user(username="owner", password="Pass12345!", role="owner")
        self.chef = Custumer.objects.create_user(username="chef", password="Pass12345!", role="chef")
        self.cashier = Custumer.objects.create_user(username="cashier", password="Pass12345!", role="cashier")
        self.waiter = Custumer.objects.create_user(username="waiter", password="Pass12345!", role="waiter")
        self.customer = Custumer.objects.create_user(username="customer", password="Pass12345!")
        self.other_owner = Custumer.objects.create_user(username="other", password="Pass12345!", role="owner")

        self.restaurant = Restaurant.objects.create(owner=self.owner, name="Rest", description="d", img="r.png", address="a", phone_number="1")
        self.filial = filial.objects.create(restaurant=self.restaurant, name="F1", address="a", img="f.png", phone_number="1")
        self.stol = Stol.objects.create(filial=self.filial, name="1", description="window", capacity=4)
        self.kitchen = Kitchen.objects.create(filial=self.filial, name="Main")

        for user, position in [(self.chef, "chef"), (self.cashier, "cashier"), (self.waiter, "waiter")]:
            Staff.objects.create(user=user, restaurant=self.restaurant, filial=self.filial, position=position, salary=100)

        self.category = Category.objects.create(restaurant=self.restaurant, name="Hot", img="c.png")
        self.product = Product.objects.create(category=self.category, name="Plov", decription="d", price=Decimal("30"), img="p.png")
        self.variant = ProductVariant.objects.create(product=self.product, name="big", price=Decimal("40"))

        self.plan = SubscriptionPlan.objects.create(name="Start", description="d", price=100, max_filial=2, max_staff=5)
        RestaurantSubscription.objects.create(restaurant=self.restaurant, plan=self.plan, start_date=date.today(), end_date=date.today() + timedelta(days=30))

        self.other_restaurant = Restaurant.objects.create(owner=self.other_owner, name="Other", description="d", img="r.png", address="a", phone_number="1")
        self.other_filial = filial.objects.create(restaurant=self.other_restaurant, name="OF", address="a", img="f.png", phone_number="1")

    def login(self, user):
        self.client.force_authenticate(user)

    def make_order(self, user=None, items=((1, None),)):
        order = Order.objects.create(user=user or self.customer, filial=self.filial, order_number="T-1")
        for count, variant in items:
            dron_product.objects.create(order=order, product=self.product, variant=variant, kalichestvo=count)
        order.refresh_from_db()
        return order


class AuthTests(RestoraTestCase):

    def test_register_login_me(self):
        response = self.client.post("/api/auth/register/", {"username": "new", "phon_number": "5", "password": "Pass12345!"})
        self.assertEqual(response.status_code, 201)

        response = self.client.post("/api/auth/login/", {"username": "new", "password": "Pass12345!"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)

        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + response.data["access"])
        response = self.client.get("/api/auth/me/")
        self.assertEqual(response.status_code, 200)

    def test_logout_blacklists_token(self):
        tokens = self.client.post("/api/auth/login/", {"username": "customer", "password": "Pass12345!"}).data
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + tokens["access"])

        self.assertEqual(self.client.post("/api/auth/logout/", {"refresh": tokens["refresh"]}).status_code, 205)
        self.assertEqual(self.client.post("/api/auth/refresh/", {"refresh": tokens["refresh"]}).status_code, 401)

    def test_error_format(self):
        response = self.client.get("/api/orders/")
        self.assertEqual(response.status_code, 401)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["status_code"], 401)


class RolePermissionTests(RestoraTestCase):

    def test_customer_cannot_use_staff_endpoints(self):
        self.login(self.customer)
        for url in ["/api/kitchen/orders/", "/api/reports/sales/", "/api/inventory/ingredients/", "/api/staff/"]:
            self.assertEqual(self.client.get(url).status_code, 403, url)

    def test_chef_sees_kitchen_not_reports(self):
        self.login(self.chef)
        self.assertEqual(self.client.get("/api/kitchen/orders/").status_code, 200)
        self.assertEqual(self.client.get("/api/reports/sales/").status_code, 403)

    def test_customer_cannot_change_order_status(self):
        order = self.make_order()
        self.login(self.customer)
        response = self.client.patch(f"/api/orders/{order.id}/status/", {"status": "ready"})
        self.assertEqual(response.status_code, 403)


class RestaurantTests(RestoraTestCase):

    def test_create_restaurant_makes_owner(self):
        self.login(self.customer)
        response = self.client.post("/api/restaurants/", {"name": "New", "description": "d", "address": "a", "phone_number": "1", "img": image()}, format="multipart")
        self.assertEqual(response.status_code, 201)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.role, "owner")

    def test_create_filial_with_subscription_limit(self):
        self.login(self.owner)
        data = {"name": "F2", "address": "a", "phone_number": "1", "restaurant": self.restaurant.id}

        response = self.client.post("/api/filials/", {**data, "img": image()}, format="multipart")
        self.assertEqual(response.status_code, 201)

        response = self.client.post("/api/filials/", {**data, "name": "F3", "img": image()}, format="multipart")
        self.assertEqual(response.status_code, 400)

    def test_owner_cannot_touch_other_restaurant(self):
        self.login(self.other_owner)
        self.assertEqual(self.client.patch(f"/api/restaurants/{self.restaurant.id}/", {"name": "hack"}).status_code, 404)

        response = self.client.post("/api/filials/", {"name": "x", "address": "a", "phone_number": "1", "restaurant": self.restaurant.id, "img": image()}, format="multipart")
        self.assertEqual(response.status_code, 403)


class SubscriptionTests(RestoraTestCase):

    def test_no_subscription_no_filial(self):
        self.login(self.other_owner)
        response = self.client.post("/api/filials/", {"name": "x", "address": "a", "phone_number": "1", "restaurant": self.other_restaurant.id, "img": image()}, format="multipart")
        self.assertEqual(response.status_code, 400)

        response = self.client.post("/api/subscriptions/subscribe/", {"restaurant": self.other_restaurant.id, "plan": self.plan.id, "payment_method": "card"})
        self.assertEqual(response.status_code, 201)

        response = self.client.post("/api/filials/", {"name": "x", "address": "a", "phone_number": "1", "restaurant": self.other_restaurant.id, "img": image()}, format="multipart")
        self.assertEqual(response.status_code, 201)

    def test_cannot_subscribe_other_restaurant(self):
        self.login(self.other_owner)
        response = self.client.post("/api/subscriptions/subscribe/", {"restaurant": self.restaurant.id, "plan": self.plan.id, "payment_method": "card"})
        self.assertEqual(response.status_code, 403)


class MenuTests(RestoraTestCase):

    def test_create_product(self):
        data = {"name": "Lagman", "decription": "d", "price": "25.00", "category": self.category.id}

        self.login(self.owner)
        self.assertEqual(self.client.post("/api/products/", {**data, "img": image()}, format="multipart").status_code, 201)

        self.login(self.customer)
        self.assertEqual(self.client.post("/api/products/", {**data, "img": image()}, format="multipart").status_code, 403)

        self.login(self.other_owner)
        self.assertEqual(self.client.post("/api/products/", {**data, "img": image()}, format="multipart").status_code, 403)

    def test_menu_is_public(self):
        response = self.client.get(f"/api/menu/?restaurant={self.restaurant.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0]["products"][0]["name"], "Plov")


class ReservationTests(RestoraTestCase):

    def test_book_overlap_cancel(self):
        self.login(self.customer)
        data = {"filial": self.filial.id, "stol": self.stol.id, "date": "2030-01-01", "vakt": "18:00", "guests": 2}

        response = self.client.post("/api/reservations/", data)
        self.assertEqual(response.status_code, 201)
        bron_id = response.data["id"]

        self.assertEqual(self.client.post("/api/reservations/", {**data, "vakt": "19:00"}).status_code, 400)
        self.assertEqual(self.client.post("/api/reservations/", {**data, "vakt": "21:00", "guests": 9}).status_code, 400)

        self.assertEqual(self.client.post(f"/api/reservations/{bron_id}/cancel/").status_code, 200)
        self.assertEqual(self.client.post("/api/reservations/", {**data, "vakt": "19:00"}).status_code, 201)


class OrderTests(RestoraTestCase):

    def test_create_order_and_total(self):
        self.login(self.customer)
        response = self.client.post("/api/orders/", {"filial": self.filial.id, "stol": self.stol.id})
        self.assertEqual(response.status_code, 201)
        order_id = response.data["id"]

        self.client.post("/api/order-products/", {"order": order_id, "product": self.product.id, "kalichestvo": 2})
        self.client.post("/api/order-products/", {"order": order_id, "product": self.product.id, "variant": self.variant.id})

        order = Order.objects.get(pk=order_id)
        self.assertEqual(order.total_price, Decimal("100.00"))
        self.assertEqual(order.dron_product_set.last().product_name, "Plov (big)")

        self.stol.refresh_from_db()
        self.assertEqual(self.stol.status, "busy")

    def test_product_name_snapshot(self):
        order = self.make_order()
        self.product.name = "New name"
        self.product.save()
        self.assertEqual(order.dron_product_set.first().product_name, "Plov")

    def test_send_to_kitchen_flow(self):
        order = self.make_order(items=((2, None),))

        self.login(self.waiter)
        response = self.client.post(f"/api/orders/{order.id}/send-to-kitchen/")
        self.assertEqual(response.status_code, 200)
        kitchen_order_id = response.data["kitchen_order_id"]

        self.login(self.chef)
        self.assertEqual(self.client.post(f"/api/kitchen/orders/{kitchen_order_id}/start/").status_code, 200)
        self.assertEqual(self.client.post(f"/api/kitchen/orders/{kitchen_order_id}/ready/").status_code, 200)

        order.refresh_from_db()
        self.assertEqual(order.status, "ready")
        self.assertTrue(OrderStatusHistory.objects.filter(order=order, new_status="ready").exists())

    def test_coupon_and_loyalty(self):
        order = self.make_order(items=((4, None),))
        Coupon.objects.create(restaurant=self.restaurant, code="SALE10", discount_type="percent", discount_value=10,
                              start_date=timezone.now() - timedelta(days=1), end_date=timezone.now() + timedelta(days=1))

        self.login(self.customer)
        response = self.client.post(f"/api/orders/{order.id}/apply-coupon/", {"code": "sale10"})
        self.assertEqual(response.data["discount"], Decimal("12.00"))

        self.login(self.waiter)
        self.client.patch(f"/api/orders/{order.id}/status/", {"status": "completed"})

        account = LoyaltyAccount.objects.get(user=self.customer)
        self.assertEqual(account.points, 10)


class PaymentTests(RestoraTestCase):

    def test_cashier_payment_and_refund(self):
        order = self.make_order(items=((3, None),))

        self.login(self.customer)
        self.assertEqual(self.client.post("/api/payments/", {"order": order.id, "payment_method": "cash"}).status_code, 403)

        self.login(self.cashier)
        self.assertEqual(self.client.post("/api/payments/", {"order": order.id, "payment_method": "cash", "amount": "100"}).status_code, 400)
        response = self.client.post("/api/payments/", {"order": order.id, "payment_method": "cash"})
        self.assertEqual(response.status_code, 201)
        payment_id = response.data["id"]
        self.assertEqual(response.data["amount"], "90.00")

        self.assertEqual(self.client.post(f"/api/payments/{payment_id}/refund/", {"reason": "x"}).status_code, 403)

        self.login(self.owner)
        response = self.client.post(f"/api/payments/{payment_id}/refund/", {"amount": "40", "reason": "cold"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["payment_status"], "partially_refunded")

    def test_customer_pays_online(self):
        order = self.make_order()
        self.login(self.customer)
        response = self.client.post("/api/payments/", {"order": order.id, "payment_method": "online"})
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data["transaction_id"].startswith("MOCK-"))


class InventoryTests(RestoraTestCase):

    def test_stock_movement_and_order_usage(self):
        rice = Ingredient.objects.create(restaurant=self.restaurant, name="Rice", unit="kg", quantity=1, min_quantity=Decimal("0.5"), price=8)
        ProductIngredient.objects.create(product=self.product, ingredient=rice, quantity=Decimal("0.2"))

        self.login(self.owner)
        self.assertEqual(self.client.post("/api/inventory/stock-movements/", {"ingredient": rice.id, "movement_type": "in", "quantity": "2"}).status_code, 201)
        self.assertEqual(self.client.post("/api/inventory/stock-movements/", {"ingredient": rice.id, "movement_type": "out", "quantity": "99"}).status_code, 400)

        order = self.make_order(items=((5, None),))
        self.assertEqual(self.client.post(f"/api/orders/{order.id}/send-to-kitchen/").status_code, 200)

        rice.refresh_from_db()
        self.assertEqual(rice.quantity, Decimal("2.00"))
        self.assertTrue(StockMovement.objects.filter(ingredient=rice, movement_type="order").exists())

    def test_other_owner_cannot_see_inventory(self):
        Ingredient.objects.create(restaurant=self.restaurant, name="Rice", unit="kg", price=8)
        self.login(self.other_owner)
        self.assertEqual(self.client.get("/api/inventory/ingredients/").data["count"], 0)


class CustomerDataTests(RestoraTestCase):

    def test_customer_sees_only_own_orders(self):
        mine = self.make_order()
        other = self.make_order(user=self.waiter)

        self.login(self.customer)
        ids = [order["id"] for order in self.client.get("/api/orders/").data["results"]]
        self.assertIn(mine.id, ids)
        self.assertNotIn(other.id, ids)
        self.assertEqual(self.client.get(f"/api/orders/{other.id}/").status_code, 404)

    def test_other_owner_cannot_see_orders(self):
        order = self.make_order()
        self.login(self.other_owner)
        self.assertEqual(self.client.get(f"/api/orders/{order.id}/").status_code, 404)
        self.assertEqual(self.client.get("/api/orders/").data["count"], 0)


class DeliveryTests(RestoraTestCase):

    def test_delivery_flow(self):
        courier_user = Custumer.objects.create_user(username="courier", password="Pass12345!")
        order = self.make_order(items=((2, None),))

        self.login(self.owner)
        courier_id = self.client.post("/api/delivery/staff/", {"user": courier_user.id, "filial": self.filial.id, "vehicle": "bike"}).data["id"]
        courier_user.refresh_from_db()
        self.assertEqual(courier_user.role, "delivery")

        self.login(self.customer)
        response = self.client.post("/api/delivery/orders/", {"order": order.id, "address": "Rudaki 1", "phone_number": "900", "delivery_price": "10"})
        self.assertEqual(response.status_code, 201)
        delivery_id = response.data["id"]
        order.refresh_from_db()
        self.assertEqual(order.total_price, Decimal("70.00"))

        self.login(courier_user)
        self.assertEqual(self.client.post(f"/api/delivery/orders/{delivery_id}/picked-up/").status_code, 404)

        self.login(self.owner)
        self.assertEqual(self.client.post(f"/api/delivery/orders/{delivery_id}/assign/", {"delivery_staff": courier_id}).status_code, 200)

        self.login(courier_user)
        self.assertEqual(self.client.get("/api/delivery/orders/").data["count"], 1)
        self.assertEqual(self.client.post(f"/api/delivery/orders/{delivery_id}/delivered/").status_code, 400)
        self.assertEqual(self.client.post(f"/api/delivery/orders/{delivery_id}/picked-up/").status_code, 200)
        self.assertEqual(self.client.post(f"/api/delivery/orders/{delivery_id}/delivered/").status_code, 200)

        order.refresh_from_db()
        self.assertEqual(order.status, "completed")


class AdminAndAuditTests(RestoraTestCase):

    def test_super_admin(self):
        admin = Custumer.objects.create_superuser(username="admin", password="Pass12345!")

        self.login(self.owner)
        self.assertEqual(self.client.get("/api/admin/stats/").status_code, 403)

        self.login(admin)
        self.assertEqual(self.client.get("/api/admin/restaurants/").data["count"], 2)
        self.assertEqual(self.client.post(f"/api/admin/restaurants/{self.restaurant.id}/deactivate/").status_code, 200)

        self.login(self.customer)
        response = self.client.post("/api/orders/", {"filial": self.filial.id})
        self.assertEqual(response.status_code, 400)

    def test_audit_log(self):
        self.login(self.owner)
        self.client.patch(f"/api/restaurants/{self.restaurant.id}/", {"name": "Renamed"})

        log = AuditLog.objects.filter(user=self.owner).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.action, "update")
        self.assertEqual(log.object_id, self.restaurant.id)

        self.assertEqual(self.client.get("/api/audit-logs/").data["count"], 1)

        self.login(self.other_owner)
        self.assertEqual(self.client.get("/api/audit-logs/").data["count"], 0)


@override_settings(GROQ_API_KEY="test-key")
class AITests(RestoraTestCase):

    def test_menu_assistant_uses_only_real_products(self):
        answer = {"answer": "Возьмите плов", "product_ids": [self.product.id, 99999]}

        self.login(self.customer)
        with patch("myapp.ai.ask", return_value=answer) as ask:
            response = self.client.post("/api/ai/menu-assistant/", {"restaurant": self.restaurant.id, "message": "что поесть?"}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual([p["id"] for p in response.data["products"]], [self.product.id])
        self.assertEqual(response.data["total_price"], Decimal("30.00"))
        self.assertIn("Plov", ask.call_args[0][0])

    def test_product_description_save_and_access(self):
        answer = {"description": "Вкусный плов", "short": "Плов"}

        self.login(self.other_owner)
        with patch("myapp.ai.ask", return_value=answer):
            response = self.client.post("/api/ai/product-description/", {"product": self.product.id})
        self.assertEqual(response.status_code, 403)

        self.login(self.owner)
        with patch("myapp.ai.ask", return_value=answer):
            response = self.client.post("/api/ai/product-description/", {"product": self.product.id, "save": True}, format="json")
        self.assertEqual(response.status_code, 200)
        self.product.refresh_from_db()
        self.assertEqual(self.product.decription, "Вкусный плов")

    def test_reports_only_for_own_restaurant(self):
        Review.objects.create(user=self.customer, restaurant=self.restaurant, rating=5, comment="good")

        self.login(self.customer)
        self.assertEqual(self.client.get(f"/api/ai/reviews-summary/?restaurant={self.restaurant.id}").status_code, 403)

        self.login(self.other_owner)
        self.assertEqual(self.client.get(f"/api/ai/reviews-summary/?restaurant={self.restaurant.id}").status_code, 400)

        self.login(self.owner)
        with patch("myapp.ai.ask", return_value={"summary": "ok", "positives": ["good"], "negatives": [], "advice": []}):
            response = self.client.get(f"/api/ai/reviews-summary/?restaurant={self.restaurant.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["rating"], 5.0)

    def test_inventory_forecast_days_left(self):
        rice = Ingredient.objects.create(restaurant=self.restaurant, name="Rice", unit="kg", quantity=10, price=8)
        StockMovement.objects.create(ingredient=rice, movement_type="order", quantity=14, price=1)

        self.login(self.chef)
        with patch("myapp.ai.ask", return_value={"summary": "", "buy_list": [], "warnings": []}):
            response = self.client.get(f"/api/ai/inventory-forecast/?restaurant={self.restaurant.id}&days=7")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["ingredients"][0]["days_left"], 5)

    def test_ai_down_returns_503(self):
        self.login(self.customer)
        with patch("myapp.ai.ask", side_effect=ai.AIError("AI service is not available now")):
            response = self.client.post("/api/ai/menu-assistant/", {"restaurant": self.restaurant.id, "message": "hi"}, format="json")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.data["error"], "AI service is not available now")

    @override_settings(GROQ_API_KEY="")
    def test_no_key(self):
        with self.assertRaises(ai.AIError):
            ai.ask("system", "user")
