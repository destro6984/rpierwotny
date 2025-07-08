import csv

from django.db import models
from django.db.models import QuerySet

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


class SubscriberSMS(BaseModel):
    phone = models.CharField(max_length=10, unique=True)
    gdpr_consent = models.BooleanField()

    objects = SubscriberSMSQuerySet.as_manager()

    def __str__(self):
        return f"SubscriberSMS: {self.phone}"


class Client(BaseModel):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=10)

    objects = ClientQuerySet.as_manager()

    def __str__(self):
        return f"Client: {self.email}"


class User(BaseModel):
    email = models.EmailField()
    phone = models.CharField(max_length=32)
    gdpr_consent = models.BooleanField()

    def __str__(self):
        return f"User: {self.email}"
