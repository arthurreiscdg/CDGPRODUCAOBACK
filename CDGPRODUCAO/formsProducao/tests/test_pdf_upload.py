import os
import sys
import logging
from django.conf import settings
from django.utils import timezone

# Configura o ambiente Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from formsProducao.utils.drive import GoogleDriveService
from formsProducao.services.google_drive_service import BaseFormularioGoogleDriveService
from formsProducao.services.zerohum_service import ZeroHumService

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_drive_initialization():
    """Testa a inicialização do serviço do Google Drive"""
    logger.info("Testando inicialização do serviço do Google Drive...")
    drive_service = GoogleDriveService()
    if drive_service.service:
        logger.info("✅ Serviço do Google Drive inicializado com sucesso")
    else:
        logger.error("❌ Falha ao inicializar o serviço do Google Drive")

def test_folder_creation():
    """Testa a criação de uma pasta temporária de teste no Drive"""
    logger.info("Testando criação de pasta no Google Drive...")
    drive_service = GoogleDriveService()
    test_folder_name = f"test_folder_{timezone.now().strftime('%Y%m%d%H%M%S')}"
    folder_id = drive_service.create_folder(test_folder_name)
    
    if folder_id:
        logger.info(f"✅ Pasta de teste '{test_folder_name}' criada com ID: {folder_id}")
        return folder_id
    else:
        logger.error("❌ Falha ao criar pasta de teste")
        return None

def test_pdf_upload(folder_id=None):
    """Testa o upload de um arquivo PDF para o Google Drive"""
    logger.info("Testando upload de PDF para o Google Drive...")
    
    # Cria um arquivo PDF de teste
    test_pdf_path = os.path.join(settings.BASE_DIR, 'temp', 'test_upload.pdf')
    os.makedirs(os.path.dirname(test_pdf_path), exist_ok=True)
    
    # Cria um arquivo PDF simples para teste
    with open(test_pdf_path, 'wb') as f:
        # Um PDF válido mínimo
        f.write(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>\nendobj\nxref\n0 4\n0000000000 65535 f\n0000000018 00000 n\n0000000066 00000 n\n0000000122 00000 n\ntrailer\n<</Size 4/Root 1 0 R>>\nstartxref\n195\n%%EOF\n')
    
    drive_service = GoogleDriveService()
    result = drive_service.upload_pdf(
        test_pdf_path, 
        f"test_pdf_{timezone.now().strftime('%Y%m%d%H%M%S')}.pdf",
        folder_id
    )
    
    if result and 'download_link' in result:
        logger.info(f"✅ Upload de PDF bem sucedido")
        logger.info(f"   ID do arquivo: {result['file_id']}")
        logger.info(f"   Link de visualização: {result.get('web_link')}")
        logger.info(f"   Link de download: {result.get('download_link')}")
        
        # Tenta acessar o link de download para verificar se é válido
        import requests
        try:
            response = requests.head(result['download_link'], timeout=5)
            if response.status_code == 200 or response.status_code == 302:
                logger.info(f"✅ Link de download verificado e funcionando (status: {response.status_code})")
            else:
                logger.warning(f"⚠️ Link de download retornou status {response.status_code}")
        except Exception as e:
            logger.warning(f"⚠️ Não foi possível verificar o link de download: {str(e)}")
            
        # Limpa o arquivo de teste
        os.remove(test_pdf_path)
        return result
    else:
        logger.error("❌ Falha no upload do PDF")
        return None

def test_service_folder_setup():
    """Testa a configuração de pasta para um serviço específico"""
    logger.info("Testando configuração de pasta para o serviço ZeroHum...")
    
    folder_id = ZeroHumService.setup_pasta_drive()
    if folder_id:
        logger.info(f"✅ Pasta ZeroHum configurada com sucesso. ID: {folder_id}")
        return folder_id
    else:
        logger.error("❌ Falha ao configurar pasta ZeroHum")
        return None

if __name__ == "__main__":
    logger.info("Iniciando testes de upload de PDF para o Google Drive...")
    
    test_drive_initialization()
    
    folder_id = test_folder_creation()
    
    if folder_id:
        pdf_result = test_pdf_upload(folder_id)
    
    service_folder = test_service_folder_setup()
    
    if service_folder:
        pdf_service_result = test_pdf_upload(service_folder)
    
    logger.info("Testes concluídos!")
