from django.apps import apps
from django.core.management.base import BaseCommand

from users.models import Subscriber


class Command(BaseCommand):
    help = "Generate csv from Queryset"

    def add_arguments(self, parser):
        parser.add_argument(
            "model",
            type=str,
            choices=["users.Subscriber", "users.SubscriberSMS"],
            help="App.ModelName (e.g., myapp.Client)",
        )

    def handle(self, *args, **options):
        model_path = options["model"]
        try:
            app_label, model_name = model_path.split(".")
            model = apps.get_model(app_label, model_name)
        except (ValueError, LookupError):
            self.stderr.write(self.style.ERROR(f"Invalid model: {model_path}"))
            return

        qs = model.objects.annotate_data_to_create_users().filter(
            user_same=False,
            client_same=True,
            user_same_phone_email_different_client=True,
        )
        csv_path = (
            "./subscribers_conflicts.csv"
            if isinstance(model, Subscriber)
            else "./subscriberssms_conflicts.csv"
        )
        model.dump_queryset_to_csv(qs, csv_path)
        self.stderr.write(self.style.NOTICE(f"File csv generated at {csv_path}"))
