from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from .models import OtpCode


@shared_task
def removed_expired_otp_codes():
    expired_time = timezone.now() - timedelta(minutes=2)
    OtpCode.objects.filter(created__lt=expired_time).delete()