from django.urls import path, include
from . import views



urlpatterns = [
    path('', views.indexCensus, name='index'),
    path('<int:voting_id>/', views.CensusDetail.as_view(), name='census_detail'),
    path('export/', views.first_view, name='census_export'),
    path('exportcsv/', views.exportcsv, name='export_csv'),
    path('exportjson/', views.exportjson, name='export_json'),
    path('exportxml/', views.exportxml, name='export_xml'),
    
    path('reuseCensusV2/V/', views.reuseCensusV2),
    path('reuseCensusV2/BV/', views.reuseCensusV2BV),
    path('reuseCensusV2/SV/', views.reuseCensusV2SV),
    path('censusForAll/V/', views.censusForAll),
    path('censusForAll/BV/', views.censusForAllBV),
    path('censusForAll/SV/', views.censusForAllSV),
    path('prueba', views.prueba),



    
]
