# filepath: c:\Users\Arthur Reis\Documents\PROJETOCASADAGRAFICA\CDGPRODUCAOBACK\CDGPRODUCAO\formsProducao\views\coleguium.py
import logging
from rest_framework.permissions import IsAuthenticated

from formsProducao.views.base_view import BaseFormularioView
from formsProducao.serializers.form_serializers import coleguiumSerializer
from formsProducao.services.form_services import coleguiumService

logger = logging.getLogger(__name__)

class coleguiumView(BaseFormularioView):
    """
    View para gerenciar o formulário coleguium.
    Herda funcionalidades da BaseFormularioView.
    """
    serializer_class = coleguiumSerializer
    service_class = coleguiumService
    
    # Descomente a linha abaixo se quiser exigir autenticação
    # permission_classes = [IsAuthenticated]