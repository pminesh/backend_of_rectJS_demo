from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Plan, Coupon, BillingDetail, Transaction, UserPackage

# Plan Admin
@admin.register(Plan)
class PlanAdmin(ImportExportModelAdmin):
    list_display = ['name', 'slug', 'id', 'description', 'device', 'validity', 'price', 'discount', 'status', 'updated_at']
    list_per_page = 12

# Coupon Admin   
@admin.register(Coupon)
class CouponAdmin(ImportExportModelAdmin):
    list_display = ['code', 'id', 'description', 'expiry_date', 'discount_type', 'discount', 'coupon_limit', 'status', 'updated_at']
    ordering = ('-updated_at',)
    readonly_fields = ('coupon_used',)
    list_per_page = 12

# Billing Admin
@admin.register(BillingDetail)
class BillingDetailAdmin(ImportExportModelAdmin):
    list_display = ['user', 'id','plan', 'coupon', 'status', 'updated_at']
    ordering = ('-updated_at',)
    list_per_page = 12
    def has_add_permission(self, request):
        return False

# Transaction Admin
@admin.register(Transaction)
class TransactionAdmin(ImportExportModelAdmin):
    list_display = ['bill', 'id', 'amount', 'currency', 'order_id', 'payment_id', 'is_paid', 'updated_at']
    ordering = ('-updated_at',)
    search_fields = ('order_id', 'payment_id', 'amount', 'currency', 'id')
    list_filter = ('is_paid', )
    date_hierarchy = 'updated_at'
    list_per_page = 12
    def has_add_permission(self, request):
        return False

@admin.register(UserPackage)
class UserPackageAdmin(ImportExportModelAdmin):
    list_display = ['user', 'plan', 'transaction', 'created_at', 'expiry_date', 'status', 'updated_at']
    ordering = ('-updated_at',)
    list_filter = ('plan', )
    date_hierarchy = 'expiry_date'
    list_per_page = 12
    def has_add_permission(self, request):
        return True