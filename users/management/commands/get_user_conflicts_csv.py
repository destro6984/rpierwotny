from django.apps import apps
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Generate csv from Queryset"

    def add_arguments(self, parser):
        parser.add_argument(
            "model", type=str, help="App.ModelName (e.g., myapp.Client)"
        )
        parser.add_argument("csv_path", type=str, help="Path to save the CSV file")

    def handle(self, *args, **options):
        model_path = options["model"]
        csv_path = options["csv_path"]
        try:
            app_label, model_name = model_path.split(".")
            model = apps.get_model(app_label, model_name)
        except (ValueError, LookupError):
            self.stderr.write(self.style.ERROR(f"Invalid model: {model_path}"))
            return

        qs = model.data_to_create_user().filter(
            user_same=False,
            client_same=True,
            user_same_phone_email_different_client=True,
        )

        model.dump_queryset_to_csv(qs, csv_path)
        self.stderr.write(self.style.NOTICE(f"File csv generated at {csv_path}"))
