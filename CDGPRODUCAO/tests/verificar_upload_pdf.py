"""
Script para verificar e testar todas as funcionalidades de upload de PDF para o Google Drive.
Este script realiza uma verificação completa incluindo:
1. Validação das credenciais do Drive
2. Verificação da estrutura de pastas
3. Teste de upload de um PDF
4. Verificação dos links gerados
"""

import os
import sys
import django
import logging
from io import BytesIO
from datetime import datetime
from reportlab.pdfgen import canvas

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

def criar_pdf_teste():
    """
    Cria um arquivo PDF de teste com informações de data e hora.
    """
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf_buffer = BytesIO()
    
    # Criar o PDF usando ReportLab
    pdf = canvas.Canvas(pdf_buffer)
    pdf.setTitle("Arquivo de Teste")
    pdf.setFont("Helvetica", 16)
    pdf.drawString(100, 750, "Arquivo de Teste para Upload no Google Drive")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, 730, f"Gerado em: {agora}")
    pdf.drawString(100, 710, "Se você está vendo este arquivo, o teste de upload foi bem-sucedido!")
    pdf.save()
    
    # Retorna o buffer do PDF como bytes
    pdf_bytes = pdf_buffer.getvalue()
    pdf_buffer.close()
    
    return pdf_bytes

def testar_google_drive():
    """
    Testa a inicialização e conexão do Google Drive.
    """
    from formsProducao.utils.drive import GoogleDriveService
    
    logger.info("=== Testando conexão com Google Drive ===")
    
    drive_service = GoogleDriveService()
    if not drive_service.service:
        logger.error("❌ Serviço do Google Drive não foi inicializado corretamente")
        return False
    
    logger.info("✓ Serviço do Google Drive inicializado com sucesso")
    
    # Testar listagem de arquivos
    try:
        arquivos = drive_service.service.files().list(
            pageSize=10, 
            fields="nextPageToken, files(id, name)"
        ).execute()
        
        items = arquivos.get('files', [])
        logger.info(f"✓ {len(items)} arquivos/pastas encontrados no Google Drive")
    except Exception as e:
        logger.error(f"❌ Erro ao listar arquivos: {str(e)}")
        return False
    
    return True

def verificar_estrutura_pastas():
    """
    Verifica se as pastas necessárias existem no Google Drive.
    """
    from formsProducao.services.zerohum_service import ZeroHumService
    
    logger.info("=== Verificando estrutura de pastas ===")
    
    # Verificar pasta do ZeroHum
    pasta_id = ZeroHumService.setup_pasta_drive()
    if pasta_id:
        logger.info(f"✓ Pasta ZeroHum encontrada com ID: {pasta_id}")
        # Atualizar o ID da pasta no serviço
        ZeroHumService.PASTA_ID = pasta_id
        return True
    else:
        logger.error("❌ Pasta ZeroHum não encontrada e não foi possível criar")
        return False

def testar_upload_pdf():
    """
    Testa o upload de um arquivo PDF para o Google Drive.
    """
    from formsProducao.services.zerohum_service import ZeroHumService
    
    logger.info("=== Testando upload de PDF ===")
    
    # Criar um arquivo PDF de teste
    pdf_bytes = criar_pdf_teste()
    logger.info(f"✓ PDF de teste criado com {len(pdf_bytes)} bytes")
    
    # Criar um dicionário com dados de teste para o formulário
    dados_teste = {
        'nome': 'Usuário de Teste',
        'email': 'teste@exemplo.com',
        'titulo': 'Formulário de Teste',
        'data_entrega': '2023-12-31',
        'unidades': [
            {'nome': 'Unidade Teste 1', 'quantidade': 10},
            {'nome': 'Unidade Teste 2', 'quantidade': 5}
        ]
    }
    
    # Processar o formulário
    try:
        formulario = ZeroHumService.processar_formulario(dados_teste, pdf_bytes)
        
        if formulario:
            logger.info(f"✓ Formulário criado com código: {formulario.cod_op}")
            
            # Verificar se os links foram gerados
            if formulario.link_download and formulario.web_view_link:
                logger.info(f"✓ Links gerados com sucesso:")
                logger.info(f"  Link de download: {formulario.link_download}")
                logger.info(f"  Link de visualização: {formulario.web_view_link}")
                return True, formulario
            else:
                logger.error("❌ Links não foram gerados corretamente")
                logger.error(f"  Link de download: {formulario.link_download}")
                logger.error(f"  Link de visualização: {formulario.web_view_link}")
                return False, formulario
        else:
            logger.error("❌ Formulário não foi criado")
            return False, None
    except Exception as e:
        import traceback
        logger.error(f"❌ Erro ao processar formulário: {str(e)}")
        logger.error(traceback.format_exc())
        return False, None

def main():
    logger.info("===== INICIANDO TESTES DE UPLOAD DE PDF =====")
    
    # Etapa 1: Testar conexão com Google Drive
    if not testar_google_drive():
        logger.error("❌❌❌ Falha na conexão com o Google Drive. Abortando testes.")
        return
        
    # Etapa 2: Verificar estrutura de pastas
    if not verificar_estrutura_pastas():
        logger.error("❌❌❌ Falha na verificação da estrutura de pastas. Abortando testes.")
        return
    
    # Etapa 3: Testar upload de PDF
    resultado, formulario = testar_upload_pdf()
    
    if resultado:
        logger.info("✓✓✓ TODOS OS TESTES PASSARAM COM SUCESSO! ✓✓✓")
        logger.info(f"Um formulário de teste foi criado com o código: {formulario.cod_op}")
        logger.info(f"Você pode visualizar o PDF em: {formulario.web_view_link}")
    else:
        logger.error("❌❌❌ FALHA NOS TESTES DE UPLOAD DE PDF ❌❌❌")
        if formulario:
            logger.info(f"Um formulário foi parcialmente criado com o código: {formulario.cod_op}")
        logger.info("Revise os logs acima para identificar e corrigir o problema.")

if __name__ == "__main__":
    main()
