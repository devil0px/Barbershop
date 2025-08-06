from django.core.management.base import BaseCommand
from django.db.models import Count
from barbershops.models import Barbershop

class Command(BaseCommand):
    help = 'Finds and merges duplicate barbershops based on owner and name.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting duplicate barbershop cleanup..."))

        duplicates = (
            Barbershop.objects.values('owner_id', 'name')
            .annotate(count=Count('id'))
            .filter(count__gt=1)
        )

        if not duplicates:
            self.stdout.write(self.style.SUCCESS("No duplicate barbershops found."))
            return

        self.stdout.write(self.style.WARNING(f"Found {len(duplicates)} group(s) of duplicates."))

        for item in duplicates:
            owner_id = item['owner_id']
            name = item['name']

            shops = Barbershop.objects.filter(
                owner_id=owner_id,
                name=name
            ).order_by('created_at', 'id')

            original_shop = shops.first()
            self.stdout.write(f"\nKeeping original shop: '{original_shop.name}' (ID: {original_shop.id})")

            duplicate_shops = shops[1:]

            for dup_shop in duplicate_shops:
                self.stdout.write(f"-- Processing duplicate: '{dup_shop.name}' (ID: {dup_shop.id})")

                services_moved = dup_shop.services.update(barbershop=original_shop)
                if services_moved:
                    self.stdout.write(self.style.SUCCESS(f"   Moved {services_moved} service(s) to the original shop."))

                images_moved = dup_shop.images.update(barbershop=original_shop)
                if images_moved:
                    self.stdout.write(self.style.SUCCESS(f"   Moved {images_moved} image(s) to the original shop."))

                if hasattr(dup_shop, 'reviews'):
                    reviews_moved = dup_shop.reviews.update(barbershop=original_shop)
                    if reviews_moved:
                        self.stdout.write(self.style.SUCCESS(f"   Moved {reviews_moved} review(s) to the original shop."))

                if hasattr(dup_shop, 'bookings'):
                    bookings_moved = dup_shop.bookings.update(barbershop=original_shop)
                    if bookings_moved:
                        self.stdout.write(self.style.SUCCESS(f"   Moved {bookings_moved} booking(s) to the original shop."))

                dup_shop.delete()
                self.stdout.write(self.style.WARNING(f"   Successfully deleted duplicate shop (ID: {dup_shop.id})."))

        self.stdout.write(self.style.SUCCESS("\nCleanup complete!"))
