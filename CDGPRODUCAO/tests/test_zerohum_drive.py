import os
import sys
import logging
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path

# Configurar o django para este script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

# Configurar o logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_zerohum_upload():
    """
    Testa o envio de um formulário ZeroHum com PDF para o Google Drive.
    """
    logger.info("=== Iniciando teste de upload de PDF do ZeroHum para o Google Drive ===")
    
    # URL da API
    url = "http://127.0.0.1:8000/api/formularios/zerohum/"
    
    # Gerar dados para o formulário
    data_entrega = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    
    # Preparar os dados do formulário
    form_data = {
        'nome': 'Teste Drive API',
        'email': 'teste@exemplo.com',
        'titulo': 'Formulário de Teste ZeroHum',
        'data_entrega': data_entrega,
        'formato': 'A4',
        'cor_impressao': 'PB',
        'impressao': '1_LADO',
        'observacoes': 'Teste de upload para o Google Drive via API',
        'unidades': json.dumps([
            {'nome': 'ARARUAMA', 'quantidade': 10},
            {'nome': 'CABO_FRIO', 'quantidade': 5}
        ])
    }
    
    # Arquivos para upload - criar um PDF simples de teste
    pdf_path = os.path.join(os.path.dirname(__file__), 'teste_pdf.pdf')
    
    # Verificar se o arquivo de teste existe, se não existir, podemos usar qualquer outro PDF no sistema
    if not os.path.exists(pdf_path):
        # Procurar por algum PDF existente no diretório "temp"
        temp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'temp')
        pdfs = [f for f in os.listdir(temp_dir) if f.endswith('.pdf')]
        if pdfs:
            pdf_path = os.path.join(temp_dir, pdfs[0])
            logger.info(f"Usando PDF existente: {pdf_path}")
        else:
            logger.error("Nenhum arquivo PDF encontrado para teste")
            return
    
    files = {
        'arquivo': ('teste.pdf', open(pdf_path, 'rb'), 'application/pdf')
    }
    
    # Fazer a requisição POST para a API
    try:
        logger.info("Enviando requisição para a API...")
        response = requests.post(url, data=form_data, files=files)
        
        # Verificar a resposta
        if response.status_code == 201:
            logger.info("Formulário enviado com sucesso!")
            response_data = response.json()
            logger.info(f"Código de operação: {response_data.get('cod_op', 'N/A')}")
            logger.info(f"Link de download: {response_data.get('link_download', 'N/A')}")
            logger.info(f"Link de visualização: {response_data.get('web_view_link', 'N/A')}")
            
            # Verificar se os links foram gerados
            if response_data.get('link_download') and response_data.get('web_view_link'):
                logger.info("SUCESSO: Links de download e visualização gerados corretamente.")
            else:
                logger.error("FALHA: Links de download e/ou visualização não foram gerados.")
        else:
            logger.error(f"FALHA: Código de status {response.status_code}")
            logger.error(f"Resposta: {response.text}")
    
    except Exception as e:
        logger.error(f"FALHA: Erro ao fazer requisição: {str(e)}")
        
    finally:
        # Fechar o arquivo
        files['arquivo'][1].close()
    
    logger.info("=== Teste finalizado ===")
    
if __name__ == "__main__":
    test_zerohum_upload()
