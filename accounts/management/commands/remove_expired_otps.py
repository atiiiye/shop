from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import OtpCode


class Command(BaseCommand):
    help = "remove all expired otp codes"

    def handle(self, *args, **options):
        expired_time = timezone.now() - timedelta(minutes=2)
        OtpCode.objects.filter(created__lt=expired_time).delete()
        self.stdout.write("all expired otps removed")
