from django import forms


class CheckoutForm(forms.Form):

    address = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Enter delivery address'
        })
    )

    phone = forms.CharField(max_length=15)

    payment_method = forms.ChoiceField(
        choices=[
            ('COD', 'Cash on Delivery')
        ]
    )