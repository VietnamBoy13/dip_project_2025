from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('home/', views.home, name='home'),
    path('reports/<int:run_id>/', views.report_view, name='report'),
    path('run-demo-test/', views.run_demo_test, name='run_demo_test'),
    path('accounts/', views.auth_view, name='auth'),
    path('logout/', LogoutView.as_view(next_page='auth'), name='logout'),
]
