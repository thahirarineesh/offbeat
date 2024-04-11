# Create your views here.
import uuid
from django.db.models import F
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.cache import cache_control, never_cache
from .models import Customer, Product, Category
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
import secrets
import smtplib
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login


def home(request):
    return render(request,'home.html')
def contact(request):
    return render(request,'contact.html')

@never_cache
def signupPage(request):
    if "email" in request.session:
        return redirect("home")

    if request.method == "POST":
        email = request.POST.get("email")
        username = request.POST.get("username")
        number = request.POST.get("number")
        pass1 = request.POST.get("password1")
        pass2 = request.POST.get("password2")

        if not email or not username or not pass1 or not pass2:
            messages.error(request, "Please input all the details.")
            return redirect("signup")

        if pass1 != pass2:
            messages.error(request, "Passwords do not match.")
            return redirect("signup")

        if not validate_email(email):
            messages.error(request, "Please enter a valid email address.")
            return redirect("signup")

        if Customer.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect("signup")

        if Customer.objects.filter(email=email).exists():
            messages.error(request, "Email already exist")
            return redirect("signup")

        message = generate_otp()
        sender_email = "thahiravh001@gmail.com"
        receiver_mail = email
        password = "wdxh avzi qazw iled"

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_mail, message)

        except smtplib.SMTPAuthenticationError:
            messages.error(
                request,
                "Failed to send OTP email. Please check your email configuration.",
            )
            return redirect("signup")

        user = Customer.objects.create_user(
            username=username,
            password=pass1,
            email=email,
            number=number,
        )
        user.save()
        request.session["email"] = email
        request.session["otp"] = message
        messages.success(request, "OTP is sent to your email")
        return redirect("verify_signup")

    return render(request, "user/signup.html")


def generate_otp(length=6):
    return "".join(secrets.choice("0123456789") for _ in range(length))


def validate_email(email):
    return "@" in email and "." in email

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def verify_signup(request):
    context = {"messages": messages.get_messages(request)}
    if request.method == "POST":
        user_email = request.session.get("email")
        user_otp = request.session.get("otp")
        entered_otp = request.POST.get("otp")

        if not user_email or not user_otp:
            messages.error(request, "Session expired. Please try again.")
            return redirect("signup")

        if entered_otp == user_otp:
            user = Customer.objects.get(email=user_email)
            user.is_verified = True
            user.save()
            del request.session["email"]
            del request.session["otp"]

            login(request, user)
            # messages.success(request, "Signup successful!")
            return redirect("home")
        else:
            messages.info(request, "Invalid OTP")
            return redirect("verify_signup")

    return render(request, "user/verify_otp.html", context)

def loginPage(request):
    context={"messages":messages.get_messages(request)}
    if "email" and "otp" in request.session:
        request.session.flush()
        return redirect("login")

    if "email" in request.session:
        return redirect("home")
    if "admin" in request.session:
        return redirect("admin")
    else:
      if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email or not password:
            messages.error(request, "Please enter both username and password.")
            return redirect("login")

        try:
            usera = Customer.objects.get(email=email)
        except Customer.DoesNotExist:
            messages.error(request, "User with this email does not exist.")
            return redirect("login")

        if not usera.is_active:
            messages.error(request, "You can't log in. Your account is blocked.")
            return redirect("login")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            request.session["email"] = email
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("login")

      return render(request, "user/login.html",context)


def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            customer = Customer.objects.get(email=email)

            if customer.email == email:
                message = generate_otp()
                sender_email = "thahiravh001@gmail.com"
                receiver_mail = email
                password = "wdxh avzi qazw iled"

                try:
                    with smtplib.SMTP("smtp.gmail.com", 587) as server:
                        server.starttls()
                        server.login(sender_email, password)
                        server.sendmail(sender_email, receiver_mail, message)

                except smtplib.SMTPAuthenticationError:
                    messages.error(
                        request,
                        "Failed to send OTP email. Please check your email configuration.",
                    )
                    return redirect("signup")

                request.session["email"] = email
                request.session["otp"] = message
                messages.success(request, "OTP is sent to your email")
                return redirect("reset_password")

        except Customer.DoesNotExist:
            messages.info(request, "Email is not valid")
            return redirect("login")
    else:
        return redirect("login")


def generate_otp(length=6):
    return "".join(secrets.choice("0123456789") for i in range(length))

