# flake8: noqa
from datetime import timezone, datetime

from django.core.management import call_command
from django.test import TestCase

from users.models import User, Subscriber, Client, SubscriberSMS


class SubscriberMigrationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        pass

    def test_user_same_email_as_subscriber(self):
        User.objects.create(email="test", phone="1", gdpr_consent=1)
        Subscriber.objects.create(email="test", gdpr_consent=1)

        call_command("migrate_data_to_users", "users.Subscriber")

        self.assertEqual(User.objects.count(), 1)

    def test_user_not_same_email_as_subscriber(self):
        User.objects.create(email="test1", phone="1", gdpr_consent=1)
        Subscriber.objects.create(email="test", gdpr_consent=1)

        call_command("migrate_data_to_users", "users.Subscriber")

        self.assertEqual(User.objects.count(), 2)

    def test_client_same_email_subscriber_no_user_same_phone_client_and_email_diff_client(
        self,
    ):
        User.objects.create(email="test1", phone="1", gdpr_consent=1)
        Subscriber.objects.create(email="test", gdpr_consent=1)

        Client.objects.create(email="test", phone="13")

        call_command("migrate_data_to_users", "users.Subscriber")

        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(User.objects.get(email="test").email, "test")
        self.assertEqual(User.objects.get(email="test").phone, "13")

    def test_client_same_email_subscriber_user_same_phone_client_and_email_diff_client(
        self,
    ):
        User.objects.create(email="test1", phone="1", gdpr_consent=1)
        Subscriber.objects.create(email="test", gdpr_consent=1)
        Client.objects.create(email="test", phone="1")

        call_command("migrate_data_to_users", "users.Subscriber")

        self.assertEqual(User.objects.count(), 1)

    def test_no_client_same_email_subscriber(self):
        User.objects.create(email="test1", phone="1", gdpr_consent=1)
        Subscriber.objects.create(email="test", gdpr_consent=1)

        Client.objects.create(email="test3", phone="2")

        call_command("migrate_data_to_users", "users.Subscriber")

        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(User.objects.get(email="test").phone, "")


class SubscriberSMSMigrationTests(TestCase):

    def test_user_same_phone_as_subscribersms(self):
        User.objects.create(email="test", phone="1", gdpr_consent=1)
        SubscriberSMS.objects.create(phone="1", gdpr_consent=1)

        call_command("migrate_data_to_users", "users.SubscriberSMS")

        self.assertEqual(User.objects.count(), 1)

    def test_user_not_same_phone_as_subscribersms(self):
        User.objects.create(email="test1", phone="1", gdpr_consent=1)
        SubscriberSMS.objects.create(phone="2", gdpr_consent=1)

        call_command("migrate_data_to_users", "users.SubscriberSMS")

        self.assertEqual(User.objects.count(), 2)

    def test_client_same_email_subscriber_no_user_same_phone_client_and_email_diff_client(
        self,
    ):
        User.objects.create(email="test1", phone="1", gdpr_consent=1)
        SubscriberSMS.objects.create(phone="13", gdpr_consent=1)

        Client.objects.create(email="test", phone="13")

        call_command("migrate_data_to_users", "users.SubscriberSMS")

        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(User.objects.get(email="test").email, "test")
        self.assertEqual(User.objects.get(email="test").phone, "13")

    def test_client_same_phone_subscribersms_user_same_phone_client_and_email_diff_client(
        self,
    ):
        User.objects.create(email="test1", phone="1", gdpr_consent=1)
        SubscriberSMS.objects.create(phone="1", gdpr_consent=1)
        Client.objects.create(email="test", phone="1")

        call_command("migrate_data_to_users", "users.SubscriberSMS")

        self.assertEqual(User.objects.count(), 1)

    def test_no_client_same_phone_subscribersms(self):
        User.objects.create(email="test1", phone="1", gdpr_consent=1)
        SubscriberSMS.objects.create(phone="12", gdpr_consent=1)

        Client.objects.create(email="test3", phone="2")

        call_command("migrate_data_to_users", "users.SubscriberSMS")

        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(User.objects.get(phone="12").email, "")


class SubscribersGDPRMigrationTests(TestCase):
    def test_user_no_same_phone_as_subscribersms(self):
        User.objects.create(email="test", phone="1", gdpr_consent=0)
        SubscriberSMS.objects.create(phone="2", gdpr_consent=1)

        call_command("migrate_gdpr_consent")

        self.assertEqual(User.objects.get(email="test").gdpr_consent, False)

    def test_user_same_email_as_subscriber(self):
        User.objects.create(email="test", phone="1", gdpr_consent=0)
        Subscriber.objects.create(email="test", gdpr_consent=1)

        call_command("migrate_gdpr_consent")

        self.assertEqual(User.objects.get(email="test").gdpr_consent, True)

    def test_user_same_email_as_subscriber_older_date(self):
        User.objects.create(email="test", phone="1", gdpr_consent=0)
        sub = Subscriber.objects.create(email="test", gdpr_consent=1)
        sub.create_date = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        sub.save()

        call_command("migrate_gdpr_consent")

        self.assertEqual(User.objects.get(email="test").gdpr_consent, False)

    def test_user_same_email_as_subscribersms_the_newest(self):
        User.objects.create(email="test", phone="1", gdpr_consent=0)
        Subscriber.objects.create(email="test", gdpr_consent=0)
        sub_sms = SubscriberSMS.objects.create(phone="1", gdpr_consent=1)
        sub_sms.create_date = datetime(2025, 9, 1, 12, 0, 0, tzinfo=timezone.utc)
        sub_sms.save()

        call_command("migrate_gdpr_consent")

        self.assertEqual(User.objects.get(email="test").gdpr_consent, True)
