from django.db.models import (
    Count,
    Exists,
    OuterRef,
    Subquery,
    CharField,
    Value,
    BooleanField,
    DateTimeField,
    When,
    Case,
    F,
)
from django.db import models


class ClientQuerySet(models.QuerySet):
    def _get_duplicate_phones(self):
        return (
            self.values("phone")
            .annotate(phone_count=Count("id"))
            .filter(phone_count__gt=1)
            .values_list("phone", flat=True)
        )

    def duplicated_phones(self):
        return self.filter(phone__in=self._get_duplicate_phones()).order_by("phone")

    def exclude_duplicated_phones(self):
        return self.exclude(phone__in=self._get_duplicate_phones())

    def annotate_conflict_users(self):
        from users.models import User

        return (
            self.exclude_duplicated_phones()
            .annotate(
                user_same_phone_different_email=Exists(
                    User.objects.filter(phone=OuterRef("phone")).exclude(
                        email=OuterRef("email")
                    )
                )
            )
            .filter(user_same_phone_different_email=True)
        )


class SubscriberQuerySet(models.QuerySet):

    def annotate_data_to_create_users(self):
        from users.models import User, Client

        return self.annotate(
            user_same=Exists(User.objects.filter(email=OuterRef("email"))),
            client_same=Exists(Client.objects.filter(email=OuterRef("email"))),
            user_same_phone_email_different_client=Exists(
                Client.objects.annotate_conflict_users().filter(email=OuterRef("email"))
            ),
            client_phone=Subquery(
                Client.objects.exclude_duplicated_phones()
                .filter(email=OuterRef("email"))
                .values("phone"),
                output_field=CharField(),
            ),
            client_email=Subquery(
                Client.objects.exclude_duplicated_phones()
                .filter(email=OuterRef("email"))
                .values("email"),
                output_field=CharField(),
            ),
        )

    def annotate_data_to_migrate_gdpr(self):
        from users.models import User

        return self.annotate(
            user_id=Subquery(
                User.objects.filter(email=OuterRef("email")).values("id")[:1]
            ),
            user_create_date=Subquery(
                User.objects.filter(email=OuterRef("email")).values("create_date")[:1],
                output_field=DateTimeField(),
            ),
            is_subscriber_newer=Case(
                When(create_date__gt=F("user_create_date"), then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            ),
        )


class SubscriberSMSQuerySet(models.QuerySet):

    def annotate_data_to_create_users(self):
        from users.models import Client, User

        return self.annotate(
            user_same=Exists(User.objects.filter(phone=OuterRef("phone"))),
            client_same=Exists(Client.objects.filter(phone=OuterRef("phone"))),
            user_same_phone_email_different_client=Exists(
                Client.objects.annotate_conflict_users().filter(phone=OuterRef("phone"))
            ),
            client_phone=Subquery(
                Client.objects.exclude_duplicated_phones()
                .filter(phone=OuterRef("phone"))
                .values("phone"),
                output_field=CharField(),
            ),
            client_email=Subquery(
                Client.objects.exclude_duplicated_phones()
                .filter(phone=OuterRef("phone"))
                .values("email"),
                output_field=CharField(),
            ),
        )

    def annotate_data_to_migrate_gdpr(self):
        from users.models import User

        return self.annotate(
            user_id=Subquery(
                User.objects.filter(phone=OuterRef("phone")).values("id")[:1]
            ),
            user_create_date=Subquery(
                User.objects.filter(phone=OuterRef("phone")).values("create_date")[:1],
                output_field=DateTimeField(),
            ),
            is_sms_newer=Case(
                When(create_date__gt=F("user_create_date"), then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            ),
        )
