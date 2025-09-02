from math import ceil
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.template.loader import render_to_string
from django.db.models import Q

# Import models
from .models import Product, Contact, Order, UserProfile, Review, Banner, Category, SubCategory
from .forms import UserProfileForm


# -------------------- HOME PAGE --------------------
def index(request):
    allProds = []

    # Only get categories that have products
    categories = Category.objects.filter(product__isnull=False).distinct()

    for cat in categories:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = ceil(n / 4)
        allProds.append([prod, range(1, nSlides + 1), nSlides, cat])

    cart_count = sum(item["quantity"] for item in request.session.get("cart", {}).values())
    return render(request, 'index.html', {'allProds': allProds, 'cart_count': cart_count})


# -------------------- BANNERS --------------------
def home(request):
    banners = Banner.objects.filter(is_active=True).order_by('-created_at')
    cart_count = sum(item["quantity"] for item in request.session.get("cart", {}).values())
    return render(request, 'home.html', {'banners': banners, 'cart_count': cart_count})


# -------------------- CART FUNCTIONS --------------------
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    color_id = request.GET.get("color") or request.POST.get("color")

    cart = request.session.get("cart", {})
    key = f"{product_id}-{color_id}" if color_id else str(product_id)

    if key in cart:
        cart[key]["quantity"] += 1
    else:
        cart[key] = {
            "product_id": product.id,
            "name": product.name,
            "price": str(product.price),
            "quantity": 1,
            "color": color_id,
        }

    request.session["cart"] = cart
    return JsonResponse({
        "qty": cart[key]["quantity"],
        "cart_count": sum(item["quantity"] for item in cart.values())
    })


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    pid = str(product_id)
    if pid in cart:
        if cart[pid]["quantity"] > 1:
            cart[pid]["quantity"] -= 1
        else:
            del cart[pid]
    request.session['cart'] = cart
    request.session.modified = True
    return JsonResponse({
        'cart_count': sum(item["quantity"] for item in cart.values()),
        'qty': cart.get(pid, {}).get("quantity", 0)
    })


def clear_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart.pop(str(product_id), None)
    request.session['cart'] = cart
    request.session.modified = True
    return JsonResponse({'cart_count': sum(item["quantity"] for item in cart.values())})


def clear_cart(request):
    request.session['cart'] = {}
    request.session.modified = True
    return redirect('checkout')


def update_cart(request, product_id, action):
    cart = request.session.get('cart', {})
    pid = str(product_id)
    if pid not in cart:
        return redirect('checkout')

    if action == 'increase':
        cart[pid]["quantity"] += 1
    elif action == 'decrease':
        if cart[pid]["quantity"] > 1:
            cart[pid]["quantity"] -= 1
        else:
            cart.pop(pid, None)
    elif action == 'remove':
        cart.pop(pid, None)

    request.session['cart'] = cart
    request.session.modified = True
    return redirect('checkout')


# -------------------- ADDRESS PAGE --------------------
@login_required
def address_page(request):
    cart = request.session.get("cart", {})
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect("index")

    cart_items = []
    total_price = 0
    for key, item in cart.items():
        product = Product.objects.get(id=item["product_id"])
        qty = item["quantity"]
        subtotal = product.price * qty
        cart_items.append({
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "quantity": qty,
            "subtotal": subtotal,
            "image": product.image,
            "color": item.get("color"),
        })
        total_price += subtotal

    if request.method == "POST":
        request.session["full_name"] = request.POST.get("full_name")
        request.session["phone"] = request.POST.get("phone")
        request.session["address_line"] = request.POST.get("address_line")
        request.session["city"] = request.POST.get("city")
        request.session["state"] = request.POST.get("state")
        request.session["pincode"] = request.POST.get("pincode")
        return redirect("payment_page")

    return render(request, "address.html", {"cart_items": cart_items, "total_price": total_price})


# -------------------- PAYMENT PAGE --------------------
@login_required
def payment_page(request):
    cart = request.session.get("cart", {})
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('index')

    total_price = 0
    for key, item in cart.items():
        product = Product.objects.get(id=item["product_id"])
        qty = item["quantity"]
        total_price += product.price * qty

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        request.session['payment_method'] = payment_method
        return redirect('order_confirmation')

    return render(request, 'payment.html', {'total_price': total_price})


# -------------------- CHECKOUT PAGE --------------------
@login_required
def checkout(request):
    cart = request.session.get("cart", {})
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('index')

    cart_items = []
    total_price = 0
    for key, item in cart.items():
        product = Product.objects.get(id=item["product_id"])
        qty = item["quantity"]
        subtotal = product.price * qty
        cart_items.append({
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "quantity": qty,
            "subtotal": subtotal,
            "image": product.image,
            "color": item.get("color"),
        })
        total_price += subtotal

    return render(request, "checkout.html", {"cart_items": cart_items, "total_price": total_price})


