

import logging
from formsProducao.services.google_drive_service import BaseFormularioGoogleDriveService

logger = logging.getLogger(__name__)

class PensiService(BaseFormularioGoogleDriveService):
    """
    Serviço específico para o formulário Pensi
    """
    PASTA_ID = None
    PASTA_NOME = "Pensi"
    PREFIXO_COD_OP = "PS"
    
    # Métodos adicionais específicos para Pensi podem ser adicionados aqui
