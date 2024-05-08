"""
URL configuration for cakebox project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from creamy import views
from django.conf import settings
from django.conf.urls.static import static

from rest_framework.authtoken.views import ObtainAuthToken

urlpatterns = [
    path('admin/', admin.site.urls),

    path("register/",views.SignUpView.as_view(),name="signup"),
    path("",views.SignInView.as_view(),name="signin"),
    path("index",views.IndexView.as_view(),name="index"),
    path("cakes/<int:pk>/",views.CakeDetailView.as_view(),name="cake-detail"),
    path("cakes/<int:pk>/add_to_basket/",views.AddToBasketView.as_view(),name="addto-basket"),
    path("basket/items/all/",views.BasketItemListView.as_view(),name="basket-item"),
    path("basket/items/<int:pk>/remove/",views.BasketItemRemoveView.as_view(),name="basketitem-remove"),
    path("basket/items/<int:pk>/qty/change/",views.CartItemUpdateQuantityView.as_view(),name="editcart-qty"),
    path("checkout/",views.CheckOutView.as_view(),name="checkout"),
    path("signout/",views.SignOutView.as_view(),name="signout"),
    path("orders/summary/",views.OrderSummaryView.as_view(),name="order-summary"),
    path("orders/items/<int:pk>/remove/", views.OrderItemRemoveView.as_view(),name="orderitem-remove"),
    path("payment/verification/",views.PaymentVerificationView.as_view(),name="verification"),

    
    
    path("api/v1/register/",views.SignUpApiView.as_view()),
    path("api/v1/token/",ObtainAuthToken.as_view()),
    path("api/v1/cakes/",views.CakeListApiView.as_view()),
    path("api/v1/cakes/<int:pk>/",views.CakeDetailApiView.as_view()),
    path("api/v1/cakes/<int:pk>/addtocart/",views.AddToCartApiView.as_view()),
    path("api/v1/carts/",views.CartListApiView.as_view()),
    path("api/v1/carts/<int:pk>/",views.CartItemUpdateApiView.as_view()),
    path("api/v1/order/",views.CheckOutApiView.as_view()),
    path("api/v1/order/summary/",views.OrderSummaryApiView.as_view()),
    path("api/v1/payment/verification/",views.PaymentVerificationApiView.as_view()),



]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
