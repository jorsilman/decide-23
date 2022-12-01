from django.urls import path
from .views import BoothBinaryView, BoothView


urlpatterns = [
    path('<int:voting_id>/', BoothView.as_view()),
    path('binaryVoting/<int:voting_id>/', BoothBinaryView.as_view()),

]
