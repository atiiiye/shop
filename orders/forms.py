from django import forms


class CartAddForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, max_value=9)


class DiscountApplyForm(forms.Form):
    code=forms.CharField(label="Discount code" , widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "Enter your discount code"}))