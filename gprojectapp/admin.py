from django.contrib import admin
from django.utils.html import format_html
from django.shortcuts import redirect
from django.urls import path, reverse
from .models import (
    Contact, Product, Order, UserProfile, Review, Banner,
    Category, SubCategory, Specification, Color, MegaMenu
)


# -------------------------
# Branding
# -------------------------
admin.site.site_header = "Shrimati Admin Panel"
admin.site.site_title = "Shrimati Admin"
admin.site.index_title = "Welcome to Shrimati Administration"


# -------------------------
# SubCategory Inline (inside Category)
# -------------------------
class SubCategoryInline(admin.TabularInline):
    model = SubCategory
    extra = 1
    show_change_link = True


# -------------------------
# Category Admin
# -------------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "show_image")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    inlines = [SubCategoryInline]

    def image_preview(self, obj):
        if obj.image:
            return f"<img src='{obj.image.url}' width='50' height='50' style='border-radius:50%;'/>"
        return "No Image"
    image_preview.allow_tags = True
    image_preview.short_description = "Preview"
    def show_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width:50px;height:50px;object-fit:cover;border-radius:50%;" />', obj.image.url)
        return "❌ No Image"


# -------------------------
# SubCategory Admin
# -------------------------
@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "slug")
    prepopulated_fields = {"slug": ("name",)}
    list_filter = ("category",)
    search_fields = ("name", "category__name")


# -------------------------
# Product Admin
# -------------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "category", "subcategory", "show_image")
    list_filter = ("category", "subcategory", "price")
    search_fields = ("name", "category__name", "subcategory__name")
    list_editable = ("price",)
    ordering = ("-id",)

    def show_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width:50px;height:50px;object-fit:cover;" />', obj.image.url)
        return "❌ No Image"
    show_image.short_description = "Preview"


# -------------------------
# Order Admin (with action buttons)
# -------------------------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id", "user", "product", "quantity", "total_price",
        "status", "payment_status", "payment_method", "phone", "address",
        "order_date", "action_buttons"
    )
    list_filter = ("status", "payment_status", "payment_method", "order_date")
    search_fields = ("user__username", "product__name", "phone", "address", "id")
    ordering = ("-order_date",)

    readonly_fields = (
        "pending_at", "processing_at", "dispatched_at",
        "shipped_at", "delivered_at", "cancelled_at"
    )

    fieldsets = (
        ("Customer Info", {"fields": ("user", "phone", "address")}),
        ("Order Details", {"fields": ("product", "quantity", "total_price", "payment_method")}),
        ("Status & Payment", {"fields": ("status", "payment_status")}),
        ("Tracking", {"fields": ("courier_name", "expected_delivery")}),
        ("Timeline (Auto)", {"fields": (
            "pending_at", "processing_at", "dispatched_at",
            "shipped_at", "delivered_at", "cancelled_at"
        )}),
    )

    # Inline buttons depending on current status
    def action_buttons(self, obj):
        buttons = []
        if obj.status == "Pending":
            buttons.append(f'<a class="button button-processing" href="mark-processing/{obj.id}/">⚙️ Process</a>')
        if obj.status == "Processing":
            buttons.append(f'<a class="button button-dispatch" href="mark-dispatched/{obj.id}/">📦 Dispatch</a>')
        if obj.status == "Dispatched":
            buttons.append(f'<a class="button button-ship" href="mark-shipped/{obj.id}/">🚚 Ship</a>')
        if obj.status == "Shipped":
            buttons.append(f'<a class="button button-deliver" href="mark-delivered/{obj.id}/">✅ Deliver</a>')
        if obj.status not in ["Delivered", "Cancelled"]:
            buttons.append(f'<a class="button button-cancel" href="mark-cancelled/{obj.id}/">❌ Cancel</a>')
        return format_html(" &nbsp; ".join(buttons))
    action_buttons.short_description = "Actions"

    # Custom URLs for buttons
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("mark-processing/<int:order_id>/", self.admin_site.admin_view(self.mark_processing), name="mark_processing"),
            path("mark-dispatched/<int:order_id>/", self.admin_site.admin_view(self.mark_dispatched), name="mark_dispatched"),
            path("mark-shipped/<int:order_id>/", self.admin_site.admin_view(self.mark_shipped), name="mark_shipped"),
            path("mark-delivered/<int:order_id>/", self.admin_site.admin_view(self.mark_delivered), name="mark_delivered"),
            path("mark-cancelled/<int:order_id>/", self.admin_site.admin_view(self.mark_cancelled), name="mark_cancelled"),
        ]
        return custom_urls + urls

    # Actions
    def mark_processing(self, request, order_id):
        Order.objects.filter(pk=order_id).update(status="Processing")
        self.message_user(request, f"Order {order_id} marked as Processing ⚙️")
        return redirect(reverse("admin:gprojectapp_order_changelist"))

    def mark_dispatched(self, request, order_id):
        Order.objects.filter(pk=order_id).update(status="Dispatched")
        self.message_user(request, f"Order {order_id} marked as Dispatched 📦")
        return redirect(reverse("admin:gprojectapp_order_changelist"))

    def mark_shipped(self, request, order_id):
        Order.objects.filter(pk=order_id).update(status="Shipped")
        self.message_user(request, f"Order {order_id} marked as Shipped 🚚")
        return redirect(reverse("admin:gprojectapp_order_changelist"))

    def mark_delivered(self, request, order_id):
        Order.objects.filter(pk=order_id).update(status="Delivered")
        self.message_user(request, f"Order {order_id} marked as Delivered ✅")
        return redirect(reverse("admin:gprojectapp_order_changelist"))

    def mark_cancelled(self, request, order_id):
        Order.objects.filter(pk=order_id).update(status="Cancelled")
        self.message_user(request, f"Order {order_id} marked as Cancelled ❌")
        return redirect(reverse("admin:gprojectapp_order_changelist"))

    class Media:
        css = {"all": ("admin/css/admin.css",)}  # ✅ use your custom file


# -------------------------
# UserProfile
# -------------------------
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "phone")
    search_fields = ("user__username", "full_name", "phone")


# -------------------------
# Review
# -------------------------
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "created_at")
    list_filter = ("rating",)
    search_fields = ("product__name", "user__username")


# -------------------------
# Banner
# -------------------------
@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("title", "subtitle", "is_active", "display_order", "created_at")
    list_filter = ("is_active",)
    search_fields = ("title", "subtitle")
    list_editable = ("is_active", "display_order")


# -------------------------
# Contact
# -------------------------
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "message")
    search_fields = ("name", "email", "phone")

    
@admin.register(MegaMenu)
class MegaMenuAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category", "is_active")
    list_filter = ("is_active", "category")
    search_fields = ("title", "category__name")
    list_editable = ("is_active",)
