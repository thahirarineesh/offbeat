from datetime import timedelta, timezone

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView,LogoutView
from django.core.paginator import Paginator
from django.http import FileResponse, HttpResponse
from django.urls import reverse_lazy
from django.db.models import Sum,Count
import json
from django.http import JsonResponse
from django.db.models import Sum, DecimalField, F
from django.db.models.functions import Cast
from django.db.models.functions import TruncWeek,TruncMonth,TruncYear,ExtractWeek
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from decimal import Decimal
import matplotlib.pyplot as plt
import io
import base64
from django.db.models.functions import TruncWeek,TruncMonth,TruncYear,ExtractWeek
from decimal import Decimal

from django.shortcuts import render,redirect,get_object_or_404
from django.utils.datetime_safe import datetime
from django.views.decorators.cache import cache_control, never_cache
from django.contrib import messages
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import A4

from cart.models import Order, OrderItem,Wallet
from offbeatapp.models import *
from shop.models import *
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from django.http import HttpResponseForbidden

# Create your views here.

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def admin_login(request):
    if 'email' in request.session:
        return redirect('home')
    elif "admin" in request.session:
        return redirect("dashboard")
    else:
        if request.method == "POST":
            username = request.POST.get("username")
            pass1 = request.POST.get("pass")
            user = authenticate(request, username=username, password=pass1)

            if user is not None and user.is_superuser:
                login(request, user)
                request.session["admin"] = username
                return redirect("dashboard")
            else:
                messages.error(request, "username or password is not same")
                return render(request, "admin/admin_login.html")
        else:
            return render(request, "admin/admin_login.html")

@never_cache
def admin_logout(request):
    if "admin" in request.session:
        request.session.flush()
    logout(request)
    return redirect("admin")

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def dashboard(request):
    if "admin" in request.session:
      admin_name = "Thahira"
      products_with_more_orders = Product.objects.annotate(order_count=Count('order')).order_by('-order_count')[:6]
      categories_with_most_orders = Category.objects.annotate(order_count=Count('product__order__id')).order_by('-order_count')[:6]
      orders = Order.objects.all().order_by("-id")[:6]
      order_item_counts = OrderItem.objects.values('product').annotate(order_item_count=Count('id'))
      labels = []
      data = []
      for order in orders:
        labels.append(str(order.id))
        data.append(order.amount)

      context = {
        "admin_name": admin_name,
        'products_with_more_orders': products_with_more_orders,
        'categories_with_most_orders': categories_with_most_orders,
        'labels': json.dumps(labels),
        'data': json.dumps(data),
        'order_item_counts': order_item_counts,
        'orders':orders


      }
      return render(request, "dashboard.html", context)

