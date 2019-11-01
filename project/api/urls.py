from django.conf.urls import url, include
from rest_framework import routers
from project.api import views
from django.conf import settings
from django.conf.urls.static import static


router = routers.DefaultRouter()
router.register(r'entities', views.NoteViewSet)
router.register(r'analyzeImage', views.AnalyzeViewSet)

urlpatterns = [
    url(r'^django-rq/', include('django_rq.urls')),
    url(r'^entities/(?P<img_uuid>[\w-]+)/$', views.NoteViewSet.as_view({
    'get': 'retrieve',
    'post': 'create',
    'delete': 'destroy',
}), name='notes-detail'),
    url(r'^', include(router.urls))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)