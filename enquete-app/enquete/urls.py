from django.urls import path

from . import views

urlpatterns = [
    path('list/', views.EnqueteListView.as_view(), name='enquete_list'),
]
