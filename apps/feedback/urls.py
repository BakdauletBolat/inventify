from rest_framework.routers import SimpleRouter

from apps.feedback.views import FeedbackViewSet

router_class = SimpleRouter()
router_class.register('', FeedbackViewSet)

urlpatterns = router_class.urls
