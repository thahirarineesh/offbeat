from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
          path('productdetail/<int:product_id>',views.productdetails,name='productdetail'),
          path('profile/', views.Profile, name='profile'),
          path('edit_profile/', views.edit_profile, name='edit_profile'),
          path('edit_address/<int:address_id>/',views.edit_address,name='edit_address'),
          path('delete_address/<int:address_id>/delete/', views.delete_address, name='delete_address'),
          path('change-password/', views.change_password, name='change_password'),
          path('search/',views.search,name='search'),


              ]+ static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
