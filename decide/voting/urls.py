from django.urls import path
from . import views


urlpatterns = [
    path('', views.VotingView.as_view(), name='voting'),
    path('<int:voting_id>/', views.VotingUpdate.as_view(), name='voting'),
    path('', views.ScoreVotingView.as_view(), name='scoreVoting'),
    path('<int:voting_id>/', views.ScoreVotingUpdate.as_view(), name='scoreVoting'),
]
