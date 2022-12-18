from django.urls import path

from .views import BoothView, ScoreBoothView, BoothBinaryView



urlpatterns = [
    path('voting/<int:voting_id>/', BoothView.as_view()),

    path('scoreVoting/<int:voting_id>/', ScoreBoothView.as_view()),

    path('binaryVoting/<int:voting_id>/', BoothBinaryView.as_view()),

]
