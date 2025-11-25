from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<str:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('clear-from-cart/<str:product_id>/', views.clear_from_cart, name='clear_from_cart'),
    path('clear-cart/', views.clear_cart, name='clear_cart'),
    path('update-cart/<str:product_id>/<str:action>/', views.update_cart, name='update_cart'),


    # Checkout flow
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/address/', views.address_page, name='address_page'),
    path('checkout/payment/', views.payment_page, name='payment_page'),
    path('checkout/confirmation/', views.order_confirmation, name='order_confirmation'),

    path('products/', views.product_list, name='product_list'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path("profile/", views.profile_view, name="profile"),
    path("upload-profile-image/", views.upload_profile_image, name="upload_profile_image"),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
    path('orders/', views.orders, name='orders'), 
    path('orders/<int:order_id>/track/', views.track_order, name='track_order'),
    path("orders/<int:order_id>/track/", views.track_order, name="track_order"),
path("orders/<int:order_id>/track/api/", views.track_order_api, name="track_order_api"),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
     path("search/", views.search_products, name="search_products"),
    path('search/', views.product_list, name='search'),
      path("category/<int:category_id>/", views.products_by_category, name="products_by_category"),
    path("subcategory/<int:subcategory_id>/", views.products_by_subcategory, name="products_by_subcategory"),
]