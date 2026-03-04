from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('finance/', include('finance.urls')),
    path('assets/', include('assets.urls')),
    path('vehicles/', include('vehicles.urls')),
    path('notes/', include('notes.urls')),
]

# WhiteNoise handles /static/ in production via middleware.
# Django's dev server still needs the media helper for uploaded files (/media/).
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
