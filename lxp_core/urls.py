"""
URL configuration for lxp_core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # API endpoints
    path('api/v1/accounts/', include('accounts.urls')),
    path('api/v1/communities/', include('communities.urls')),
    path('api/v1/content/', include('content.urls')),
    path('api/v1/social/', include('social.urls')),
    path('api/v1/assessments/', include('assessments.urls')),
    path('api/v1/xapi/', include('xapi_integration.urls')),
    path('api/v1/ai/', include('ai_services.urls')),
    path('api/v1/analytics/', include('analytics.urls')),
]

