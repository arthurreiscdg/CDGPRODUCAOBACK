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

def test_form_update():
    """Testa a atualização de um formulário existente"""
    logger.info("Testando atualização de formulário...")
    
    # Primeiro, obtém o último formulário criado para teste
    try:
        formulario = Formulario.objects.filter(cod_op__startswith='ZH').order_by('-criado_em').first()
        
        if not formulario:
            logger.error("❌ Não foi encontrado nenhum formulário para teste")
            return None
            
        logger.info(f"✅ Formulário encontrado para teste: {formulario.cod_op}")
        logger.info(f"   Link de download atual: {formulario.link_download}")
        
        # Cria um arquivo PDF de teste
        test_pdf_path = os.path.join(settings.BASE_DIR, 'temp', 'test_update.pdf')
        os.makedirs(os.path.dirname(test_pdf_path), exist_ok=True)
        
        # Cria um arquivo PDF simples para teste
        with open(test_pdf_path, 'wb') as f:
            # Um PDF válido mínimo com conteúdo diferente
            f.write(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>\nendobj\nxref\n0 4\n0000000000 65535 f\n0000000018 00000 n\n0000000066 00000 n\n0000000122 00000 n\ntrailer\n<</Size 4/Root 1 0 R>>\nstartxref\n195\n%%EOF\nTHIS IS AN UPDATED FILE\n')
        
        # Lê o arquivo PDF
        with open(test_pdf_path, 'rb') as f:
            pdf_content = f.read()
        
        # Dados atualizados
        dados_atualizados = {
            'titulo': f'Título atualizado em {timezone.now().strftime("%d/%m/%Y %H:%M:%S")}',
            'observacoes': 'Observações atualizadas no teste'
        }
        
        # Atualiza o formulário
        formulario_atualizado = ZeroHumService.atualizar_formulario(
            formulario,
            dados_atualizados,
            pdf_content
        )
        
        if formulario_atualizado:
            logger.info(f"✅ Formulário atualizado com sucesso")
            logger.info(f"   Novo título: {formulario_atualizado.titulo}")
            logger.info(f"   Novo link de download: {formulario_atualizado.link_download}")
            
            # Verifica se o link foi atualizado corretamente
            if formulario_atualizado.link_download != formulario.link_download:
                logger.info(f"✅ Link de download foi atualizado")
                
                # Tenta acessar o link para verificar se é válido
                import requests
                try:
                    response = requests.head(formulario_atualizado.link_download, timeout=5)
                    if response.status_code == 200 or response.status_code == 302 or response.status_code == 303:
                        logger.info(f"✅ Link de download verificado e funcionando (status: {response.status_code})")
                    else:
                        logger.warning(f"⚠️ Link de download retornou status {response.status_code}")
                except Exception as e:
                    logger.warning(f"⚠️ Não foi possível verificar o link de download: {str(e)}")
            else:
                logger.warning("⚠️ O link de download não foi atualizado")
            
            # Verifica o JSON
            if formulario_atualizado.json_link:
                import json
                try:
                    json_data = json.loads(formulario_atualizado.json_link)
                    if 'link_pdf' in json_data:
                        logger.info(f"✅ Link de download também está no JSON: {json_data['link_pdf']}")
                        if json_data['link_pdf'] == formulario_atualizado.link_download:
                            logger.info(f"✅ Link no JSON é igual ao link no formulário")
                        else:
                            logger.warning(f"⚠️ Link no JSON ({json_data['link_pdf']}) é diferente do link no formulário ({formulario_atualizado.link_download})")
                    else:
                        logger.error("❌ O JSON não contém o campo 'link_pdf'")
                except:
                    logger.error("❌ Não foi possível analisar o JSON")
            
            return formulario_atualizado
        else:
            logger.error("❌ Falha ao atualizar o formulário")
            return None
    except Exception as e:
        logger.error(f"❌ Erro ao testar atualização de formulário: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None
    finally:
        # Limpa o arquivo de teste
        if os.path.exists(test_pdf_path):
            os.remove(test_pdf_path)

if __name__ == "__main__":
    logger.info("Iniciando teste de atualização de formulário...")
    
    formulario = test_form_update()
    
    logger.info("Teste concluído!")
