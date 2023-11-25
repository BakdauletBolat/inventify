from rest_framework.views import APIView


# Create your views here.
class BaseAPIView(APIView):
    deserializer_class = None
    serializer_class = None

    def get_deserializer(self, *args, **kwargs):
        return self.deserializer_class(*args, **kwargs)

    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(*args, **kwargs)
