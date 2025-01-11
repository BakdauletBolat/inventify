from rest_framework.viewsets import ModelViewSet

from apps.feedback.models import Feedback
from apps.feedback.serializers import FeedbackSerializer


class FeedbackViewSet(ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
