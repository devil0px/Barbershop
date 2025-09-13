from django.core.management.base import BaseCommand
from barbershops.utils import reset_daily_turns


class Command(BaseCommand):
    help = 'Reset current turn numbers for all barbershops to 0 (daily reset)'

    def handle(self, *args, **options):
        updated_count = reset_daily_turns()
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully reset turn numbers for {updated_count} barbershops'
            )
        )
