from django.urls import path
from . import views

urlpatterns = [
    path('registrations/', views.RegistrationListView.as_view(), name='registrations-list'),
    path('registrations/create/', views.RegistrationCreateView.as_view(), name='registrations-create'),
    path('winners/', views.CategoryWinnersView.as_view(), name='winners'),
    path('statistics/', views.StatisticsView.as_view(), name='statistics'),
    path('event/date/', views.EventDateUpdateView.as_view(), name='event-date'),
]