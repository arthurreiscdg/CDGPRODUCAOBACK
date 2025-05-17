# filepath: c:\Users\Arthur Reis\Documents\PROJETOCASADAGRAFICA\CDGPRODUCAOBACK\CDGPRODUCAO\formsProducao\urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from formsProducao.views.zerohum import ZeroHumView
from formsProducao.views.pensi import PensiView
from formsProducao.views.elite import EliteView
from formsProducao.views.coleguium import coleguiumView

urlpatterns = [
    # Rotas para o formulário ZeroHum
    path('zerohum/', ZeroHumView.as_view(), name='zerohum-formulario'),
    path('zerohum/<str:cod_op>/', ZeroHumView.as_view(), name='zerohum-detalhe'),
    
    # Rotas para o formulário Pensi
    path('pensi/', PensiView.as_view(), name='pensi-formulario'),
    path('pensi/<str:cod_op>/', PensiView.as_view(), name='pensi-detalhe'),
    
    # Rotas para o formulário Elite
    path('elite/', EliteView.as_view(), name='elite-formulario'),
    path('elite/<str:cod_op>/', EliteView.as_view(), name='elite-detalhe'),
    
    # Rotas para o formulário coleguium
    path('coleguium/', coleguiumView.as_view(), name='coleguium-formulario'),
    path('coleguium/<str:cod_op>/', coleguiumView.as_view(), name='coleguium-detalhe'),
]