from rest_framework import routers

from kudos.viewsets import UserViewSet, KudosViewSet

router = routers.SimpleRouter()

router.register(r"api/users", UserViewSet)
router.register(r"api/kudos", KudosViewSet)
