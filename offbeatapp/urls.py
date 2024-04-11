from django.urls import path
from . import views


urlpatterns = [
    path('',views.home,name='home'),
    path('contact/',views.contact,name='contact'),
    path('signup/',views.signupPage, name='signup'),
    path('otp/', views.verify_signup, name='otp'),
    path('verify_otp/',views.verify_signup,name='verify_signup'),
    path('verify-signup/', views.verify_signup, name='verify_signup_page'),
    path('login/', views.loginPage, name='login'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('logout/',views.logout_view, name='logout'),
    path('Customer/', views.customers, name='customer'),
    path('customer/<int:customer_id>/block/', views.block_customer, name='block_customer'),
    path('customer/<int:customer_id>/unblock/', views.unblock_customer, name='unblock_customer'),
    path('category/<int:id>/update_category/', views.update_category, name='update_category'),
    path('category/<int:category_id>/delete/', views.delete_category, name='delete_category'),
    path('category/<int:category_id>/edit/', views.editcategory, name='edit_category'),
    path('category/', views.category, name='category'),
    path('addc/', views.add_category, name='add_category'),
    path('products/', views.product, name='products'),
    path('add/', views.add_product, name='add_product'),
    path('edit/<int:product_id>/', views.editproduct, name='edit_product'),
    path('product/<int:id>/update/', views.update, name='update'),
    path('product/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('product_list',views.product_list,name='product_list')
]