from django.urls import path
from home_automation.user import views

urlpatterns = [
    path('user',views.UserList.as_view(),name='user_details'),
    path('user/<int:pk>/', views.UserDetail.as_view()),
    path('login',views.UserLoginView.as_view(),name='login')
]