from django import forms
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'})
    )
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'})
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'})
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'})
    )

    class Meta:
        model = UserProfile
        fields = ['phone']   # only phone is from UserProfile

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        if commit:
            user.save()
            profile.save()
        return profile
    class PaymentForm(forms.Form):
        pass

    PAYMENT_CHOICES = [
        ('upi', 'UPI'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('wallet', 'Wallet (Paytm, PhonePe, etc.)'),
        ('cod', 'Cash on Delivery'),
    ]

    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        widget=forms.RadioSelect,
        label="Select Payment Method"
    )

    # For UPI
    upi_id = forms.CharField(required=False, max_length=50)

    # For Card
    card_number = forms.CharField(required=False, max_length=16)
    expiry_date = forms.CharField(required=False, max_length=5, help_text="MM/YY")
    cvv = forms.CharField(required=False, max_length=3)

    # For Wallet
    wallet_number = forms.CharField(required=False, max_length=15)