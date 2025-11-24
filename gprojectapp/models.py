from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.exceptions import ValidationError
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile


# -------------------------
# Banner image validator
# -------------------------
def validate_banner_image(image):
    valid_mime_types = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp']
    file_mime_type = image.file.content_type
    if file_mime_type not in valid_mime_types:
        raise ValidationError('Unsupported file type. Only JPEG, PNG, and WEBP are allowed.')

    # Validate file size (max 2MB)
    max_size_mb = 5
    if image.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f'Image file too large ( > {max_size_mb}MB )')


# -------------------------
# Category & SubCategory
# -------------------------
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to="category_images/", blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, related_name="subcategories", on_delete=models.CASCADE)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = "SubCategories"
        ordering = ["name"]

    def __str__(self):
        return f"{self.category.name} -> {self.name}"



# -------------------------
# Contact model
# -------------------------
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    message = models.TextField()

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=50, unique=True)
    hex_code = models.CharField(max_length=7, blank=True, null=True, help_text="Optional: #RRGGBB")

    def __str__(self):
        return self.name

# -------------------------
# Product model
# -------------------------
class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="products/")
    description = models.TextField(blank=True, null=True)
    offer = models.CharField(max_length=255, blank=True, null=True)
    about = models.TextField(
        help_text="Enter each feature on a new line",
        blank=True
    )
    colors = models.ManyToManyField(Color, blank=True, related_name="products")
    brand = models.CharField(max_length=100, null=True, blank=True)

    # KEEP ONLY ONE
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum([r.rating for r in reviews]) / reviews.count(), 1)
        return 0

    def get_about_points(self):
        return [point.strip() for point in self.about.splitlines() if point.strip()]

class Specification(models.Model):
    product = models.ForeignKey(Product, related_name="specifications", on_delete=models.CASCADE)
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.key}: {self.value}"
# -------------------------
# Order model with payment
# -------------------------
class Order(models.Model):
    STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("Processing", "Processing"),
        ("Dispatched", "Dispatched"),
        ("Shipped", "Shipped"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
    )

    PAYMENT_STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("Completed", "Completed"),
    )

    PAYMENT_METHOD_CHOICES = (
        ('upi', 'UPI'),
        ('card', 'Credit/Debit Card'),
        ('wallet', 'Wallet'),
        ('cod', 'Cash on Delivery'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.FloatField()
    address = models.TextField()
    phone = models.CharField(max_length=15)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default="Pending")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="Pending")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cod')
    order_date = models.DateTimeField(auto_now_add=True)

    # Optional tracking fields
    courier_name = models.CharField(max_length=100, blank=True, null=True)
    expected_delivery = models.DateField(blank=True, null=True)

    # Timeline fields
    pending_at = models.DateTimeField(auto_now_add=True)
    processing_at = models.DateTimeField(blank=True, null=True)
    dispatched_at = models.DateTimeField(blank=True, null=True)
    shipped_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    # 👇 timeline auto-update
    def update_timeline(self):
        now = timezone.now()
        if self.status == "Processing" and not self.processing_at:
            self.processing_at = now
        elif self.status == "Dispatched" and not self.dispatched_at:
            self.dispatched_at = now
        elif self.status == "Shipped" and not self.shipped_at:
            self.shipped_at = now
        elif self.status == "Delivered" and not self.delivered_at:
            self.delivered_at = now
        elif self.status == "Cancelled" and not self.cancelled_at:
            self.cancelled_at = now

    def save(self, *args, **kwargs):
        # Before saving, auto-update timeline based on status
        self.update_timeline()
        super().save(*args, **kwargs)

# -------------------------
# UserProfile model
# -------------------------
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, null=True)
    full_name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()


# -------------------------
# Review model
# -------------------------
class Review(models.Model):
    product = models.ForeignKey(Product, related_name="reviews", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="reviews/images/", blank=True, null=True)
    video = models.FileField(upload_to="reviews/videos/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.rating}⭐"


# -------------------------
# Banner model
# -------------------------
class Banner(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True)
    subtitle = models.CharField(max_length=300, blank=True, null=True)
    image = models.ImageField(upload_to='banners/', validators=[validate_banner_image])
    link = models.URLField(blank=True, null=True)
    product = models.ForeignKey(Product, blank=True, null=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Banner"
        verbose_name_plural = "Banners"
        ordering = ['display_order', '-created_at']

    def __str__(self):
        return self.title or f"Banner {self.id}"

    def save(self, *args, **kwargs):
        if self.image:
            try:
                img = Image.open(self.image)

                # Convert PNG/WEBP to RGB
                if img.mode != "RGB":
                    img = img.convert("RGB")

                # Resize banner
                img = img.resize((1200, 400), Image.Resampling.LANCZOS)

                buffer = BytesIO()
                img.save(buffer, format="JPEG", quality=85)
                buffer.seek(0)

                # Save new file
                self.image = ContentFile(buffer.read(), name=f"banner_{self.pk or ''}.jpg")

            except Exception as e:
                print("Banner image compression failed:", e)

        super().save(*args, **kwargs)


class MegaMenu(models.Model):
    title = models.CharField(max_length=100)
    category = models.ForeignKey("Category", on_delete=models.CASCADE, related_name="megamenu")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Mega Menu"
        verbose_name_plural = "Mega Menus"

    def __str__(self):
        return f"{self.title} ({self.category.name})"
    
   