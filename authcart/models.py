from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, null=True)
    profile_image = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    full_name = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username
    

def cart_count(request):
    cart = request.session.get('cart', {})
    total_items = sum(cart.values()) if cart else 0
    return {'cart_count': total_items}
