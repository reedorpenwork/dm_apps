from django.urls import path
from . import views

app_name = 'shiny'

urlpatterns = [
    path('', views.IndexTemplateView.as_view(), name="index"),

]
