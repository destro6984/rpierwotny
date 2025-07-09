import random

from django.core.management.base import BaseCommand
from faker import Faker
from users.models import Subscriber, SubscriberSMS, Client, User


class Command(BaseCommand):
    help = "Generate test data with overlapping emails/phones across models"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count", type=int, default=20, help="Number of test records per model"
        )

    def handle(self, *args, **options):
        fake = Faker("pl_PL")
        count = options["count"]

        # Generate a shared pool larger than needed
        shared_emails = [fake.unique.email() for _ in range(count * 2)]
        fake.unique.clear()
        shared_phones = [self.fake_phone_number(fake) for _ in range(count * 2)]
        fake.unique.clear()

        # Randomly sample unique emails/phones for each model
        subscriber_emails = random.sample(shared_emails, count)
        client_emails = random.sample(shared_emails, count)

        # Subscriber
        for email in subscriber_emails:
            Subscriber.objects.create(
                email=email,
                gdpr_consent=fake.boolean(),
            )

        # SubscriberSMS
        subscriber_phones = random.sample(shared_phones, count)
        for phone in subscriber_phones:
            SubscriberSMS.objects.create(
                phone=phone,
                gdpr_consent=fake.boolean(),
            )

        # Client
        client_phones = random.sample(shared_phones, count)
        for email, phone in zip(client_emails, client_phones):
            Client.objects.create(
                email=email,
                phone=phone,
            )

        # User (optional: also sample, or use random.choice for more overlap)
        user_emails = random.sample(shared_emails, count)
        user_phones = random.sample(shared_phones, count)
        for email, phone in zip(user_emails, user_phones):
            User.objects.create(
                email=email,
                phone=phone,
                gdpr_consent=fake.boolean(),
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Test data with possible overlap "
                "between Client and Subscriber emails, "
                "but unique within each model, generated!"
            )
        )

    @staticmethod
    def fake_phone_number(fake: Faker) -> str:
        return f"{fake.msisdn()[4:]}"
