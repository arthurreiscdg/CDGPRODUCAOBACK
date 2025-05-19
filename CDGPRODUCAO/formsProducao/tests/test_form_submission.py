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
from formsProducao.services.zerohum_service import ZeroHumService
from formsProducao.models.formulario import Formulario

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_form_submission():
    """Testa o fluxo completo de envio de um formulário"""
    logger.info("Testando envio de formulário completo...")
    
    # Cria um arquivo PDF de teste
    test_pdf_path = os.path.join(settings.BASE_DIR, 'temp', 'test_form.pdf')
    os.makedirs(os.path.dirname(test_pdf_path), exist_ok=True)
    
    # Cria um arquivo PDF simples para teste
    with open(test_pdf_path, 'wb') as f:
        # Um PDF válido mínimo
        f.write(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>\nendobj\nxref\n0 4\n0000000000 65535 f\n0000000018 00000 n\n0000000066 00000 n\n0000000122 00000 n\ntrailer\n<</Size 4/Root 1 0 R>>\nstartxref\n195\n%%EOF\n')
    
    # Lê o arquivo PDF
    with open(test_pdf_path, 'rb') as f:
        pdf_content = f.read()
    
    # Dados do formulário
    form_data = {
        'nome': f'Teste Automático {timezone.now().strftime("%d/%m/%Y %H:%M:%S")}',
        'email': 'teste@exemplo.com',
        'unidade_nome': 'Unidade Teste',
        'titulo': 'Documento de Teste',
        'data_entrega': timezone.now().date() + timezone.timedelta(days=7),
        'observacoes': 'Teste automático de submissão de formulário e upload de PDF'
    }
    
    try:
        # Processa o formulário
        formulario = ZeroHumService.processar_formulario(
            form_data,
            pdf_content
        )
        
        if formulario:
            logger.info(f"✅ Formulário processado com sucesso")
            logger.info(f"   Código de operação: {formulario.cod_op}")
            logger.info(f"   Link de download: {formulario.link_download}")
            
            # Verifica se o link foi salvo corretamente
            if formulario.link_download:
                logger.info(f"✅ Link de download salvo no banco de dados")
                
                # Tenta acessar o link para verificar se é válido
                import requests
                try:
                    response = requests.head(formulario.link_download, timeout=5)
                    if response.status_code == 200 or response.status_code == 302:
                        logger.info(f"✅ Link de download verificado e funcionando (status: {response.status_code})")
                    else:
                        logger.warning(f"⚠️ Link de download retornou status {response.status_code}")
                except Exception as e:
                    logger.warning(f"⚠️ Não foi possível verificar o link de download: {str(e)}")
            else:
                logger.error("❌ O link de download não foi salvo no banco de dados")
            
            # Verifica o JSON
            if formulario.json_link:
                import json
                try:
                    json_data = json.loads(formulario.json_link)
                    if 'link_pdf' in json_data:
                        logger.info(f"✅ Link de download também está no JSON: {json_data['link_pdf']}")
                    else:
                        logger.error("❌ O JSON não contém o campo 'link_pdf'")
                except:
                    logger.error("❌ Não foi possível analisar o JSON")
            
            return formulario
        else:
            logger.error("❌ Falha ao processar o formulário")
            return None
    except Exception as e:
        logger.error(f"❌ Erro ao testar envio de formulário: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None
    finally:
        # Limpa o arquivo de teste
        if os.path.exists(test_pdf_path):
            os.remove(test_pdf_path)

if __name__ == "__main__":
    logger.info("Iniciando teste de envio de formulário...")
    
    formulario = test_form_submission()
    
    logger.info("Teste concluído!")
