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
import json

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_form_submission_with_view_link():
    """Testa o fluxo completo de envio de um formulário e verifica o link de visualização"""
    logger.info("Testando envio de formulário completo com link de visualização...")
    
    # Cria um arquivo PDF de teste
    test_pdf_path = os.path.join(settings.BASE_DIR, 'temp', 'test_form_view_link.pdf')
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
        'nome': f'Teste Web Link {timezone.now().strftime("%d/%m/%Y %H:%M:%S")}',
        'email': 'arthur.casadagrafica@gmail.com',
        'unidade_nome': 'Unidade Teste',
        'titulo': 'Documento de Teste Links',
        'data_entrega': timezone.now().date() + timezone.timedelta(days=7),
        'observacoes': 'Teste automático para verificar o link de visualização'
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
            logger.info(f"   Link de visualização: {formulario.web_view_link}")
            
            # Verifica se o link de visualização foi salvo corretamente
            if formulario.web_view_link:
                logger.info(f"✅ Link de visualização salvo no banco de dados")
                
                # Tenta acessar o link para verificar se é válido
                import requests
                try:
                    response = requests.head(formulario.web_view_link, timeout=5)
                    if response.status_code == 200:
                        logger.info(f"✅ Link de visualização verificado e funcionando (status: {response.status_code})")
                    else:
                        logger.warning(f"⚠️ Link de visualização retornou status {response.status_code}")
                except Exception as e:
                    logger.warning(f"⚠️ Não foi possível verificar o link de visualização: {str(e)}")
            else:
                logger.error("❌ O link de visualização não foi salvo no banco de dados")
            
            # Verifica o JSON
            if formulario.json_link:
                try:
                    json_data = json.loads(formulario.json_link)
                    if 'link_visualizacao' in json_data:
                        logger.info(f"✅ Link de visualização também está no JSON: {json_data['link_visualizacao']}")
                    else:
                        logger.error("❌ O JSON não contém o campo 'link_visualizacao'")
                except:
                    logger.error("❌ Não foi possível analisar o JSON")                # Verificando a pasta onde o arquivo foi salvo
            if formulario.web_view_link:
                logger.info(f"📁 Arquivo salvo no Google Drive e acessível via link: {formulario.web_view_link}")
                logger.info(f"   Pasta do formulário: {ZeroHumService.PASTA_NOME}")
                logger.info(f"   ID da pasta: {ZeroHumService.PASTA_ID}")
                logger.info(f"   Email do usuário que precisa ter acesso: arthur.casadagrafica@gmail.com")
                
                # Verificando as permissões do arquivo
                try:
                    # Extrair o ID do arquivo do link de visualização
                    import re
                    file_id_match = re.search(r'/d/([^/]+)', formulario.web_view_link)
                    if file_id_match:
                        file_id = file_id_match.group(1)
                        
                        # Verificar permissões
                        drive_service = GoogleDriveService()
                        permissions = drive_service.service.permissions().list(
                            fileId=file_id, 
                            fields="permissions(id, type, role, emailAddress)"
                        ).execute().get('permissions', [])
                        
                        logger.info(f"Permissões do arquivo:")
                        tem_acesso = False
                        for perm in permissions:
                            logger.info(f"   - {perm.get('type')} {perm.get('role')} {perm.get('emailAddress', 'N/A')}")
                            if (perm.get('type') == 'user' and 
                                perm.get('emailAddress', '') == 'arthur.casadagrafica@gmail.com'):
                                tem_acesso = True
                        
                        if tem_acesso:
                            logger.info("✅ O email arthur.casadagrafica@gmail.com tem permissão no arquivo")
                        else:
                            logger.warning("⚠️ O email arthur.casadagrafica@gmail.com NÃO tem permissão explícita no arquivo")
                            
                            # Adicionar permissão se não existir
                            logger.info("Adicionando permissão para arthur.casadagrafica@gmail.com...")
                            drive_service.service.permissions().create(
                                fileId=file_id,
                                body={'type': 'user', 'role': 'reader', 'emailAddress': 'arthur.casadagrafica@gmail.com'},
                                fields='id'
                            ).execute()
                            logger.info("✅ Permissão adicionada com sucesso")
                    else:
                        logger.error("❌ Não foi possível extrair o ID do arquivo do link de visualização")
                except Exception as e:
                    logger.error(f"❌ Erro ao verificar permissões: {str(e)}")
            
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
    logger.info("Iniciando teste de envio de formulário com link de visualização...")
    
    formulario = test_form_submission_with_view_link()
    
    logger.info("Teste concluído!")
