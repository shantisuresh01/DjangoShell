"""DjangoShell_djangoapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path, re_path, include
from DjangoShell_djangoapp.views import AboutTheProgramView, whereto
from django.contrib.auth.views import logout_then_login
from django.views.generic.base import RedirectView
from DjangoShell_djangoapp.views import LandingView, whereto

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django_registration.backends.activation.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    re_path(r'^logout/$', logout_then_login, name='logout'),
    re_path(r'^whereto$', whereto, name="whereto"),
    re_path(r'^about$', AboutTheProgramView.as_view(), {}, name="about"),
    re_path(r'session_security/', include('session_security.urls')),
    re_path(r'^$', RedirectView.as_view(url='welcome/', permanent=False)),
    re_path(r'^welcome/$(?i)', LandingView.as_view(), {}, name="landing_page"),


]
