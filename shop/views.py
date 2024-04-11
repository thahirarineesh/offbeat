from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator
from django.http import Http404, HttpResponseRedirect
from django.views.decorators.cache import cache_control, never_cache

from cart.models import Coupon
from .forms import AddressForm
from .models import Product ,Images,Customer,Address
from .forms import AddressForm, ChangePasswordForm
from django.shortcuts import render, redirect
from django.db.models import Q

from django.contrib import messages, auth


# Create your views here.
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def productdetails(request, product_id=None):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        raise Http404("Product does not exist")
    images = Images.objects.filter(product=product)
    context = {
        "product": product,
        "images": images,
    }
    return render(request, "shop/product_detail.html", context)


def Profile(request):

    if request.method == 'POST':
        form =AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('profile')
    form = AddressForm()
    addresses=Address.objects.filter(user=request.user,is_deleted=False)
    context = {
        'form':form,
        'addresses':addresses,
    }
    return render(request, 'shop/profile.html',context)

def edit_profile(request):
    try:
        customer = Customer.objects.get(id=request.user.id)
    except Customer.DoesNotExist:
        return redirect("home")

    if request.method == "POST":
        customer.username = request.POST.get("username")
        customer.email = request.POST.get("email")
        customer.number = request.POST.get("number")
        password = request.POST.get("password1")
        profile_photo = request.FILES.get("image")
        address_id = request.POST.get("id")

        if profile_photo:
            customer.profile_photo.save(profile_photo.name, profile_photo, save=True)

        if password:
            customer.set_password(password)
        customer.save()
        messages.success(request, "Updated successfully")
        return redirect("edit_profile")

    addresses = Address.objects.filter(user=request.user).order_by("id")

    context = {
        "customer": customer,
        "addresses": addresses,
    }

    return render(request, "shop/profile.html", context)


def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Update the session to prevent the user from being logged out
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')  # Replace with the actual URL for the user's profile
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = ChangePasswordForm(request.user)

    return render(request, 'change_password.html', {'form': form})

def edit_address(request, address_id):
    try:
        address = Address.objects.get(id=address_id)
    except Address.DoesNotExist:
        messages.error(request, "Address not found")
        return redirect("profile")

    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        number = request.POST.get("number")
        address1 = request.POST.get("address1")
        address2 = request.POST.get("address2")
        country = request.POST.get("country")
        city = request.POST.get("city")
        state = request.POST.get("state")
        zip_code = request.POST.get("zip_code")

        address.first_name = first_name
        address.last_name = last_name
        address.email = email
        address.number = number
        address.address1 = address1
        address.address2 = address2
        address.country = country
        address.city = city
        address.state = state
        address.zip_code = zip_code
        address.save()
        messages.success(request, "Address updated successfully")

    return redirect("profile")


def delete_address(request, address_id):
    try:
        address = Address.objects.get(id=address_id)
    except Address.DoesNotExist:
        return redirect("profile")

    address.is_deleted = True
    address.save()

    messages.success(request, "Address deleted successfully.")
    return redirect("profile")

def search(request):
    query = request.GET.get("q")

    if query:
        results = Product.objects.filter(
            Q(product_name__icontains=query) |
            Q(description__icontains=query)
        ).distinct()
    else:
        results = []

    paginator = Paginator(results, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "query": query,
    }

    return render(request, "search.html", context)



