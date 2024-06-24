from django.urls import path
from . import views

urlpatterns = [
    path('montecarlo/', views.montecarlo, name='montecarlo'),
    path('api/montecarlo/', views.MontecarloExecute.as_view(), name='montecarloexecute'),
]
