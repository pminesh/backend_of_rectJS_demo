from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentStart, PaymentSuccess, PlansView, PlansDetailView, CouponCheckView, CouponDeleteView, BillView, TransactionView
# ,test_payment

# Router Object
router = DefaultRouter()

router.register('bills', BillView, basename='user_bills')

urlpatterns = [
    path('', include(router.urls)),

    # Razorpay
    path('pay/', PaymentStart.as_view(), name="start_payment"),
    path('success/', PaymentSuccess.as_view(), name="payment_success"),

    # Inner Links
    path('plans/', PlansView.as_view(), name="plans"),
    path('plans/<slug>/', PlansDetailView.as_view(), name="plan_detail"),

    # path('billing/<int:pk>/', BillView.as_view(), name="billing"),
    path('coupon/', CouponCheckView.as_view(), name="coupon_check"),
    path('coupon/delete/', CouponDeleteView.as_view(), name="coupon_delete"),
    path('transactions/', TransactionView.as_view(), name="user_transactions"),

    # path('test_payment/', test_payment, name="test_payment"),


]