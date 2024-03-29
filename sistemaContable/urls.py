"""sistemaContable URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from apps.contables import views
from django.contrib.auth.views import login, logout_then_login

urlpatterns = [
	#Urls Inicio
    url(r'^$', views.index, name='index'),

    #Urls Administrador
    url(r'^admin/', admin.site.urls),
    url(r'^', include('apps.contables.urls', namespace ="contable")),

    url(r'^accounts/login/$' , login,{'template_name':'Inicio/index2.html'}, name='login'),

    url(r'^cerrar/$' , logout_then_login, name='logout'),


]
