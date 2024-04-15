from django.urls import path
from . import views



urlpatterns = [
    path('adminn/', views.admin_login,name='admin'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin_logout/',views.admin_logout,name='admin_logout'),
    path('order/',views.order,name = 'order'),
<<<<<<< HEAD
    path('admin_order_details/<int:order_id>/', views.admin_order_details, name='admin_order_details'),
=======
>>>>>>> ad1ccebe2dc1cab1ae7d6af9981a0bef86943c2c
    path('update_order/', views.updateorder, name='update_order'),
    path('cancel_order/', views.cancel_order, name='cancel_order'),
    path('return_order/', views.return_order, name='user_return_order'),
    path('report-pdf-order/', views.report_pdf_order, name='report_pdf_order'),

<<<<<<< HEAD
]
=======
]
>>>>>>> ad1ccebe2dc1cab1ae7d6af9981a0bef86943c2c
