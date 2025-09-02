# authcart/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.views import View
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_str, force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

# ---------------- LOGIN ----------------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:  # check activation
                login(request, user)
                return redirect('/')  
            else:
                messages.error(request, "Your account is not activated. Please check your email.")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "authentication/login.html")


# ---------------- SIGNUP ----------------
def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "authentication/signup.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, "authentication/signup.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, "authentication/signup.html")

        user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name)
        user.is_active = False  # Deactivate account till it is confirmed
        user.save()

        # Send activation email
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_link = request.build_absolute_uri(
            reverse('activate', kwargs={'uidb64': uidb64, 'token': token})
        )

        subject = "Activate your account"
        message = f"Hi {user.username},\n\nPlease click the link below to activate your account:\n{activation_link}\n\nThank you!"
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]

        send_mail(subject, message, from_email, recipient_list)

        messages.success(request, "Account created successfully! Please check your email to activate your account.")
        return redirect("login")

    return render(request, "authentication/signup.html")


# ---------------- LOGOUT ----------------
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return render(request, "authentication/logout.html")


# ---------------- ACTIVATE ACCOUNT ----------------
class ActivateAccount(View):
    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, "Your account has been activated successfully. You can now login.")
            return redirect("login")
        else:
            messages.error(request, "Activation link is invalid or expired.")
            return redirect("signup")
