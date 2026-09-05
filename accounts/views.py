from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import logout, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import View

from utils import send_otp_code, generate_otp
from .forms import UserRegistrationForm, VerifyCodeForm, UserLoginForm
from .models import OtpCode, User


class UserRegisterView(View):
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'

    def setup(self, request, *args, **kwargs):
        self.next = request.GET.get("next")
        return super().setup(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            code = generate_otp()
            send_otp_code(phone_number=cd['phone_number'], code=code)
            OtpCode.objects.create(phone_number=cd['phone_number'], code=code)
            request.session['user_info'] = {
                'phone_number': cd['phone_number'],
                'email': cd['email'],
                'full_name': cd['full_name'],
                'password': cd['password']
            }
            messages.success(request, 'code send to you', 'success')
            return redirect('accounts:register_verify_code')

        return render(request, self.template_name, {'form': form})


class UserRegistrationVerifyCodeView(View):
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
                code_instance.delete()
                return redirect('accounts:user_register')

            if cd['code'] == code_instance.code and timezone.now() < expired_time:
                User.objects.create_user(user_session['phone_number'], user_session['email'],
                                         user_session['full_name'], user_session['password'])
                messages.success(request, 'You register successfully', 'success')
                code_instance.delete()
                return redirect('home:home')
            else:
                messages.error(request, 'Code is wrong', 'danger')
                return redirect('accounts:register_verify_code')
        return redirect('home:home')


class UserLoginView(View):
    form_class = UserLoginForm
    template_name = 'accounts/login.html'

    def setup(self, request, *args, **kwargs):
        self.next = request.GET.get("next")
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home:home")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            try:
                User.objects.get(phone_number=cd['phone_number'])
            except User.DoesNotExist:
                messages.error(request, 'User does not exist', 'danger')
                return redirect('accounts:user_login')

            code = generate_otp()
            send_otp_code(phone_number=cd['phone_number'], code=code)
            OtpCode.objects.filter(phone_number=cd['phone_number']).delete()
            OtpCode.objects.create(phone_number=cd['phone_number'], code=code)
            request.session['user_login_info'] = {
                'phone_number': cd['phone_number'],
            }
            messages.success(request, 'code send to you', 'success')
            return redirect('accounts:login_verify_code')

        return render(request, self.template_name, {"form": form})


class UserLoginVerifyCodeView(View):
    form_class = VerifyCodeForm
    template_name = 'accounts/verify.html'

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)
        user_session = request.session['user_login_info']
        code_instance = OtpCode.objects.get(phone_number=user_session['phone_number'])
        expired_time = code_instance.created + timedelta(minutes=1)
        if form.is_valid():
            cd = form.cleaned_data
            if timezone.now() > expired_time:
                messages.error(request, 'Code is expired', 'danger')
                code_instance.delete()
                return redirect('accounts:user_login')

            if cd['code'] == code_instance.code and timezone.now() < expired_time:
                user = User.objects.get(phone_number=user_session['phone_number'])
                login(request, user)
                messages.success(request, 'You login successfully', 'success')
                code_instance.delete()
                return redirect('home:home')
            else:
                messages.error(request, 'Code is wrong', 'danger')
                return redirect('accounts:login_verify_code')
        return redirect('home:home')


class UserLogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        messages.info(request, "logged out successfully", "info")
        return redirect("home:home")
