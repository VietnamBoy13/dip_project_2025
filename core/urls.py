from django.urls import path
from .views import home, report_view, run_demo_test

urlpatterns = [
    path('', home, name='home'),
    path('reports/<int:run_id>/', report_view, name='report'),
    path('run-demo-test/', run_demo_test, name='run_demo_test'),
]
