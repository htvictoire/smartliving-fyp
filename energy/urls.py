from django.urls import path
from . import views
from .views import EnergyReportView, EnergyReportJsonView
urlpatterns = [
    path('notif/', views.notif, name='notif'),
    path('report/', EnergyReportView.as_view(), name='energy_report'),
    
    path('report/json/', EnergyReportJsonView.as_view(), name='energy_report_json')
]