# def dashboard(request):
#     admin_name = "Thahira"
#     products_with_more_orders = Product.objects.annotate(order_count=Count('order')).order_by('-order_count')[:6]
#     categories_with_most_orders = Category.objects.annotate(order_count=Count('product__order')).order_by('-order_count')[:6]
#     latest_orders = Order.objects.order_by("-id")[:5]
#     order_item_counts = OrderItem.objects.values('product').annotate(order_item_count=Count('id'))
#     labels = []
#     data = []
#     for order in latest_orders:
#         labels.append(str(order.id))
#         data.append(order.amount)
#
#
#     context = {
#         "labels": json.dumps(labels),
#         "data": json.dumps(data),
#         'products_with_more_orders': products_with_more_orders,
#         'categories_with_most_orders': categories_with_most_orders,
#         "admin_name": admin_name,
#         'order_item_counts': order_item_counts,
#     }
    #
    # if "admin" in request.session:
    #     time_range = request.POST.get('time_range', 'month')
    #     context['time_range'] = time_range
    #     if time_range == 'month':
    #             monthly_sales = Order.objects.annotate(month=TruncMonth('date')).values('month').annotate(
    #             total_sales=Count('id')).order_by('month')
    #             labels = [sales['month'].strftime('%B') for sales in monthly_sales]
    #             data = [sales['total_sales'] for sales in monthly_sales]
    #     elif time_range == 'year':
    #              yearly_sales = Order.objects.annotate(year=TruncYear('date')).values('year').annotate(
    #              total_sales=Count('id')).order_by('year')
    #              labels = [f"Year {sales['year'].year}" for sales in yearly_sales]
    #              data = [sales['total_sales'] for sales in yearly_sales]
    #     elif time_range == 'week':
    #            weekly_sales = Order.objects.annotate(week=ExtractWeek('date')).values('week').annotate(
    #            total_sales=Count('id')).order_by('week')
    #            labels = [f"Week {sales['week']}" for sales in weekly_sales]
    #            data = [sales['total_sales'] for sales in weekly_sales]
    #     else:
    #         monthly_sales = Order.objects.annotate(month=TruncMonth('date')).values('month').annotate(
    #         total_sales=Count('id')).order_by('month')
    #         labels = [sales['month'].strftime('%B') for sales in monthly_sales]
    #         data = [sales['total_sales'] for sales in monthly_sales]
    #     context={
    #             'labels': labels,
    #             'data': data,
    #             'time_range': time_range,
    #     }

    # return render(request, "dashboard.html", context)
    # else:
    #     return redirect("admin")

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def order(request):
    if "admin" in request.session:
        orders = Order.objects.all().order_by("-id")

        paginator = Paginator(orders, per_page=10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context = {
            "orders": page_obj,
        }
        return render(request, "admin/orders.html", context)
    else:
        return redirect("admin")

@login_required
def admin_order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    for order_item in order_items:
        order_item.total = order_item.quantity * order_item.product.price

    context = {
        'order': order,
        'order_items': order_items,

    }
    print(context)

    return render(request, 'admin/admin_order_details.html', context)


def updateorder(request):
    if request.method == "POST":
        order_id = request.POST.get("order_id")
        status = request.POST.get("status")

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return redirect("order")
        order.status = status
        order.save()
        messages.success(request, "Order status updated successfully.")

        return redirect("order")

    return redirect("admin")

def cancel_order(request):
    order_id = request.POST.get('order_id')

    try:
        order = Order.objects.get(id=order_id)
        user=order.user
        try:
            wallets = Wallet.objects.get(user=user)
        except Wallet.DoesNotExist:
            wallets = Wallet.objects.create(user=user)

        if order.status in ['pending', 'processing']:
            order.status = 'cancelled'
            order.save()
            if order.payment_type != 'cod':
             wallets.amount+=int(order.amount)
             wallets.save()
             messages.success(request, f"Order #{order_id} has been cancelled.")
        else:
            messages.error(request, f"Order #{order_id} cannot be cancelled.")

    except Order.DoesNotExist:
        messages.error(request, f"Order #{order_id} not found.")

    return redirect('order')

def return_order(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        order_item_id = request.POST.get('order_item_id')

        try:
            order_item = OrderItem.objects.get(order_id=order_id)
            order = order_item .order
            user = request.user

            try:
                wallets = Wallet.objects.get(user=user)
            except Wallet.DoesNotExist:
                wallets = Wallet.objects.create(user=user)

            if order.status in ['delivered']:
                order.status = 'returned'
                order.save()
                if order.payment_type == 'cod' or order.payment_type == 'razorpay':
                  wallets.amount += int(order.amount)
                  wallets.save()

                messages.success(request, f"{order.id} has been returned.Piad Amount Refunded To Wallet")
            else:
                messages.error(request, f"Order #{order.id} cannot be returned.")

        except OrderItem.DoesNotExist:
            messages.error(request, f"Order Item #{order_item_id} not found.")
        except Order.DoesNotExist:
            messages.error(request, f"Order #{order_id} not found.")

    return redirect('my_orders')

def report_generator(request, orders):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    story = []

    data = [["Order ID", "User Name", "Total Quantity", "Product IDs", "Product Names", "Amount"]]

    for order in orders:
        # Retrieve order items associated with the current order
        order_items = OrderItem.objects.filter(order=order)
        total_quantity = sum(item.quantity for item in order_items)

        if order_items.exists():
            product_ids = ", ".join([str(item.product.id) for item in order_items])
            product_names = ", ".join([str(item.product.product_name) for item in order_items])
        else:
            product_ids = "N/A"
            product_names = "N/A"

        data.append([order.id, order.user.username,total_quantity, product_ids, product_names, order.amount])

    # Set column widths for six columns
    col_widths = [1.5 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch]
    table = Table(data, colWidths=col_widths)

    # Style the table
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    table.setStyle(table_style)
    story.append(table)
    doc.build(story)
    buf.seek(0)
    return FileResponse(buf, as_attachment=True, filename='orders_report.pdf')

def report_pdf_order(request):
    orders = Order.objects.all().order_by("-id")

    if request.method == 'POST':

        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        try:
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
        except ValueError:
            return HttpResponse('Invalid date format.')
        orders = Order.objects.filter(date__range=[from_date, to_date]).order_by('-id')
        return report_generator(request, orders)

    return render(request,'hello.html',context={'orders': orders})
