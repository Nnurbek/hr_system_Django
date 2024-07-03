from django.contrib import admin
from django.urls import path, include
from hr_system import views as hr_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('hr_system/', include('hr_system.urls')),
    path('accounts/login/', hr_views.custom_login, name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
]
