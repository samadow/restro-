
from rest_framework import serializers
from django.db import transaction
from django.utils import timezone
from .models import *
from decimal import Decimal
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes


class CustumerSerializers(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Custumer
        fields = [
            'username',
            'phon_number',
            'password'
        ]

    @transaction.atomic
    def create(self, validated_data):
        user = Custumer.objects.create_user(**validated_data)
        Profile.objects.create(user=user)
        return user


class ProfillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id','fullname','bio','phon_number','img','role']
        read_only_fields = ["id",'user','cr_at','role']


class RestarantSSerializers(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['id','name','description','address','phone_number','img','owner']
        read_only_fields = ['id','cr_at','owner',]

class FilialSerializer(serializers.ModelSerializer):
    restaurant_id = RestarantSSerializers(source='restaurant',read_only=True)

    class Meta:
        model = filial
        fields = ['id','name','phone_number','address','restaurant','restaurant_id','img','is_active']
        read_only_fields = ['id', 'cr_at']
        extra_kwargs = {'is_active': {'default': True}}



class StolSerializers(serializers.ModelSerializer):
    filial_id = FilialSerializer(source='filial' ,read_only=True)

    class Meta:
        model = Stol
        fields = ['id','name','description','capacity','status','filial','filial_id']
        read_only_fields = ['id']

class CategorySerialiyser(serializers.ModelSerializer):
    restaurant_id = RestarantSSerializers(source='restaurant',read_only=True)
    class Meta:
        model = Category
        fields = ['id','name','description','restaurant','img','restaurant_id','is_active']
        read_only_fields = ['id','cr_at']
        extra_kwargs = {'is_active': {'default': True}}


class ProductSerialayzer(serializers.ModelSerializer):
    categori_id = CategorySerialiyser(source='category',read_only=True)
    class Meta:
        model = Product
        fields = ['id','name','decription','price','preparation_time','img','category','categori_id','is_available']
        read_only_fields = ['id','cr_at']
        extra_kwargs = {'is_available': {'default': True}}

class ProductVariantSeriali(serializers.ModelSerializer):
    product_id = ProductSerialayzer(source='product',read_only=True)
    class Meta:
        model = ProductVariant
        fields = ['id','name','price','product','product_id','is_active']
        read_only_fields = ['id']


class ProductExtraSeriali(serializers.ModelSerializer):
    product_id = ProductSerialayzer(source='product',read_only=True)
    class Meta:
        model = ProductExtra
        fields = ['id','name','price','is_active','product','product_id']
        read_only_fields = ['id']


class DronStolSerializer(serializers.ModelSerializer):
    filial_id = FilialSerializer(source='filial', read_only=True)
    stol_id = StolSerializers(source='stol', read_only=True)

    class Meta:
        model = dron_stol
        fields = ['id','user','filial','filial_id','stol','stol_id','date','vakt','end_time','guests','status','comment']
        read_only_fields = ['id', 'cr_at','user','status']


class OrderSerialiser(serializers.ModelSerializer):
    filial_id = FilialSerializer(source="filial",read_only=True)
    stol_id = StolSerializers(source="stol",read_only=True)
    reservation_id = DronStolSerializer(source="reservation",read_only=True)
    class Meta:
        model = Order
        fields = ['id','user','filial','filial_id','stol','stol_id','reservation','reservation_id','order_number','order_type','status','total_price','comment','discount','coupon','points_used']
        # money is calculated on the server only (coupon + loyalty points)
        read_only_fields = ['id','user','status','total_price','discount','coupon','points_used']
        extra_kwargs = {'order_number': {'required': False}}


class Bron_productSeria(serializers.ModelSerializer):
    order_id = OrderSerialiser(source='order',read_only=True)
    product_id = ProductSerialayzer(source='product',read_only=True)
    variant_id = ProductVariantSeriali(source='variant',read_only=True)

    class Meta:
        model = dron_product
        fields = ['id','kalichestvo','total_price','price','order','order_id','variant','variant_id','product','product_id','comment']
        # price is taken from product / variant on the server
        read_only_fields=['id','total_price','price']

    def validate(self, data):
        order = data.get("order", getattr(self.instance, "order", None))
        product = data.get("product", getattr(self.instance, "product", None))
        variant = data.get("variant", getattr(self.instance, "variant", None))

        if self.instance and "order" in data and data["order"].pk != self.instance.order_id:
            raise serializers.ValidationError({"order": "Item cannot be moved to another order"})

        if product.category.restaurant_id != order.filial.restaurant_id:
            raise serializers.ValidationError({"product": "This product is not from the restaurant of this order"})

        if not product.is_available or not product.category.is_active:
            raise serializers.ValidationError({"product": "This product is not available"})

        if variant and (variant.product_id != product.id or not variant.is_active):
            raise serializers.ValidationError({"variant": "This variant is not for this product"})

        return data

    def update(self, instance, validated_data):
        if "product" in validated_data or "variant" in validated_data:
            # product or variant changed - take new price and name from the menu
            instance.price = None
            instance.product_name = ""

        return super().update(instance, validated_data)


# RESTAURANT

class RestaurantSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantSettings
        fields = ['id','restaurant','currency','language','opening_time','closing_time','delivery_enabled','reservation_enabled']
        read_only_fields = ['id','cr_at']


class StaffSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    filial_name = serializers.CharField(source='filial.name', read_only=True)

    class Meta:
        model = Staff
        fields = ['id','user','username','restaurant','filial','filial_name','position','salary','is_active','cr_at']
        read_only_fields = ['id','cr_at']


class StaffShiftSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='staff.user.username', read_only=True)
    hours = serializers.SerializerMethodField()

    class Meta:
        model = StaffShift
        fields = ['id','staff','username','start_time','end_time','status','hours','cr_at']
        read_only_fields = ['id','end_time','status','cr_at']
        extra_kwargs = {'start_time': {'required': False}}

    def get_hours(self, obj) -> float:
        end = obj.end_time or timezone.now()
        return round((end - obj.start_time).total_seconds() / 3600, 2)


class StaffAttendanceSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='staff.user.username', read_only=True)

    class Meta:
        model = StaffAttendance
        fields = ['id','staff','username','date','check_in','check_out','status']
        read_only_fields = ['id']
        extra_kwargs = {'date': {'required': False}}