# -------------------- PRODUCT DETAIL & REVIEW --------------------
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all()

    if request.method == "POST" and request.user.is_authenticated:
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")
        image = request.FILES.get("image")
        video = request.FILES.get("video")

        Review.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            comment=comment,
            image=image,
            video=video,
        )
        return redirect("product_detail", product_id=product.id)

    return render(request, "product_detail.html", {
        "product": product,
        "reviews": reviews,
        "average_rating": product.average_rating(),
    })


# -------------------- ORDER FUNCTIONS --------------------
@login_required
def order_confirmation(request):
    cart = request.session.get("cart", {})
    if not cart:
        return redirect('index')

    full_name = request.session.get('full_name')
    phone = request.session.get('phone')
    address = f"{request.session.get('address_line')}, {request.session.get('city')}, {request.session.get('state')} - {request.session.get('pincode')}"
    payment_method = request.session.get('payment_method') or 'cod'

    for key, item in cart.items():
        product = Product.objects.get(id=item["product_id"])
        qty = item["quantity"]
        Order.objects.create(
            user=request.user,
            product=product,
            quantity=qty,
            total_price=product.price * qty,
            address=address,
            phone=phone,
            payment_status='Completed' if payment_method != 'cod' else 'Pending',
            status='Pending',
            payment_method=payment_method,
        )

    # Clear session
    keys_to_clear = ['cart', 'full_name', 'phone', 'address_line', 'city', 'state', 'pincode', 'payment_method']
    for key in keys_to_clear:
        request.session.pop(key, None)

    return render(request, 'confirmation.html', {
        "full_name": full_name,
        "address": address,
        "phone": phone,
        "payment_method": payment_method,
    })


@login_required
def orders(request):
    user_orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, "orders.html", {"orders": user_orders})


@login_required
def track_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "track_order.html", {"order": order})


def track_order_api(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    timeline_html = render_to_string("order_timeline.html", {"order": order})
    return JsonResponse({
        "status": order.status,
        "payment_status": order.payment_status,
        "timeline_html": timeline_html
    })


# -------------------- PROFILE --------------------
@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, "profile.html", {"profile": profile})


@login_required
def edit_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            request.user.email = request.POST.get("email")
            request.user.first_name = request.POST.get("first_name", "")
            request.user.last_name = request.POST.get("last_name", "")
            request.user.save()
            return redirect("profile")
    else:
        form = UserProfileForm(instance=profile)
    return render(request, "edit_profile.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('index')


# -------------------- OTHER PAGES --------------------
def product_list(request):
    products = Product.objects.all()
    cart_count = sum(item["quantity"] for item in request.session.get("cart", {}).values())
    return render(request, 'product_list.html', {'products': products, 'cart_count': cart_count})


def about(request):
    cart_count = sum(item["quantity"] for item in request.session.get("cart", {}).values())
    return render(request, 'about.html', {'cart_count': cart_count})


def contact(request):
    if request.method == "POST":
        Contact.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            message=request.POST.get('message')
        )
        messages.success(request, "Your message has been sent successfully.")
        return redirect('contact')
    cart_count = sum(item["quantity"] for item in request.session.get("cart", {}).values())
    return render(request, 'contact.html', {'cart_count': cart_count})


# -------------------- SEARCH & FILTER --------------------
def search_products(request):
    query = request.GET.get("q", "")
    categories = request.GET.getlist("category")
    subcategories = request.GET.getlist("subcategory")
    brands = request.GET.getlist("brand")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    rating_filter = request.GET.get("rating")
    sort = request.GET.get("sort")

    products = Product.objects.filter(is_active=True)

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(subcategory__name__icontains=query) |
            Q(brand__icontains=query)
        )
    if categories:
        products = products.filter(category__id__in=categories)
    if subcategories:
        products = products.filter(subcategory__id__in=subcategories)
    if brands:
        products = products.filter(brand__in=brands)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    if rating_filter:
        products = products.filter(rating__gte=rating_filter)

    if sort == "low-high":
        products = products.order_by("price")
    elif sort == "high-low":
        products = products.order_by("-price")
    elif sort == "newest":
        products = products.order_by("-created_at")

    all_categories = Category.objects.all()
    all_brands = Product.objects.values_list("brand", flat=True).distinct().exclude(brand__isnull=True).exclude(brand__exact="")

    return render(request, "search_results.html", {
        "products": products,
        "categories": all_categories,
        "brands": all_brands,
        "query": query,
        "selected_categories": categories,
        "selected_subcategories": subcategories,
        "selected_brands": brands,
        "min_price": min_price,
        "max_price": max_price,
        "rating_filter": rating_filter,
        "sort": sort
    })
