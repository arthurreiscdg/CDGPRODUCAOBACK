"""
Script para testar a conexão com o Google Drive API.
Este script verifica se as credenciais estão configuradas corretamente.
"""

import os
import json
import logging
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def testar_conexao_drive():
    """
    Testa a conexão com o Google Drive API usando as credenciais do arquivo .env
    """
    try:
        # Carrega as variáveis de ambiente
        load_dotenv()
        
        # Escopo necessário para acesso ao Drive
        SCOPES = ['https://www.googleapis.com/auth/drive']
        
        # Cria o dict de credenciais a partir das variáveis de ambiente
        credentials_dict = {
            "type": os.environ.get("GOOGLE_SERVICE_ACCOUNT_TYPE"),
            "project_id": os.environ.get("GOOGLE_PROJECT_ID"),
            "private_key_id": os.environ.get("GOOGLE_PRIVATE_KEY_ID"),
            "private_key": os.environ.get("GOOGLE_PRIVATE_KEY").replace('\\n', '\n'),
            "client_email": os.environ.get("GOOGLE_CLIENT_EMAIL"),
            "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
            "auth_uri": os.environ.get("GOOGLE_AUTH_URI"),
            "token_uri": os.environ.get("GOOGLE_TOKEN_URI"),
            "auth_provider_x509_cert_url": os.environ.get("GOOGLE_AUTH_PROVIDER_X509_CERT_URL"),
            "client_x509_cert_url": os.environ.get("GOOGLE_CLIENT_X509_CERT_URL"),
            "universe_domain": os.environ.get("GOOGLE_UNIVERSE_DOMAIN")
        }
        
        # Imprime as informações de credenciais (ocultando a chave privada)
        for key, value in credentials_dict.items():
            if key == "private_key":
                logger.info(f"{key}: [OCULTO PARA SEGURANÇA]")
                logger.info(f"private_key comprimento: {len(str(value)) if value else 'VAZIO'}")
            else:
                logger.info(f"{key}: {value}")
        
        # Verificar se temos as credenciais mínimas necessárias
        if not credentials_dict["private_key"] or not credentials_dict["client_email"]:
            logger.error("Credenciais do Google Drive não foram carregadas corretamente do arquivo .env")
            logger.error(f"Private Key disponível: {'Sim' if credentials_dict['private_key'] else 'Não'}")
            logger.error(f"Client Email disponível: {'Sim' if credentials_dict['client_email'] else 'Não'}")
            return False
            
        # Carrega as credenciais a partir do dicionário
        credentials = service_account.Credentials.from_service_account_info(
            credentials_dict, scopes=SCOPES)
            
        # Constrói o serviço
        service = build('drive', 'v3', credentials=credentials)
        logger.info("Serviço do Google Drive inicializado com sucesso.")
        
        # Tenta listar os arquivos para verificar se a conexão está funcionando
        results = service.files().list(
            pageSize=10, 
            fields="nextPageToken, files(id, name)"
        ).execute()
        
        items = results.get('files', [])
        
        logger.info(f"Arquivos/pastas disponíveis no Google Drive: {len(items)}")
        for item in items:
            logger.info(f"- {item['name']} (ID: {item['id']})")
        
        # Cria uma pasta de teste
        folder_metadata = {
            'name': 'Pasta_Teste_CDG',
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        folder = service.files().create(
            body=folder_metadata,
            fields='id'
        ).execute()
        
        folder_id = folder.get('id')
        logger.info(f"Pasta de teste criada com ID: {folder_id}")
            
        # Cria um arquivo de teste na pasta
        with open("teste_upload.txt", "w") as f:
            f.write("Este é um arquivo de teste para upload no Google Drive.")
        
        file_metadata = {
            'name': 'teste_upload.txt',
            'parents': [folder_id]
        }
        
        media = MediaFileUpload(
            "teste_upload.txt", 
            mimetype='text/plain',
            resumable=True
        )
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink, webContentLink'
        ).execute()
        
        file_id = file.get('id')
        web_view_link = file.get('webViewLink')
        download_link = file.get('webContentLink') or f"https://drive.google.com/uc?export=download&id={file_id}"
        
        logger.info(f"Arquivo de teste criado com ID: {file_id}")
        logger.info(f"Link de visualização: {web_view_link}")
        logger.info(f"Link de download: {download_link}")
        
        # Configura permissões para tornar o arquivo acessível por link
        service.permissions().create(
            fileId=file_id,
            body={'type': 'anyone', 'role': 'reader'},
            fields='id'
        ).execute()
        
        logger.info("Permissões de acesso configuradas.")
        
        return True
    
    except Exception as e:
        logger.error(f"Erro ao testar conexão com o Google Drive: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    
    finally:
        # Limpa os arquivos de teste locais
        if os.path.exists("teste_upload.txt"):
            os.remove("teste_upload.txt")

if __name__ == "__main__":
    print("Testando a conexão com o Google Drive...")
    resultado = testar_conexao_drive()
    print(f"Teste concluído. Resultado: {'SUCESSO' if resultado else 'FALHA'}")
