"""
Script para verificar a conectividade do Google Drive no ambiente de produção.
Execute este script após a implantação para verificar se tudo está funcionando.
"""

import os
import sys
import django
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configura o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Importa os utilitários necessários
from formsProducao.utils.drive import GoogleDriveService

def verificar_drive():
    """
    Verifica se a conexão com o Google Drive está funcionando.
    """
    logger.info("=== Verificando conexão com o Google Drive ===")
    
    # Testa a conexão básica com o Drive
    drive_service = GoogleDriveService()
    
    if not drive_service.service:
        logger.error("FALHA: Não foi possível inicializar o serviço do Google Drive")
        return False
    
    # Tenta listar os arquivos/pastas
    try:
        results = drive_service.service.files().list(
            pageSize=10, 
            fields="nextPageToken, files(id, name)"
        ).execute()
        
        items = results.get('files', [])
        logger.info(f"Arquivos/pastas disponíveis no Google Drive: {len(items)}")
        
        for item in items:
            logger.info(f"- {item['name']} (ID: {item['id']})")
            
        if not items:
            logger.warning("Nenhum arquivo ou pasta encontrado no Google Drive")
            
        return True
    
    except Exception as e:
        logger.error(f"FALHA ao listar arquivos: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def verificar_pastas_formularios():
    """
    Verifica se as pastas para armazenamento de formulários estão configuradas.
    """
    logger.info("=== Verificando pastas de formulários ===")
    
    # Lista de serviços para verificar
    from formsProducao.services.zerohum_service import ZeroHumService
    
    # Verifica a pasta do ZeroHum
    zerohum_id = ZeroHumService.PASTA_ID
    if zerohum_id or ZeroHumService.setup_pasta_drive():
        logger.info(f"OK: Pasta ZeroHum configurada com ID: {ZeroHumService.PASTA_ID}")
    else:
        logger.error("FALHA: Não foi possível configurar a pasta ZeroHum")
    
    # Adicione aqui verificações para outras pastas conforme necessário

if __name__ == "__main__":
    logger.info("Iniciando verificação do ambiente de upload de arquivos...")
    
    # Verifica a conexão com o Drive
    if verificar_drive():
        logger.info("✓ Conexão com o Google Drive OK")
    else:
        logger.error("✘ Problemas na conexão com o Google Drive")
    
    # Verifica as pastas para formulários
    verificar_pastas_formularios()
    
    logger.info("Verificação concluída!")
