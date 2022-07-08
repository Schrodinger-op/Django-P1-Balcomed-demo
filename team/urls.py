from django.urls import path
from . import views


urlpatterns = [
    path('', views.team, name='team'),
    path('department/<slug:department_slug>/', views.team, name='doctors_by_department'),
    path('department/<slug:department_slug>/<slug:doctor_slug>/', views.doctor_detail, name='doctor_detail'),
    path('search/', views.search, name='search'),
]
