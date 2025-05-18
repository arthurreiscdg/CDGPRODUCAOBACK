# filepath: c:\Users\Arthur Reis\Documents\PROJETOCASADAGRAFICA\CDGPRODUCAOBACK\CDGPRODUCAO\formsProducao\services\coleguium_service.py
import logging
from formsProducao.services.google_drive_service import BaseFormularioGoogleDriveService

logger = logging.getLogger(__name__)

class coleguiumService(BaseFormularioGoogleDriveService):
    """
    Serviço específico para o formulário coleguium
    """
    PASTA_ID = None
    PASTA_NOME = "coleguium"
    PREFIXO_COD_OP = "CL"
