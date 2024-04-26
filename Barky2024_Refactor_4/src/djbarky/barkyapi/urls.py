from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"bookmarks", views.BookmarkViewSet)
router.register(r"snippets", views.SnippetViewSet)
router.register(r"users", views.UserViewSet)

app_name = "barkyapi"

urlpatterns = [
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("", include(router.urls)),
]

# add the router's URLs to the urlpatterns
urlpatterns += router.urls
