from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # users (login / signup / redirect)
    path("", include("users.urls")),

    # teacher side
    path("questions/", include("questions.urls")),

    # student side
    path("exams/", include("exams.urls")),
]

# media files (uploads)
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
