from django.urls import path
from . import views


urlpatterns = [
   

    path('', views.VotingView.as_view(), name='voting'),
    path('<int:voting_id>/', views.VotingUpdate.as_view(), name='voting'),


    path('votingbinary/', views.VotingBinaryView.as_view(), name='votingbinary'),
    path('votingbinary/<int:voting_id>/', views.VotingBinaryUpdate.as_view(), name='votingbinary'),
    
    path('scoreVoting/', views.ScoreVotingView.as_view(), name='scoreVoting'),
    path('scoreVoting/<int:voting_id>/', views.ScoreVotingUpdate.as_view(), name='scoreVoting')

]
