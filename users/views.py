from rest_framework import viewsets
from .models import Subscriber, SubscriberSMS, Client, User
from .serializers import (
    SubscriberSerializer,
    SubscriberSMSSerializer,
    ClientSerializer,
    UserSerializer,
)


class SubscriberViewSet(viewsets.ModelViewSet):
    queryset = Subscriber.objects.all()
    serializer_class = SubscriberSerializer


class SubscriberSMSViewSet(viewsets.ModelViewSet):
    queryset = SubscriberSMS.objects.all()
    serializer_class = SubscriberSMSSerializer


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
