import os
import sys
import logging
import re
from django.conf import settings

# Configura o ambiente Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from formsProducao.utils.drive import GoogleDriveService
from formsProducao.models.formulario import Formulario

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def verificar_e_atualizar_permissoes():
    """
    Verifica e atualiza as permissões de todos os arquivos no Google Drive
    para garantir que o email arthur.casadagrafica@gmail.com tenha acesso.
    """
    email_alvo = 'arthur.casadagrafica@gmail.com'
    logger.info(f"Verificando e atualizando permissões para: {email_alvo}")
    
    # Inicializa o serviço do Google Drive
    drive_service = GoogleDriveService()
    if not drive_service.service:
        logger.error("Não foi possível inicializar o serviço do Google Drive.")
        return
    
    # Obter todos os formulários com link de visualização
    formularios = Formulario.objects.exclude(web_view_link__isnull=True).exclude(web_view_link='')
    logger.info(f"Encontrados {formularios.count()} formulários com links de visualização")
    
    # Contador para estatísticas
    total_processados = 0
    ja_tem_permissao = 0
    adicionadas_permissoes = 0
    falhas = 0
    
    for formulario in formularios:
        try:
            total_processados += 1
            logger.info(f"[{total_processados}/{formularios.count()}] Processando formulário {formulario.cod_op}")
            
            # Extrair o ID do arquivo do link de visualização
            file_id_match = re.search(r'/d/([^/]+)', formulario.web_view_link)
            if not file_id_match:
                logger.error(f"  ❌ Não foi possível extrair o ID do arquivo do link: {formulario.web_view_link}")
                falhas += 1
                continue
                
            file_id = file_id_match.group(1)
            logger.info(f"  📄 ID do arquivo: {file_id}")
            
            # Verificar permissões atuais
            try:
                permissions = drive_service.service.permissions().list(
                    fileId=file_id, 
                    fields="permissions(id, type, role, emailAddress)"
                ).execute().get('permissions', [])
                
                tem_acesso = False
                for perm in permissions:
                    if (perm.get('type') == 'user' and 
                        perm.get('emailAddress', '').lower() == email_alvo.lower()):
                        tem_acesso = True
                        break
                
                if tem_acesso:
                    logger.info(f"  ✅ O email {email_alvo} já tem permissão no arquivo")
                    ja_tem_permissao += 1
                else:
                    # Adicionar permissão
                    logger.info(f"  ⚠️ Adicionando permissão para {email_alvo}...")
                    drive_service.service.permissions().create(
                        fileId=file_id,
                        body={'type': 'user', 'role': 'reader', 'emailAddress': email_alvo},
                        fields='id'
                    ).execute()
                    logger.info(f"  ✅ Permissão adicionada com sucesso")
                    adicionadas_permissoes += 1
                    
            except Exception as e:
                logger.error(f"  ❌ Erro ao verificar/atualizar permissões: {str(e)}")
                falhas += 1
        
        except Exception as e:
            logger.error(f"Erro ao processar formulário {formulario.cod_op}: {str(e)}")
            falhas += 1
    
    # Exibir estatísticas finais
    logger.info("="*50)
    logger.info(f"Resumo da operação:")
    logger.info(f"  Total de formulários processados: {total_processados}")
    logger.info(f"  Já tinham permissão: {ja_tem_permissao}")
    logger.info(f"  Permissões adicionadas: {adicionadas_permissoes}")
    logger.info(f"  Falhas: {falhas}")
    logger.info("="*50)

if __name__ == "__main__":
    logger.info("Iniciando verificação e atualização de permissões...")
    verificar_e_atualizar_permissoes()
    logger.info("Processo concluído!")
