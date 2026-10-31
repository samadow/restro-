from django.urls import path
from .views import *

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)


urlpatterns = [
    path('register/', RegisterApi.as_view(), name='register'),
    path("profil_cr/", Profil_cr.as_view()),
    path('profile/<int:pk>/', ProfilApi.as_view(), name='profile'),
    path("Restarant/<int:pk>/", RestarantApi.as_view()),
    path("resta_cr/", Cr_rest.as_view()),
    path("filial/<int:pk>/", filialApi.as_view()),
    path("cr_filial/", cr_filial.as_view()),
    path("stol/<int:pk>/", StolApi.as_view()),
    path("cr_stol/", cr_Stol.as_view()),
    path("categoryapi/", CategoruApi.as_view()),
    path("categoryapi/<int:pk>/", CategoryDetail.as_view()),
    path("productApi/", ProductApi.as_view()),
    path("productApi/<int:pk>/", ProductDetail.as_view()),
    path("product-variants/", ProductVariantApi.as_view()),
    path("product-variants/<int:pk>/", ProductVariantDetail.as_view()),
    path("product-extras/", ProductExtraApi.as_view()),
    path("product-extras/<int:pk>/", ProductExtraDetail.as_view()),
    path("reservations/", DronStolList.as_view()),
    path("reservations/<int:pk>/", DronStolDetail.as_view()),
    path("orders/", OrderApi.as_view()),
    path("orders/<int:pk>/", OrderDetail.as_view()),
    path("order-products/", AddProduct.as_view()),
    path("order-products/<int:pk>/quantity/", update_quantity),
    path("order-products/<int:pk>/total/", calculate_total),
    path("orders/<int:pk>/assign-table/", assign_table),
    path("orders/<int:pk>/status/", change_order_status),
    path("orders/<int:pk>/cancel/", cancel_order),
    path("orders/<int:pk>/send-to-kitchen/", send_to_kitchen),
    path("orders/<int:pk>/history/", get_order_history),
    path("orders/<int:pk>/complete/", complete_order),

    # 4.1 Auth
    path("auth/register/", RegisterApi.as_view()),
    path("auth/login/", TokenObtainPairView.as_view()),
    path("auth/refresh/", TokenRefreshView.as_view()),
    path("auth/logout/", LogoutView.as_view()),
    path("auth/me/", MyProfile.as_view()),
    path("auth/change-password/", change_password),
    path("auth/users/<int:pk>/role/", change_role),

    # 4.2 Restaurant / filial
    path("restaurants/", RestaurantList.as_view()),
    path("restaurants/<int:pk>/", RestarantApi.as_view()),
    path("restaurant-settings/", RestaurantSettingsApi.as_view()),
    path("restaurant-settings/<int:pk>/", RestaurantSettingsDetail.as_view()),
    path("staff/", StaffApi.as_view()),
    path("staff/<int:pk>/", StaffDetail.as_view()),
    path("filials/", FilialList.as_view()),
    path("filials/<int:pk>/", filialApi.as_view()),

    # 4.3 Menu
    path("menu/", MenuApi.as_view()),
    path("categories/", CategoruApi.as_view()),
    path("categories/<int:pk>/", CategoryDetail.as_view()),
    path("products/", ProductApi.as_view()),
    path("products/<int:pk>/", ProductDetail.as_view()),

    # 4.4 Stol / bron
    path("tables/", StolList.as_view()),
    path("tables/<int:pk>/", StolApi.as_view()),
    path("tables/<int:pk>/available/", stol_available),
    path("reservations/<int:pk>/cancel/", cancel_reservation),
    path("reservations/<int:pk>/status/", change_reservation_status),

    # 4.5 Orders
    path("orders/<int:pk>/assign-customer/", assign_customer),

    # 4.6 Kitchen
    path("kitchens/", KitchenApi.as_view()),
    path("kitchens/<int:pk>/", KitchenDetail.as_view()),
    path("kitchen/orders/", KitchenOrderList.as_view()),
    path("kitchen/orders/<int:pk>/", KitchenOrderDetail.as_view()),
    path("kitchen/orders/<int:pk>/start/", kitchen_start),
    path("kitchen/orders/<int:pk>/ready/", kitchen_ready),
    path("kitchen/items/<int:pk>/ready/", kitchen_item_ready),

    # 4.7 Payments
    path("payments/", PaymentApi.as_view()),
    path("payments/<int:pk>/", PaymentDetail.as_view()),
    path("payments/<int:pk>/refund/", refund_payment),
    path("orders/<int:pk>/payment-status/", order_payment_status),

    # 4.8 Inventory
    path("inventory/ingredients/", IngredientApi.as_view()),
    path("inventory/ingredients/<int:pk>/", IngredientDetail.as_view()),
    path("inventory/low-stock/", low_stock),
    path("inventory/suppliers/", SupplierApi.as_view()),
    path("inventory/suppliers/<int:pk>/", SupplierDetail.as_view()),
    path("inventory/product-ingredients/", ProductIngredientApi.as_view()),
    path("inventory/product-ingredients/<int:pk>/", ProductIngredientDetail.as_view()),
    path("inventory/stock-movements/", StockMovementApi.as_view()),
    path("orders/<int:pk>/ingredients/", get_order_ingredients),

    # 4.9 Staff
    path("staff/shifts/", StaffShiftApi.as_view()),
    path("staff/shifts/<int:pk>/", StaffShiftDetail.as_view()),
    path("staff/shifts/<int:pk>/end/", end_shift),
    path("staff/attendance/", StaffAttendanceApi.as_view()),
    path("staff/attendance/<int:pk>/", StaffAttendanceDetail.as_view()),
    path("staff/attendance/check-in/", check_in),
    path("staff/attendance/check-out/", check_out),

    # 4.10 Customers
    path("customers/me/", customer_me),
    path("customers/me/orders/", CustomerOrdersApi.as_view()),
    path("customers/me/addresses/", CustomerAddressApi.as_view()),
    path("customers/me/addresses/<int:pk>/", CustomerAddressDetail.as_view()),
    path("customers/me/favorites/", CustomerFavoriteApi.as_view()),
    path("customers/me/favorites/<int:pk>/", CustomerFavoriteDetail.as_view()),
    path("reviews/", ReviewApi.as_view()),
    path("reviews/<int:pk>/", ReviewDetail.as_view()),
    path("restaurants/<int:pk>/rating/", restaurant_rating),

    # 4.11 Notifications
    path("notifications/", NotificationApi.as_view()),
    path("notifications/unread-count/", unread_count),
    path("notifications/<int:pk>/read/", read_notification),
    path("notifications/read-all/", read_all_notifications),
    path("restaurant-notifications/", RestaurantNotificationApi.as_view()),
    path("restaurant-notifications/<int:pk>/read/", read_restaurant_notification),
    path("restaurant-notifications/read-all/", read_all_restaurant_notifications),

    # 4.13 Reports
    path("reports/daily/", daily_report),
    path("reports/daily/history/", DailyReportHistory.as_view()),
    path("reports/sales/", sales_report),
    path("reports/filials/", filials_report),
    path("reports/products/", products_report),
    path("reports/payments/", payments_report),
    path("reports/cancelled/", cancelled_report),
    path("reports/expenses/", ExpenseApi.as_view()),
    path("reports/expenses/<int:pk>/", ExpenseDetail.as_view()),

    # 4.14 Subscription
    path("subscriptions/plans/", SubscriptionPlanApi.as_view()),
    path("subscriptions/plans/<int:pk>/", SubscriptionPlanDetail.as_view()),
    path("subscriptions/current/", current_subscription),
    path("subscriptions/subscribe/", subscribe),
    path("subscriptions/payments/", SubscriptionPaymentApi.as_view()),
    path("subscriptions/history/", SubscriptionHistory.as_view()),

    # 4.15 Loyalty / Coupon
    path("coupons/", CouponApi.as_view()),
    path("coupons/<int:pk>/", CouponDetail.as_view()),
    path("coupons/validate/", validate_coupon),
    path("orders/<int:pk>/apply-coupon/", apply_coupon),
    path("loyalty/", LoyaltyApi.as_view()),
    path("loyalty/redeem/", redeem_points),

    # 4.12 Delivery
    path("delivery/staff/", DeliveryStaffApi.as_view()),
    path("delivery/staff/<int:pk>/", DeliveryStaffDetail.as_view()),
    path("delivery/orders/", DeliveryApi.as_view()),
    path("delivery/orders/<int:pk>/", DeliveryDetail.as_view()),
    path("delivery/orders/<int:pk>/assign/", assign_delivery),
    path("delivery/orders/<int:pk>/picked-up/", picked_up_delivery),
    path("delivery/orders/<int:pk>/delivered/", delivered_delivery),

    # 4.16 Audit log
    path("audit-logs/", AuditLogApi.as_view()),

    # Super Admin
    path("admin/restaurants/", AdminRestaurantApi.as_view()),
    path("admin/restaurants/<int:pk>/<str:action>/", admin_restaurant_active),
    path("admin/stats/", admin_stats),

    # AI
    path("ai/menu-assistant/", ai_menu_assistant),
    path("ai/product-description/", ai_product_description),
    path("ai/reviews-summary/", ai_reviews_summary),
    path("ai/sales-insights/", ai_sales_insights),
    path("ai/inventory-forecast/", ai_inventory_forecast),

    # Login / Token
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
]