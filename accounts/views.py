from django.shortcuts import render, redirect
from django.views import View

from utils import send_otp_code
from .forms import UserRegistrationForm, VerifyCodeForm
from random import randint
from django.contrib import messages
from .models import OtpCode, User

from datetime import timedelta
from django.utils import timezone


class UserRegisterView(View):
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            code = randint(1000, 9999)

            send_otp_code(phone_number=cd['phone_number'], code=code)
            OtpCode.objects.create(phone_number=cd['phone_number'], code=code)
            request.session['user_info'] = {
                'phone_number': cd['phone_number'],
                'email': cd['email'],
                'full_name': cd['full_name'],
                'password': cd['password']
            }
            messages.success(request, 'code send to you', 'success')
            return redirect('accounts:verify_code')

        return render(request, self.template_name, {'form': form})


class UserVerifyCodeView(View):
    form_class = VerifyCodeForm

    def get(self, request):
        form = self.form_class
        return render(request, 'accounts/verify.html', {"form": form})

    def post(self, request):
        user_session = request.session['user_info']
        form = self.form_class(request.POST)
        code_instance = OtpCode.objects.get(phone_number=user_session['phone_number'])
        expired_time = code_instance.created + timedelta(minutes=1)
        if form.is_valid():
            cd = form.cleaned_data
            if timezone.now() > expired_time:
                messages.error(request, 'Code is expired', 'danger')
                return redirect('accounts:user_register')

            if cd['code'] == code_instance.code and timezone.now() < expired_time:
                User.objects.create_user(user_session['phone_number'], user_session['email'],
                                     user_session['full_name'], user_session['password'])
                messages.success(request, 'You register successfully', 'success')
                code_instance.delete()
                return redirect('home:home')
            else:
                messages.error(request, 'Code is wrong', 'danger')
                return redirect('accounts:verify_code')
        return redirect('home:home')
