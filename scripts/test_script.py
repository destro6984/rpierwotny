import csv

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Exists, OuterRef, Count, Case, DateTimeField, F
from django.template.defaultfilters import default

from users.models import *
from users.serializers import SubscriberSMSSerializer
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import (
    Exists,
    OuterRef,
    Count,
    QuerySet,
    Case,
    When,
    Value,
    BooleanField,
    Subquery,
)

from users.models import *
from users.serializers import SubscriberSMSSerializer


def run():
    # client_phones_duplicates = (
    #     Client.objects.values('phone')
    #     .annotate(phone_count=Count('id'))
    #     .filter(phone_count__gt=1)
    # )
    #
    # print(client_phones_duplicates.values("phone", "phone_count"))
    # user_same_phone_email_different_client = (Client.objects.annotate(user_same_phone_diffetent_email=Exists(
    #     User.objects.filter(
    #         phone=OuterRef('phone')
    #     ).exclude(email=OuterRef('email'))
    # )
    # ))
    #
    # print(user_same_phone_email_different_client.count(),99999)
    # print(user_same_phone_email_different_client.exclude(phone__in=client_phones_duplicates.values_list('phone', flat=True)).count(),9999449)
    # # .exclude(phone__in=client_phones_duplicates.values_list('phone', flat=True)))
    #
    # qur=Subscriber.objects.all()
    # c = qur.annotate(
    #         user_same_email_subscriber=Exists(User.objects.filter(email=OuterRef('email'))),
    #         client_same_email_subscriber=Exists(Client.objects.filter(email=OuterRef('email'))),
    #         user_same_phone_email_different_client=Exists(user_same_phone_email_different_client),
    #
    #
    #         should_create_user=Case(
    #             When(user_same_email_subscriber=True, then=Value(False)),
    #             default=Value(False),
    #             output_field=BooleanField(),
    #
    #         ),
    #         should_create_user_from_client=Case(
    #             When(user_same_email_subscriber=False, client_same_email_subscriber=True,
    #                  user_same_phone_email_different_client=False, then=Value(True))),
    #         should_create_phone_empty=Case(When(user_same_email_subscriber=False, then=Value(True))),
    #         client_email=Subquery(Client.objects.filter(email=OuterRef('email')).values("email")),
    #         client_phone=Subquery(Client.objects.filter(email=OuterRef('email')).values("phone")),
    #     )
    # sub_to_create_users = c.filter(user_same_email_subscriber=False, client_same_email_subscriber=True,
    #                                     user_same_phone_email_different_client=False)
    #
    # # for i in c:
    # #     print(vars(i),"^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    # print(sub_to_create_users.count(),"((((((((((((((((((((((((((((")
    # print(c.count())

    # b=SubscriberSMS.objects.annotate(
    #         user_same_phone=Exists(User.objects.filter(email=OuterRef('phone'))),
    #         client_same_phone=Exists(Client.objects.filter(email=OuterRef('phone'))),
    #         user_same_phone_email_different_client=Exists(user_same_phone_email_different_client),
    #
    #         should_create_user=Case(
    #             When(user_same_phone=True, then=Value(False)),
    #             default=Value(False),
    #             output_field=BooleanField(),
    #
    #         ),
    #         should_create_user_from_client=Case(
    #             When(user_same_phone=False, client_same_phone=True,
    #                  user_same_phone_email_different_client=False, then=Value(True))),
    #         client_email=Subquery(Client.objects.filter(phone=OuterRef('phone')).values("email")),
    #         client_phone=Subquery(Client.objects.filter(phone=OuterRef('phone')).values("phone")),
    #     )
    # for i in b:
    #     print(vars(i))
    # print(b.count())

    # x= User.objects.annotate(Exists(Client.objects.filter(email=OuterRef("phone"))))

    # user_conflict = Client.objects.exclude_duplicated_phones().annotate(user_same_phone_different_email=Exists(
    #     User.objects.filter(
    #         phone=OuterRef('phone')
    #     ).exclude(email=OuterRef('email'))
    # ))
    #
    # b = Subscriber.objects.annotate(
    #     user_same_email=Exists(User.objects.filter(email=OuterRef('email'))),
    #     client_same_email=Exists(Client.objects.filter(email=OuterRef('email'))),
    #     user_same_phone_client=Exists(user_conflict.filter(email=OuterRef("email"))),
    #     client_phone=Subquery(
    #         Client.objects.exclude_duplicated_phones().filter(email=OuterRef("email")).values("phone"),
    #         output_field=CharField()),
    #     client_email=Subquery(
    #         Client.objects.exclude_duplicated_phones().filter(email=OuterRef("email")).values("email"),
    #         output_field=CharField())
    # )
    #
    # print(b.values())
    #
    # sms=SubscriberSMS.objects.annotate(
    # user_same_phone=Exists(User.objects.filter(phone=OuterRef('phone'))),
    # client_same_phone=Exists(Client.objects.filter(phone=OuterRef('phone'))),
    # user_same_phone_client=Exists(user_conflict.filter(phone=OuterRef("phone"))),
    # client_phone=Subquery(
    #     Client.objects.exclude_duplicated_phones().filter(phone=OuterRef("phone")).values("phone"),
    #     output_field=CharField()),
    # client_email=Subquery(
    #     Client.objects.exclude_duplicated_phones().filter(phone=OuterRef("phone")).values("email"),
    #     output_field=CharField())
    # )
    # # nie zmienia tego ostatniego warunku tylko łap o phoen a nie po emial i bedzie dobrze
    # print(sms)
    # print(sms.count())
    # print(sms.values())

    qs = Subscriber.data_to_create_user().filter(user_same=True)

    user_from_client = User.objects.annotate(
        exist_from_client=Exists(
            Client.objects.filter(email=OuterRef("email"), phone=OuterRef("phone"))
        )
    ).filter(exist_from_client=True)

    m = (
        Subscriber.data_to_create_user()
        .filter(user_same=True)
        .annotate(
            user_same_created_date=Subquery(
                User.objects.filter(email=OuterRef("email")).values("create_date")[:1],
                output_field=DateTimeField(),
            ),
            user_id_to_update=Subquery(
                User.objects.filter(email=OuterRef("email")).values("id")[:1]
            ),
            created_first=Case(
                When(create_date__gt=F("user_same_created_date"), then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            ),
            user_from_client=Exists(user_from_client),
        )
    )
    m = (
        Subscriber.data_to_create_user()
        .filter(user_same=True)
        .annotate(
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
        .filter(is_subscriber_newer=True)
    )
    print(
        SubscriberSMS.data_to_create_user()
        .filter(user_same=True)
        .annotate(
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
        .filter(is_sms_newer=True)
    )
