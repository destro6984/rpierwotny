from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import transaction, IntegrityError

from users.models import User


class Command(BaseCommand):
    help = "Migrates data to Users from Subscriber/SubscriberSMS"

    def add_arguments(self, parser):
        parser.add_argument(
            "model",
            type=str,
            choices=["users.Subscriber", "users.SubscriberSMS"],
            help="App.ModelName (e.g., myapp.Client)",
        )

    def handle(self, *args, **options):
        failed = 0

        model_path = options["model"]
        try:
            app_label, model_name = model_path.split(".")
            model = apps.get_model(app_label, model_name)
        except (ValueError, LookupError):
            self.stderr.write(self.style.ERROR(f"Invalid model: {model_path}"))
            return

        data_to_create_users = []

        qs = model.objects.annotate_data_to_create_users()

        qs_to_create_users = qs.filter(
            user_same=False, user_same_phone_email_different_client=False
        )

        for data in qs_to_create_users:
            if data.client_same:
                data_to_create_users.append(
                    User(
                        phone=data.client_phone,
                        email=data.client_email,
                        gdpr_consent=data.gdpr_consent,
                    )
                )
            else:
                data_to_create_users.append(
                    User(
                        phone=getattr(data, "phone", ""),
                        email=getattr(data, "email", ""),
                        gdpr_consent=data.gdpr_consent,
                    )
                )

        try:
            with transaction.atomic():
                User.objects.bulk_create(data_to_create_users)
        except IntegrityError as e:
            self.stdout.write(f"Unexpected error: {e}")
            failed += 1

        self.stdout.write(
            f"Data migrated : failed {failed} " f"out of {len(qs_to_create_users)} "
        )
