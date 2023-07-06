from rest_framework import serializers
from django.shortcuts import get_object_or_404
from .models import Transaction, BillingDetail, Plan, Coupon
from .utils import check_coupon
# Payment Serializer
class PaymentSerializer(serializers.ModelSerializer):
    # order_date = serializers.DateTimeField(format="%d %B %Y %I:%M %p")
    class Meta:
        model = Transaction
        fields = ['id', 'order_id', 'amount', 'is_paid', 'bill', 'created_at']
        # fields = '__all__'
        # depth = 2

# Plan Serializer
class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'name', 'slug', 'description', 'validity', 'device', 'price', 'discount', 'final_price']


# Coupon Serializer
class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['code', 'description', 'discount_type', 'discount']

# Coupon Delete Serializer
class CouponDeleteSerializer(serializers.Serializer):
    bill_id = serializers.IntegerField()
    class Meta:
        fields = ['bill_id']

# Billing Serializer
class BillingDetailSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    coupon = CouponSerializer(read_only=True)
    class Meta:
        model = BillingDetail
        fields = ['id', 'user', 'plan', 'coupon']
        # extra_kwargs = {
        #     'billing_name': {'required': True},
        #     'billing_mobile': {'required': True},
        # }
        # read_only_fields = ('status', )

    def to_representation(self, instance):
        
        data = super().to_representation(instance)
        data['plan'] = PlanSerializer(Plan.objects.get(pk=data['plan'])).data # Added for Posting Data on Post

        if data['coupon']:
            coupon = get_object_or_404(Coupon, code=data['coupon']['code'])
            response = check_coupon(coupon, data['plan']['final_price'])
            data['coupon']['price'] = data['plan']['final_price']
            data['coupon']['price_after_discount'] = response
        return data

    def validate(self, attrs):
        if plan := attrs.get('plan', ''):
            return super().validate(attrs)
        else:
            raise serializers.ValidationError({"plan": "Select a plan to continue."})

# Transaction Serializer
class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'order_id', 'amount', 'is_paid', 'bill', 'created_at']