# MENU

class MenuVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id','name','price']


class MenuExtraSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductExtra
        fields = ['id','name','price']


class MenuProductSerializer(serializers.ModelSerializer):
    variants = serializers.SerializerMethodField()
    extras = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id','name','decription','price','preparation_time','img','variants','extras']

    @extend_schema_field(MenuVariantSerializer(many=True))
    def get_variants(self, obj):
        variants = obj.productvariant_set.filter(is_active=True)
        return MenuVariantSerializer(variants, many=True).data

    @extend_schema_field(MenuExtraSerializer(many=True))
    def get_extras(self, obj):
        extras = obj.productextra_set.filter(is_active=True)
        return MenuExtraSerializer(extras, many=True).data


class MenuSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id','name','description','img','restaurant','products']

    @extend_schema_field(MenuProductSerializer(many=True))
    def get_products(self, obj):
        products = obj.product_set.filter(is_available=True)
        return MenuProductSerializer(products, many=True, context=self.context).data


# KITCHEN

class KitchenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kitchen
        fields = ['id','filial','name','is_active']
        read_only_fields = ['id']


class KitchenOrderItemSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source='order_item.product.name', read_only=True)
    variant = serializers.CharField(source='order_item.variant.name', read_only=True, default=None)
    kalichestvo = serializers.IntegerField(source='order_item.kalichestvo', read_only=True)
    comment = serializers.CharField(source='order_item.comment', read_only=True)
    preparation_time = serializers.IntegerField(source='order_item.product.preparation_time', read_only=True)

    class Meta:
        model = KitchenOrderItem
        fields = ['id','product','variant','kalichestvo','comment','preparation_time','status','started_at','finished_at']


class KitchenOrderSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    stol = serializers.CharField(source='order.stol.name', read_only=True, default=None)
    order_time = serializers.DateTimeField(source='order.cr_at', read_only=True)
    items = serializers.SerializerMethodField()
    preparation_time = serializers.SerializerMethodField()
    cooking_minutes = serializers.SerializerMethodField()

    class Meta:
        model = KitchenOrder
        fields = ['id','order','order_number','stol','kitchen','status','order_time','cr_at','started_at','finished_at','preparation_time','cooking_minutes','items']

    @extend_schema_field(KitchenOrderItemSerializer(many=True))
    def get_items(self, obj):
        items = obj.kitchenorderitem_set.all()
        return KitchenOrderItemSerializer(items, many=True).data

    def get_preparation_time(self, obj) -> int:
        times = [item.order_item.product.preparation_time for item in obj.kitchenorderitem_set.all()]
        return max(times) if times else 0

    def get_cooking_minutes(self, obj) -> int:
        if not obj.started_at:
            return None

        end = obj.finished_at or timezone.now()
        return int((end - obj.started_at).total_seconds() // 60)


# PAYMENTS

class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = ['id','payment','amount','reason','status','cr_at']
        read_only_fields = ['id','payment','status','cr_at']
        extra_kwargs = {'amount': {'required': False}}


class PaymentSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    refunds = RefundSerializer(source='refund_set', many=True, read_only=True)

    class Meta:
        model = Payment
        fields = ['id','order','order_number','user','amount','payment_method','status','transaction_id','refunds','cr_at']
        read_only_fields = ['id','user','status','transaction_id','cr_at']
        extra_kwargs = {'amount': {'required': False}}


# INVENTORY

class IngredientSerializer(serializers.ModelSerializer):
    is_low = serializers.SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = ['id','restaurant','name','unit','quantity','min_quantity','price','is_low','cr_at']
        read_only_fields = ['id','cr_at']

    def get_is_low(self, obj) -> bool:
        return obj.quantity <= obj.min_quantity


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id','restaurant','name','phone_number','address','cr_at']
        read_only_fields = ['id','cr_at']


class ProductIngredientSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    ingredient_name = serializers.CharField(source='ingredient.name', read_only=True)
    unit = serializers.CharField(source='ingredient.unit', read_only=True)

    class Meta:
        model = ProductIngredient
        fields = ['id','product','product_name','ingredient','ingredient_name','unit','quantity']
        read_only_fields = ['id']


class StockMovementSerializer(serializers.ModelSerializer):
    ingredient_name = serializers.CharField(source='ingredient.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True, default=None)

    class Meta:
        model = StockMovement
        fields = ['id','ingredient','ingredient_name','supplier','supplier_name','movement_type','quantity','price','comment','cr_at']
        read_only_fields = ['id','cr_at']
        extra_kwargs = {'price': {'required': False}}


# CUSTOMERS

class CustomerAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerAddress
        fields = ['id','address','city','is_default']
        read_only_fields = ['id']


class CustomerFavoriteSerializer(serializers.ModelSerializer):
    restaurant_id = RestarantSSerializers(source='restaurant', read_only=True)

    class Meta:
        model = CustomerFavorite
        fields = ['id','restaurant','restaurant_id','cr_at']
        read_only_fields = ['id','cr_at']


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Review
        fields = ['id','user','username','restaurant','order','rating','comment','cr_at']
        read_only_fields = ['id','user','cr_at']
        extra_kwargs = {'rating': {'min_value': 1, 'max_value': 5}}


# NOTIFICATIONS

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id','title','message','notification_type','is_read','cr_at']
        read_only_fields = ['id','title','message','notification_type','cr_at']


class RestaurantNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantNotification
        fields = ['id','restaurant','title','message','notification_type','is_read','cr_at']
        read_only_fields = ['id','restaurant','title','message','notification_type','cr_at']


# REPORTS

class ExpenseSerializer(serializers.ModelSerializer):
    filial_name = serializers.CharField(source='filial.name', read_only=True)

    class Meta:
        model = Expense
        fields = ['id','restaurant','filial','filial_name','title','amount','category','comment','date','cr_at']
        read_only_fields = ['id','cr_at']
        extra_kwargs = {'date': {'required': False}}


class DailyReportSerializer(serializers.ModelSerializer):
    filial_name = serializers.CharField(source='filial.name', read_only=True)

    class Meta:
        model = DailyReport
        fields = ['id','restaurant','filial','filial_name','date','total_orders','total_sales','total_payments','cr_at']


# SUBSCRIPTION

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['id','name','description','price','duration_days','max_filial','max_staff','is_active']
        read_only_fields = ['id']
        extra_kwargs = {'is_active': {'default': True}}


class RestaurantSubscriptionSerializer(serializers.ModelSerializer):
    plan_id = SubscriptionPlanSerializer(source='plan', read_only=True)
    days_left = serializers.SerializerMethodField()

    class Meta:
        model = RestaurantSubscription
        fields = ['id','restaurant','plan','plan_id','start_date','end_date','status','days_left','cr_at']

    def get_days_left(self, obj) -> int:
        return max((obj.end_date - timezone.localdate()).days, 0)


class SubscriptionPaymentSerializer(serializers.ModelSerializer):
    restaurant = serializers.IntegerField(source='subscription.restaurant_id', read_only=True)
    plan = serializers.CharField(source='subscription.plan.name', read_only=True)

    class Meta:
        model = SubscriptionPayment
        fields = ['id','subscription','restaurant','plan','amount','payment_method','status','transaction_id','cr_at']


class SubscribeSerializer(serializers.Serializer):
    restaurant = serializers.PrimaryKeyRelatedField(queryset=Restaurant.objects.all())
    plan = serializers.PrimaryKeyRelatedField(queryset=SubscriptionPlan.objects.all())
    payment_method = serializers.ChoiceField(choices=PAYMENT_METHOD)


# COUPON / LOYALTY

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id','restaurant','code','discount_type','discount_value','min_order_price','start_date','end_date','is_active','cr_at']
        read_only_fields = ['id','cr_at']
        extra_kwargs = {'is_active': {'default': True}}

    def validate(self, data):
        discount_type = data.get("discount_type", getattr(self.instance, "discount_type", None))
        discount_value = data.get("discount_value", getattr(self.instance, "discount_value", 0))
        start_date = data.get("start_date", getattr(self.instance, "start_date", None))
        end_date = data.get("end_date", getattr(self.instance, "end_date", None))

        if discount_value <= 0:
            raise serializers.ValidationError({"discount_value": "Must be more than 0"})
        if discount_type == "percent" and discount_value > 100:
            raise serializers.ValidationError({"discount_value": "Percent cannot be more than 100"})
        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError({"end_date": "end_date must be after start_date"})

        return data


class LoyaltyTransactionSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='order.order_number', read_only=True, default=None)

    class Meta:
        model = LoyaltyTransaction
        fields = ['id','order','order_number','points','transaction_type','cr_at']


class LoyaltyAccountSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    points_price = serializers.SerializerMethodField()
    transactions = serializers.SerializerMethodField()

    class Meta:
        model = LoyaltyAccount
        fields = ['id','restaurant','restaurant_name','points','points_price','transactions','cr_at']

    def get_points_price(self, obj) -> Decimal:
        return obj.points * POINT_PRICE

    @extend_schema_field(LoyaltyTransactionSerializer(many=True))
    def get_transactions(self, obj):
        transactions = obj.loyaltytransaction_set.all().order_by("-cr_at")[:20]
        return LoyaltyTransactionSerializer(transactions, many=True).data


# DELIVERY

class DeliveryStaffSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    filial_name = serializers.CharField(source='filial.name', read_only=True)

    class Meta:
        model = DeliveryStaff
        fields = ['id','user','username','filial','filial_name','vehicle','is_active']
        read_only_fields = ['id']
        extra_kwargs = {'is_active': {'default': True}}


class DeliverySerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    order_status = serializers.CharField(source='order.status', read_only=True)
    must_pay = serializers.SerializerMethodField()
    courier = serializers.CharField(source='delivery_staff.user.username', read_only=True, default=None)

    class Meta:
        model = Delivery
        fields = ['id','order','order_number','order_status','must_pay','delivery_staff','courier','address','phone_number','delivery_price','status','picked_up_at','delivered_at','cr_at','updated_at']
        read_only_fields = ['id','delivery_staff','status','picked_up_at','delivered_at','cr_at','updated_at']

    def get_must_pay(self, obj) -> Decimal:
        return obj.order.total_price - obj.order.discount


# SUPER ADMIN / AUDIT

class AdminRestaurantSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    filials = serializers.SerializerMethodField()
    subscription = serializers.SerializerMethodField()

    class Meta:
        model = Restaurant
        fields = ['id','name','owner','owner_username','phone_number','address','is_active','filials','subscription','cr_at']

    def get_filials(self, obj) -> int:
        return obj.filial_set.count()

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_subscription(self, obj):
        today = timezone.localdate()
        subscription = obj.restaurantsubscription_set.filter(
            status="active", start_date__lte=today, end_date__gte=today
        ).first()

        if not subscription:
            return None

        return {"plan": subscription.plan.name, "end_date": subscription.end_date}


class AuditLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True, default=None)

    class Meta:
        model = AuditLog
        fields = ['id','user','username','restaurant','action','model_name','object_id','description','cr_at']
