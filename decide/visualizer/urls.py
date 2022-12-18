from django.urls import path
from .views import VisualizerView, VisualizerViewBinary, VisualizerViewScore

app_name= 'visualizer'

urlpatterns = [
    path('<int:voting_id>/', VisualizerView.as_view()),
    path('binaryVoting/<int:voting_id>/', VisualizerViewBinary.as_view()),
    path('scoreVoting/<int:voting_id>/', VisualizerViewScore.as_view()),
]
