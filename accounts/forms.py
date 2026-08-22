from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django import forms
from .models import User


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='confirm password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email', 'phone_number', 'full_name']

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password1'] and cd['password2'] and cd['password1'] != cd['password2']:
            raise ValidationError("passwords don't match")
        return cd['password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password2'])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(help_text='you can change password using <a href="../password/">this form</a>')

    class Meta:
        model = User
        fields = ['email', 'phone_number', 'full_name', 'password', 'last_login']


class UserRegistrationForm(forms.Form):
    email = forms.EmailField(max_length=255, label="Email", widget=forms.EmailInput(
        attrs={"class": "form-control col-md-6 mt-1", "placeholder": "Enter your email"}),
                             error_messages={
                                 "required": "Please enter your email.",
                                 "invalid": "Please enter a valid email",
                                 "max_length": "Phone number cannot be longer than 255 characters",
                             })
    phone_number = forms.CharField(max_length=11, label="Phone number", widget=forms.TextInput(
        attrs={"class": "form-control col=md-6", "placeholder": "Enter your phone number"}),
                                   error_messages={
                                       "required": "Please enter your phone number",
                                       "invalid": "Please enter a valid phone number",
                                       "max_length": "Phone number cannot be longer than 11 characters",
                                   })
    full_name = forms.CharField(max_length=255, label="Full name", widget=forms.TextInput(
        attrs={"class": "form-control col-md-6", "placeholder": "Enter your fullname"}),
                                error_messages={
                                    "required": "Please enter your full name",
                                    "max_length": "Full name cannot be longer than 255 characters",
                                })
    password = forms.CharField(max_length=255, min_length=4, label="Password", widget=forms.PasswordInput(
        attrs={"class": "form-control col-md-6 mt-1", "placeholder": "Enter your password"}),
                               error_messages={
                                   "required": "Please enter your password",
                                   "max_length": "Password cannot be longer than 255 characters",
                                   "min_length": "Password cannot be less than 4 characters"
                               })

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        user = User.objects.filter(phone_number=phone_number).exists()

        if user:
            raise ValidationError("This phone number already exists")
        return phone_number

    def clean_email(self):
        email = self.cleaned_data['email']
        user = User.objects.filter(email=email).exists()
        if user:
            raise ValidationError("This email already exists")
        return email


class VerifyCodeForm(forms.Form):
    code = forms.IntegerField(label="Code", widget=forms.NumberInput(attrs={"class": "form-control col=md-6 mb-3"}))


class UserLoginForm(forms.Form):
    phone_number = forms.CharField(max_length=11, label="Phone number", widget=forms.TextInput(
        attrs={"class": "form-control col=md-6", "placeholder": "Enter your phone number"}),
                                   error_messages={
                                       "required": "Please enter your phone number",
                                       "invalid": "Please enter a valid phone number",
                                       "max_length": "Phone number cannot be longer than 11 characters",
                                   })