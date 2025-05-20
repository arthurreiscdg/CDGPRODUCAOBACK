"""
Script para verificar os registros do formulário ZeroHum no banco de dados
e detectar qualquer inconsistência nos links do Google Drive.
"""

import os
import sys
import django
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurar caminho do projeto Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Inicializar o ambiente Django
django.setup()

def verificar_registros_banco():
    """
    Verifica os registros do formulário ZeroHum no banco de dados.
    """
    from formsProducao.models.formulario import Formulario
    
    logger.info("=== Verificando registros do formulário ZeroHum no banco de dados ===")
    
    # Obter todos os formulários
    formularios = Formulario.objects.all().order_by('-criado_em')
    
    if not formularios:
        logger.info("Nenhum formulário encontrado no banco de dados")
        return
    
    logger.info(f"Total de formulários: {len(formularios)}")
    
    # Verificar formulários sem links
    formularios_sem_links = formularios.filter(link_download__isnull=True) | formularios.filter(link_download='')
    if formularios_sem_links:
        logger.warning(f"❌ {formularios_sem_links.count()} formulários sem link de download")
        for form in formularios_sem_links:
            logger.warning(f"  - {form.cod_op} ({form.criado_em}) - {form.nome}")
    else:
        logger.info("✓ Todos os formulários têm link de download")
    
    # Verificar os 5 formulários mais recentes
    logger.info("=== 5 formulários mais recentes ===")
    for form in formularios[:5]:
        logger.info(f"Formulário: {form.cod_op}")
        logger.info(f"  Nome: {form.nome}")
        logger.info(f"  Data: {form.criado_em}")
        logger.info(f"  Link Download: {form.link_download if form.link_download else 'NÃO DISPONÍVEL'}")
        logger.info(f"  Link Visualização: {form.web_view_link if form.web_view_link else 'NÃO DISPONÍVEL'}")
        
        # Verificar unidades associadas
        unidades = form.unidades.all()
        if unidades:
            logger.info(f"  Unidades ({unidades.count()}):")
            for unidade in unidades:
                logger.info(f"    - {unidade.nome}: {unidade.quantidade}")
        else:
            logger.warning(f"  ❌ Nenhuma unidade associada a este formulário")
        
        logger.info("---")

def tentar_corrigir_links():
    """
    Tenta corrigir os links de formulários sem link de download.
    """
    from formsProducao.models.formulario import Formulario
    from formsProducao.services.zerohum_service import ZeroHumService
    from formsProducao.utils.drive import GoogleDriveService
    
    logger.info("=== Tentando corrigir formulários sem links ===")
    
    # Obter formulários sem links
    formularios_sem_links = Formulario.objects.filter(link_download__isnull=True) | Formulario.objects.filter(link_download='')
    
    if not formularios_sem_links:
        logger.info("✓ Não há formulários sem links para corrigir")
        return
    
    logger.info(f"Encontrados {formularios_sem_links.count()} formulários sem links")
    
    # Configurar o serviço do Google Drive
    drive_service = GoogleDriveService()
    if not drive_service.service:
        logger.error("❌ Não foi possível inicializar o serviço do Google Drive")
        return
    
    # Verificar se a pasta ZeroHum existe
    if ZeroHumService.PASTA_ID is None:
        pasta_id = ZeroHumService.setup_pasta_drive()
        if not pasta_id:
            logger.error("❌ Não foi possível configurar a pasta ZeroHum")
            return
        ZeroHumService.PASTA_ID = pasta_id
    
    # Tentar encontrar os arquivos no Google Drive pelos nomes esperados
    for form in formularios_sem_links:
        nome_arquivo = f"{ZeroHumService.PASTA_NOME}_{form.cod_op}.pdf"
        logger.info(f"Buscando arquivo '{nome_arquivo}' para o formulário {form.cod_op}")
        
        # Buscar o arquivo no Google Drive
        try:
            # Consulta para encontrar o arquivo por nome na pasta específica
            query = f"name='{nome_arquivo}' and '{ZeroHumService.PASTA_ID}' in parents and trashed=false"
            response = drive_service.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, webViewLink, webContentLink)'
            ).execute()
            
            files = response.get('files', [])
            if not files:
                logger.warning(f"❌ Arquivo '{nome_arquivo}' não encontrado no Google Drive")
                continue
                
            file = files[0]  # Pegar o primeiro arquivo encontrado
            file_id = file.get('id')
            
            logger.info(f"✓ Arquivo encontrado com ID: {file_id}")
            
            # Obter ou gerar os links
            web_view_link = file.get('webViewLink')
            download_link = file.get('webContentLink')
            
            # Se não tiver o link de download, criar manualmente
            if not download_link:
                download_link = f"https://drive.google.com/uc?export=download&id={file_id}"
                
            # Se não tiver o link de visualização, criar manualmente
            if not web_view_link:
                web_view_link = f"https://drive.google.com/file/d/{file_id}/view?usp=drivesdk"
            
            # Atualizar o formulário com os links
            form.link_download = download_link
            form.web_view_link = web_view_link
            form.save()
            
            logger.info(f"✓ Formulário {form.cod_op} atualizado com links do Google Drive")
            logger.info(f"  Link Download: {download_link}")
            logger.info(f"  Link Visualização: {web_view_link}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar arquivo '{nome_arquivo}': {str(e)}")
            continue

def main():
    logger.info("===== VERIFICAÇÃO DE REGISTROS DE FORMULÁRIOS =====")
    
    # Verificar registros no banco de dados
    verificar_registros_banco()
    
    # Perguntar se deseja tentar corrigir os links
    resposta = input("\nDeseja tentar corrigir os formulários sem links? (s/n): ")
    if resposta.lower() == 's':
        tentar_corrigir_links()
        
        # Verificar novamente após a correção
        logger.info("\n=== Verificando registros após tentativa de correção ===")
        verificar_registros_banco()
    
    logger.info("===== VERIFICAÇÃO CONCLUÍDA =====")

if __name__ == "__main__":
    main()
