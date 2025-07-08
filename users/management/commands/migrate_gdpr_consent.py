from django.db import transaction, IntegrityError

from users.models import User, Subscriber, SubscriberSMS

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Migrate GDPR consent from "
        "Subscriber/SubscriberSMS to User based on "
        "creation date logic"
    )

    def handle(self, *args, **options):
        # Annotate Subscribers with related User info
        subscribers = (
            Subscriber.objects.annotate_data_to_create_users()
            .filter(user_same=True)
            .annotate_data_to_migrate_gdpr()
            .filter(is_subscriber_newer=True)
        )

        # Annotate SubscriberSMS with related User info
        sms_subscribers = (
            SubscriberSMS.objects.annotate_data_to_create_users()
            .filter(user_same=True)
            .annotate_data_to_migrate_gdpr()
            .filter(is_sms_newer=True)
        )

        # Build user update mapping {user_id: (latest_create_date, gdpr_consent)}
        user_updates = {}

        # First, process Subscriber
        for sub in subscribers:
            if (
                sub.user_id not in user_updates
                or sub.create_date > user_updates[sub.user_id][1]
            ):
                user_updates[sub.user_id] = (sub.gdpr_consent, sub.create_date)

        # Then, process SubscriberSMS (may overwrite if create_date is newer)
        for sms in sms_subscribers:
            if (
                sms.user_id not in user_updates
                or sms.create_date > user_updates[sms.user_id][1]
            ):
                user_updates[sms.user_id] = (sms.gdpr_consent, sms.create_date)

        # Bulk update Users
        updated_counter = 0
        user_ids = list(user_updates.keys())
        users = User.objects.filter(id__in=user_ids)
        for user in users:
            if user.gdpr_consent != user_updates[user.id][0]:
                user.gdpr_consent = user_updates[user.id][0]
                updated_counter += 1

        try:
            with transaction.atomic():
                User.objects.bulk_update(users, ["gdpr_consent"])
        except IntegrityError as e:
            self.stdout.write(f"Unexpected error: {e}")

        self.stdout.write(
            self.style.SUCCESS(f"Updated GDPR consent for {updated_counter} users.")
        )
