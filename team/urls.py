from django.urls import path
from . import views


urlpatterns = [
    path('', views.team, name='team'),
    path('<slug:department_slug>/', views.team, name='doctors_by_department'),
    path('<slug:department_slug>/<slug:doctor_slug>/', views.doctor_detail, name='doctor_detail'),
]
