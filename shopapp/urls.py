from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('search/', views.search_products, name='search'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('coupon/apply/', views.apply_coupon, name='apply_coupon'),
    path('import/', views.import_data, name='import_data'),
]
