import logging
from rest_framework.permissions import IsAuthenticated

from formsProducao.views.base_view import BaseFormularioView
from formsProducao.serializers import PensiSerializer
from formsProducao.services import PensiService

logger = logging.getLogger(__name__)

class PensiView(BaseFormularioView):
    """
    View para gerenciar o formulário Pensi.
    Herda funcionalidades da BaseFormularioView.
    """
    serializer_class = PensiSerializer
    service_class = PensiService
    
    # Descomente a linha abaixo se quiser exigir autenticação
    # permission_classes = [IsAuthenticated]