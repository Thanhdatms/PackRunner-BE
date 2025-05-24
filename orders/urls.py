"""
URL configuration for PackRunner project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from .views import OrderCreateView, OrderDetailView, OrderStatusUpdateView, PaymentView, OrderListView, OrderStatisticsView, EstimateShippingCostView
urlpatterns = [
    path('', OrderCreateView.as_view(), name='order-create'),
    path('list/', OrderListView.as_view(), name='order-list'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('<int:pk>/status/', OrderStatusUpdateView.as_view()),
    path('payment/', PaymentView.as_view()),
    path('statistics/',OrderStatisticsView.as_view()),
    path('estimate-shipping-cost/', EstimateShippingCostView.as_view(), name='estimate-shipping-cost'),
    # path('payment/<int:pk>/', PaymentView.as_view()),  # Uncomment if needed
    # path('shipment/',ShipmentView.as_view())

]
