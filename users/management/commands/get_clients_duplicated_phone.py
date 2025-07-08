from django.core.management.base import BaseCommand

from users.models import Client


class Command(BaseCommand):
    help = "Generate csv from Queryset Clients duplicated phones"

    def handle(self, *args, **options):

        qs = Client.objects.duplicated_phones()

        Client.dump_queryset_to_csv(qs, "./clients_duplicated_phone.csv")
        self.stderr.write(
            self.style.NOTICE(
                f"File csv generated at {"./clients_duplicated_phone.csv"}"
            )
        )
