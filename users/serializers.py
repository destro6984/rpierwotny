from rest_framework import serializers
from users.models import Subscriber, SubscriberSMS, Client, User


class SubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriber
        fields = "__all__"


class SubscriberSMSSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriberSMS
        fields = "__all__"


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
