from django.urls import path
from . import views

app_name = 'conag'

urlpatterns = [
    # path('', views.index, name='index'),
    path('/bbc', views.bbc, name='bbc'),
    path('/cnn', views.cnn, name='cnn')
]