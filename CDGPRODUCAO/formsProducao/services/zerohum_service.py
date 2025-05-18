

import logging
from formsProducao.services.google_drive_service import BaseFormularioGoogleDriveService

logger = logging.getLogger(__name__)

class ZeroHumService(BaseFormularioGoogleDriveService):
    """
    Serviço específico para o formulário ZeroHum
    """
    PASTA_ID = None
    PASTA_NOME = "ZeroHum"
    PREFIXO_COD_OP = "ZH"
    
    # Métodos adicionais específicos para ZeroHum podem ser adicionados aqui
