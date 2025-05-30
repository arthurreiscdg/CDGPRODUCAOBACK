import logging
from rest_framework.permissions import IsAuthenticated

from formsProducao.views.base_view import BaseFormularioView
from formsProducao.serializers import ZeroHumSerializer
from formsProducao.services import ZeroHumService

logger = logging.getLogger(__name__)

class ZeroHumView(BaseFormularioView):
    """
    View para gerenciar o formulário ZeroHum.
    Herda funcionalidades da BaseFormularioView.
    """
    serializer_class = ZeroHumSerializer
    service_class = ZeroHumService
    
    # Descomente a linha abaixo se quiser exigir autenticação
    # permission_classes = [IsAuthenticated]