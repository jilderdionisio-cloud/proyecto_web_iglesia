from django.urls import path
from .views import ChurchProfileView
urlpatterns=[path('church-profile/',ChurchProfileView.as_view(),name='church-profile')]
