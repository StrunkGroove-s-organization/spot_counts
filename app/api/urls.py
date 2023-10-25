from django.urls import path
from . import views

urlpatterns = [
    path('inter-arbitrage/', views.Inter.as_view()),
    path('triangular-arbitrage/', views.Triangular.as_view()),
]
