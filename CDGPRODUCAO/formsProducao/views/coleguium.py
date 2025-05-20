# filepath: c:\Users\Arthur Reis\Documents\PROJETOCASADAGRAFICA\CDGPRODUCAOBACK\CDGPRODUCAO\formsProducao\views\coleguium.py
import logging
from rest_framework.permissions import IsAuthenticated

from formsProducao.views.base_view import BaseFormularioView
from formsProducao.serializers import coleguiumSerializer
from formsProducao.services import coleguiumService

logger = logging.getLogger(__name__)

class ColeguiumView(BaseFormularioView):
    """
    View para gerenciar o formulário Coleguium.
    Herda funcionalidades da BaseFormularioView.
    """
    serializer_class = coleguiumSerializer
    service_class = coleguiumService
    
    # Descomente a linha abaixo se quiser exigir autenticação
    # permission_classes = [IsAuthenticated]