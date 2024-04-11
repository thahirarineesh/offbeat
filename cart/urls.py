from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
       path('cart/',views.cart,name='cart'),
       path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
       path('update-cart/<int:product_id>/', views.update_cart, name='update_cart'),
       path('remove_from_cart/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
       path('wishlist/',views.wishlist_view, name='wishlist_view'),
       path('addtowishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
       path('remove_from_wishlist/<int:wishlist_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
       path('add-to-cart-from-wishlist/<int:wishlist_id>/',views.add_to_cart_from_wishlist, name='add_to_cart_from_wishlist'),
       path('checkout',views.checkout,name='checkout'),
       path('success/',views.ordersuccess,name='order_success'),
       path('placeorder/',views.placeorder,name='placeorder'),
       path('my_orders/', views.my_orders, name='my_orders'),
       path('order/<int:order_id>/', views.order_detail, name='order_detail'),
       path('order_invoice/<int:order_id>/', views.order_invoice, name='order_invoice'),
       path('user_cancel_order/', views.user_cancel_order, name='user_cancel_order'),
       path('coupon/', views.coupon, name='coupon'),
       path('addcoupon/', views.addcoupon, name='addcoupon'),
       path('apply_coupon/', views.apply_coupon, name='apply_coupon'),
       path('wallet/',views.wallet,name='wallet'),
       path('pay-with-wallet/', views.pay_with_wallet, name='pay_with_wallet'),
       path('proceed-to-pay',views.proceedtopay,name='proceedtopay'),
       path('razorpay/<int:address_id>/',views.razorpay,name='razorpay'),


            ] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)