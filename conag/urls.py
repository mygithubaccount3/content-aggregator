from django.urls import path
from .views import BbcView, CnnView, IndexView

app_name = 'conag'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('bbc', BbcView.as_view(), name='bbc'),
    path('cnn', CnnView.as_view(), name='cnn')
]