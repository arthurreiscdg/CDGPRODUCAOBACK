import logging
from rest_framework.permissions import IsAuthenticated

from formsProducao.views.base_view import BaseFormularioView
from formsProducao.serializers import EliteSerializer
from formsProducao.services import EliteService

logger = logging.getLogger(__name__)

class EliteView(BaseFormularioView):
    """
    View para gerenciar o formulário Elite.
    Herda funcionalidades da BaseFormularioView.
    """
    serializer_class = EliteSerializer
    service_class = EliteService
    
    # Descomente a linha abaixo se quiser exigir autenticação
    # permission_classes = [IsAuthenticated]