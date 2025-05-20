"""
Script para testar o upload de PDF para o Google Drive usando o ZeroHumService.
Este script simula o envio de um formulário com um arquivo PDF.
"""

import os
import sys
import json
import logging
from django.conf import settings
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importa as configurações do Django e configura o ambiente
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

# Agora é seguro importar os modelos e serviços
from formsProducao.services.zerohum_service import ZeroHumService
from formsProducao.utils.drive import GoogleDriveService
from django.contrib.auth.models import User

def criar_pdf_teste():
    """
    Cria um arquivo PDF de teste para upload.
    """
    try:
        import fpdf
    except ImportError:
        logger.error("Biblioteca fpdf não está instalada. Instalando...")
        os.system("pip install fpdf")
        import fpdf
    
    pdf = fpdf.FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"PDF de Teste - ZeroHum", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Gerado em {django.utils.timezone.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='C')
    pdf.cell(200, 10, txt="Este é um arquivo de teste para verificar o upload no Google Drive", ln=True)
    
    # Salva o PDF em um arquivo temporário
    temp_file = os.path.join(settings.BASE_DIR, "temp_test.pdf")
    pdf.output(temp_file)
    
    logger.info(f"Arquivo PDF de teste criado em: {temp_file}")
    
    # Lê o conteúdo do arquivo para bytes
    with open(temp_file, "rb") as f:
        pdf_bytes = f.read()
    
    # Remove o arquivo temporário
    os.remove(temp_file)
    
    return pdf_bytes

def testar_upload_pdf():
    """
    Testa o upload de um PDF de teste usando o ZeroHumService.
    """
    try:
        # Carrega as variáveis de ambiente
        load_dotenv()
        
        # Verifica se as credenciais do Google Drive estão configuradas
        if not os.environ.get("GOOGLE_PRIVATE_KEY") or not os.environ.get("GOOGLE_CLIENT_EMAIL"):
            logger.error("Credenciais do Google Drive não configuradas. Verifique o arquivo .env")
            return False
        
        # Cria um arquivo PDF de teste
        pdf_bytes = criar_pdf_teste()
        
        # Cria dados de exemplo para o formulário
        dados_form = {
            "nome": "Usuário de Teste",
            "email": "teste@example.com",
            "titulo": "Formulário de Teste",
            "data_entrega": django.utils.timezone.now().date(),
            "observacoes": "Este é um teste automático",
            "formato": "A4",
            "cor_impressao": "PB",
            "impressao": "1_LADO",
            "unidades": [
                {"nome": "ARARUAMA", "quantidade": 1},
                {"nome": "CABO_FRIO", "quantidade": 2}
            ]
        }
        
        # Obtém um usuário para o teste (cria um se não existir)
        try:
            usuario = User.objects.get(username="usuario_teste")
        except User.DoesNotExist:
            usuario = User.objects.create_user(
                username="usuario_teste",
                email="teste@example.com",
                password="senha_segura"
            )
        
        # Testa conexão com o Google Drive
        drive_service = GoogleDriveService()
        if drive_service.service:
            logger.info("Conexão com o Google Drive estabelecida com sucesso.")
        else:
            logger.error("Falha ao conectar com o Google Drive API.")
            return False
        
        # Configura a pasta do ZeroHum no Drive
        pasta_id = ZeroHumService.setup_pasta_drive()
        logger.info(f"ID da pasta ZeroHum no Google Drive: {pasta_id}")
        
        # Processa o formulário com o arquivo PDF
        logger.info("Processando formulário de teste com arquivo PDF...")
        
        formulario = ZeroHumService.processar_formulario(
            dados_form=dados_form,
            arquivo_pdf=pdf_bytes,
            usuario=usuario
        )
        
        if formulario:
            logger.info(f"Formulário criado com ID: {formulario.id}")
            logger.info(f"Código de operação: {formulario.cod_op}")
            logger.info(f"Link de Download: {formulario.link_download}")
            logger.info(f"Link de Visualização: {formulario.web_view_link}")
            
            if formulario.link_download and formulario.web_view_link:
                logger.info("TESTE BEM-SUCEDIDO: Links gerados corretamente!")
                return True
            else:
                logger.error("FALHA: Links não foram gerados corretamente.")
                return False
        else:
            logger.error("FALHA: Formulário não foi criado.")
            return False
    
    except Exception as e:
        logger.error(f"Erro durante o teste: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    print("Testando o upload de PDF para o Google Drive usando ZeroHumService...")
    resultado = testar_upload_pdf()
    print(f"Teste concluído. Resultado: {'SUCESSO' if resultado else 'FALHA'}")
