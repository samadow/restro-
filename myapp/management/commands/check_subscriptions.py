from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from myapp.models import RestaurantSubscription, RestaurantNotification, notify_restaurant


class Command(BaseCommand):
    help = "Notify restaurants about ending and expired subscriptions"

    def handle(self, *args, **options):
        today = timezone.localdate()

        expired = list(RestaurantSubscription.objects.filter(status="active", end_date__lt=today))
        for subscription in expired:
            subscription.status = "expired"
            subscription.save()

        ending = RestaurantSubscription.objects.filter(
            status="active",
            end_date__gte=today,
            end_date__lte=today + timedelta(days=3)
        )
        for subscription in ending:
            already = RestaurantNotification.objects.filter(
                restaurant=subscription.restaurant,
                notification_type="subscription",
                title="Subscription ends soon",
                cr_at__date=today
            ).exists()

            if not already:
                days = (subscription.end_date - today).days
                notify_restaurant(
                    subscription.restaurant,
                    "Subscription ends soon",
                    f"Plan {subscription.plan.name} ends in {days} day(s) ({subscription.end_date})",
                    "subscription"
                )

        self.stdout.write(f"Expired: {len(expired)}, ending soon: {ending.count()}")
