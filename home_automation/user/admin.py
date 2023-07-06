from django.contrib import admin
from home_automation.user.models import MyUser

# #user model register on admin panel
# # 05/Oct/2022 Minesh patel
# # ===============================================================================Start
# @admin.register(UserModel)
# class UserModelAdmin(admin.ModelAdmin):
#     list_display = ("id","user_name","user_email","user_password","user_type")
#     list_filter = ('user_type',)
#     list_per_page = 10
# # ===============================================================================End

@admin.register(MyUser)
class UserModelAdmin(admin.ModelAdmin):
    list_display = ("id",'email', 'user_name', 'mobile_number','is_active','is_admin','is_staff','is_active','email_verified','mobile_verified')
    list_filter = ('is_active','is_admin')    
    list_per_page = 10