def reset_password(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        stored_otp = request.session.get("otp")
        if entered_otp == stored_otp:
            if new_password == confirm_password:
                email = request.session.get("email")
                try:
                    customer = Customer.objects.get(email=email)
                    customer.set_password(new_password)
                    customer.save()
                    del request.session["email"]
                    del request.session["otp"]
                    messages.success(
                        request,
                        "Password reset successful. Please login with your new password.",
                    )
                    return redirect("login")
                except Customer.DoesNotExist:
                    messages.error(
                        request, "Failed to reset password. Please try again later."
                    )
                    return redirect("login")
            else:
                messages.error(
                    request, "New password and confirm password do not match."
                )
                return redirect("reset_password")
        else:
            messages.error(request, "Invalid OTP. Please enter the correct OTP.")
            return redirect("reset_password")
    else:
        return render(request, "user/forgot_password.html")


def logout_view(request):
    logout(request)
    return redirect('home')

@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def customers(request):
    if "admin" in request.session:
        customer_list = Customer.objects.filter(is_staff=False).order_by("id")
        paginator = Paginator(customer_list, 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        context = { "page_obj": page_obj, }
        return render(request, "customer.html", context)
    else:
        return redirect("admin")

def unblock_customer(request, customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
    except ObjectDoesNotExist:
        return redirect("customer")

    customer.is_active = not customer.is_active
    customer.save()

    return redirect("customer")

def block_customer(request, customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return redirect("customer")
    customer.is_active = False
    customer.save()
    return redirect("customer")

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def category(request):
    if "admin" in request.session:
        categories = Category.objects.all().order_by("id")
        paginator = Paginator(categories, per_page=4)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        context = {
            "categories": page_obj,
        }
        return render(request, "category/category.html", context)
    else:
        return redirect("admin")


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def add_category(request):
    if "admin" in request.session:
        if request.method == "POST":
            category_name = request.POST["category_name"]
            description = request.POST["description"]
            image = request.FILES.get("image")

            # Check if the category_name is not just whitespace
            if not category_name.strip():
                error_message = "Category name cannot be empty or contain only spaces."
                return render(request, "category/add_category.html", {"error_message": error_message})

            try:
                # Attempt to create a new category
                category = Category.objects.create(
                    category_name=category_name,
                    description=description,
                    image=image,
                )
                return redirect("category")
            except IntegrityError:
                error_message = "A category with the same name already exists. Please choose a different name."
                return render(request, "category/add_category.html", {"error_message": error_message})

        return render(request, "category/add_category.html")
    else:
        return redirect("admin")


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def editcategory(request, category_id):
    if "admin" in request.session:
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return render(request, "category_not_found.html")

        context = {"category": category}
        return render(request, "category/edit_category.html", context)
    else:
        return redirect("admin")


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def update_category(request, id):
    try:
        category = Category.objects.get(id=id)
    except Category.DoesNotExist:
        return render(request, "category_not_found.html")

    if request.method == "POST":
        category_name = request.POST.get("category_name")
        if category_name:
            category.category_name = category_name
            category.description = request.POST.get("description")
            image = request.FILES.get("image")

        if image:
            category.image = image
        category.save()
        return redirect("category")

    context = {"category": category}
    return render(request, "category/edit_category.html", context)


def delete_category(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        return render(request, "category_not_found.html")

    category.delete()

    categories = Category.objects.all()
    context = {"categories": categories}

    return redirect("category")

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def product(request):
    if "admin" in request.session:
        products = Product.objects.all().order_by("id")

        paginator = Paginator(products, 3)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context = {
            "page_obj": page_obj,
        }
        return render(request, "product/product.html", context)
    else:
        return redirect("admin")

def add_product(request):
    if "admin" in request.session:
        if request.method == "POST":
            product_name = request.POST.get("product_name")
            description = request.POST.get("description")
            category_name = request.POST.get("category")
            category = get_object_or_404(Category, category_name=category_name)
            stock = request.POST.get("stock")
            price = request.POST.get("price")
            image = request.FILES.get("image")
            if not (
                    product_name.strip()  # Check if the stripped value is not empty
                    and description
                    and category_name
                    and category
                    and price
                    and image
                    and stock
            ):
                categories = Category.objects.all()
                context = {"categories": categories}
                return render(request, "product/add_product.html", context)
            product = Product()
            product.product_name = product_name
            product.description = description
            product.category = category
            product.stock = stock
            product.price = price
            product.image = image
            product.available = True
            try:
               product.save()
               return redirect("products")
            except IntegrityError:
                error_message = "A product with the same name already exists. Please choose a different name."
                categories = Category.objects.all()
                context = {"categories": categories, "error_message": error_message}
                return render(request, "product/add_product.html", context)
        categories = Category.objects.all()
        context = {"categories": categories}
        return render(request, "product/add_product.html", context)
    else:
        return redirect("admin")


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def editproduct(request, product_id):
    if "admin" in request.session:
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return render(request, "product_not_found.html")

        categories = Category.objects.all()
        context = {
            "product": product,
            "categories": categories,
        }

        return render(request, "product/edit_product.html", context)
    else:
        return redirect("admin")


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def update(request, id):
    product = Product.objects.get(id=id)
    if request.method == "POST":
        product.product_name = request.POST.get("product_name")
        product.description = request.POST.get("description")
        category_name = request.POST.get("category")
        category = Category.objects.get(category_name=category_name)
        product.category = category
        product.stock = request.POST.get("stock")
        product.price = request.POST.get("price")
        product.product_offer = request.POST.get("offer")
        image = request.FILES.get("image")
        images = request.FILES.getlist("mulimage")

        if image:
            product.image = image
        product.save()

        return redirect("products")
    else:
        context = {"product": product}
    return render(request, "product/products.html", context)

def delete_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return render(request, "product_not_found.html")

    product.delete()

    products = Product.objects.all()
    context = {"products": products}

    return redirect("products")


def product_list(request):
    results = Product.objects.filter(deleted=False).order_by("id")

    total_product_count = Product.objects.count()
    selected_categories = request.GET.getlist("category")
    if selected_categories:
        results = results.filter(category__category_name__in=selected_categories)

    sort_option = request.GET.get("sort")
    if sort_option == "high":
        results = results.order_by(F("price").desc())
    elif sort_option == "all":
        results = results.order_by("price")

    sort_alpha_option = request.GET.get("sort_alpha")
    if sort_alpha_option == "az":
        results = results.order_by("product_name")
    elif sort_alpha_option == "za":
        results = results.order_by("-product_name")

    paginator = Paginator(results,6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()


    context = {
        "page_obj": page_obj,
        "selected_categories": selected_categories,
        "total_product_count": total_product_count,
        "categories": categories,
        "results":results,
    }

    device_id = request.COOKIES.get("device_id")
    if not device_id:
        device_id = uuid.uuid4()
        response = render(request, "shop/product_list.html", context)
        response.set_cookie("device_id", device_id)
        return response
    return render(request, "shop/product_list.html", context)




