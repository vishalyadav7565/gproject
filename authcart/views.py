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
from .token_generator import email_token_generator
from .models import Profile


# ---------------- LOGIN ----------------
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User

def login_view(request):
    if request.method == "POST":
        username_or_email = request.POST.get("username").strip()
        password = request.POST.get("password").strip()

        # Allow login using email
        if "@" in username_or_email:
            try:
                user_obj = User.objects.get(email=username_or_email)
                username = user_obj.username
            except User.DoesNotExist:
                messages.error(request, "No user found with this email.")
                return render(request, "authentication/login.html")
        else:
            username = username_or_email

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect("/")
            else:
                messages.warning(request, "Please verify your email before login.")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "authentication/login.html")





# ---------------- SIGNUP ----------------
def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        # Validation
        if not email or "@" not in email:
            messages.error(request, "Please enter a valid email.")
            return render(request, "authentication/signup.html")
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "authentication/signup.html")
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, "authentication/signup.html")
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, "authentication/signup.html")

        # Create inactive user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        user.is_active = False
        user.save()

        # Create profile
        Profile.objects.create(
            user=user,
            phone="",
            full_name=f"{first_name} {last_name}".strip()
        )

        # Generate activation link
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = email_token_generator.make_token(user)

        activation_link = request.build_absolute_uri(
            reverse("activate", kwargs={"uidb64": uidb64, "token": token})
        )

        # Send email
        subject = "Activate Your Account"
        message = (
            f"Hi {user.username},\n\n"
            f"Click the link below to activate your account:\n{activation_link}\n\n"
            f"If you didn't request this, ignore this email."
        )
        try:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
        except Exception as e:
            user.delete()  # Remove inactive user if email fails
            messages.error(request, "Error sending email. Try again later.")
            print("EMAIL ERROR:", e)
            return render(request, "authentication/signup.html")

        messages.success(request, "Account created! Check your email to activate.")
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
        except Exception:
            user = None

        if user is not None and email_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, "Your account has been activated. You can now login.")
            return redirect("login")

        messages.error(request, "Activation link is invalid or expired.")
        return redirect("login")



# ---------------- PASSWORD RESET EMAIL ----------------
def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "No account found with this email.")
            return render(request, "authentication/forgot_password.html")

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        reset_link = request.build_absolute_uri(
            reverse('reset_password', kwargs={'uidb64': uidb64, 'token': token})
        )

        send_mail(
            "Reset Your Password",
            f"Hi {user.username}, click to reset your password: {reset_link}",
            settings.EMAIL_HOST_USER,
            [email],
        )

        messages.success(request, "Password reset link sent! Check your email.")
        return redirect("login")

    return render(request, "authentication/forgot_password.html")

# ---------------- PASSWORD RESET CONFIRM ----------------
def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and default_token_generator.check_token(user, token):

        if request.method == "POST":
            password = request.POST.get("password1")
            confirm_password = request.POST.get("password2")

            if password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return render(request, "authentication/reset_password.html")

            user.set_password(password)
            user.save()
            messages.success(request, "Password updated successfully. You can now log in.")
            return redirect("login")

        return render(request, "authentication/reset_password.html")

    else:
        messages.error(request, "Invalid or expired link.")
        return redirect("forgot_password")
