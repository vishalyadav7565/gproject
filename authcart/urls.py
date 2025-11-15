from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('activate/<uidb64>/<token>/', views.ActivateAccount.as_view(), name='activate'),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("reset/<uidb64>/<token>/", views.reset_password, name="reset_password"),
   
]

