from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User, Product


class RegisterForm(UserCreationForm):

    email = forms.EmailField()

    phone = forms.CharField(max_length=15)

    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        widget=forms.Select()
    )

    class Meta:

        model = User

        fields = [
            'username',
            'email',
            'phone',
            'role',
            'password1',
            'password2'
        ]


class ProductForm(forms.ModelForm):

    class Meta:

        model = Product

        fields = [
            'name',
            'description',
            'price',
            'image',
            'stock'
        ]

        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }