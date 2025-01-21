from datetime import datetime

from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.feedback.models import Feedback
from apps.feedback.requests import TelegramRequest
from apps.feedback.serializers import FeedbackSerializer


class FeedbackViewSet(ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        message = (
            f"🔔 Новая обратная связь ID: {serializer.instance.id}\n"
            f"📞 Номер телефона: {serializer.validated_data['phone']}\n"
            f"👤 Имя: {serializer.validated_data['name']}\n"
            f"⏰ Дата создания: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )

        TelegramRequest().send_sms_feedback(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
