import csv

from django.db import models
from django.db.models import (
    QuerySet,
    OuterRef,
    Exists,
    Subquery,
    CharField,
)

from users.managers import ClientQuerySet, SubscriberSMSQuerySet, SubscriberQuerySet


class BaseModel(models.Model):
    create_date = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def dump_queryset_to_csv(qs: QuerySet, outfile_path: str) -> None:
        model = qs.model
        field_names = [field.name for field in model._meta.fields]
        with open(f"./{outfile_path}", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(field_names)
            for obj in qs:
                writer.writerow([getattr(obj, field) for field in field_names])

    class Meta:
        abstract = True


class Subscriber(BaseModel):
    email = models.EmailField(unique=True)
    gdpr_consent = models.BooleanField()

    objects = SubscriberQuerySet.as_manager()

    def __str__(self):
        return f"Subscriber: {self.email}"

    @classmethod
    def data_to_create_user(cls):
        qs = cls.objects.annotate(
            user_same=Exists(User.objects.filter(email=OuterRef("email"))),
            client_same=Exists(Client.objects.filter(email=OuterRef("email"))),
            user_same_phone_email_different_client=Exists(
                Client.get_conflict_users().filter(email=OuterRef("email"))
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
        return qs


class SubscriberSMS(BaseModel):
    phone = models.CharField(max_length=10, unique=True)
    gdpr_consent = models.BooleanField()

    objects = SubscriberSMSQuerySet.as_manager()

    def __str__(self):
        return f"SubscriberSMS: {self.phone}"

    @classmethod
    def data_to_create_user(cls):
        qs = cls.objects.annotate(
            user_same=Exists(User.objects.filter(phone=OuterRef("phone"))),
            client_same=Exists(Client.objects.filter(phone=OuterRef("phone"))),
            user_same_phone_email_different_client=Exists(
                Client.get_conflict_users().filter(phone=OuterRef("phone"))
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
        return qs


class Client(BaseModel):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=10)

    objects = ClientQuerySet.as_manager()

    def __str__(self):
        return f"Client: {self.email}"

    @classmethod
    def get_conflict_users(cls):
        # better on custom QS or manager
        return (
            Client.objects.exclude_duplicated_phones()
            .annotate(
                user_same_phone_different_email=Exists(
                    User.objects.filter(phone=OuterRef("phone")).exclude(
                        email=OuterRef("email")
                    )
                )
            )
            .filter(user_same_phone_different_email=True)
        )


class User(BaseModel):
    email = models.EmailField()
    phone = models.CharField(max_length=32)
    gdpr_consent = models.BooleanField()

    def __str__(self):
        return f"User: {self.email}"
