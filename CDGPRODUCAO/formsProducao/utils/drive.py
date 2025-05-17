from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class GoogleDriveService:
    """
    Serviço para integração com o Google Drive API.
    """
    def __init__(self):
        self.credentials = None
        self.service = None
        self.initialize_service()

    def initialize_service(self):
        """
        Inicializa o serviço do Google Drive usando o arquivo de credenciais.
        """
        try:
            # Caminho para o arquivo de credenciais do serviço do Google Drive
            credentials_path = os.path.join(settings.BASE_DIR, 'credentials', 'google_drive_credentials.json')
            
            # Verifica se o arquivo de credenciais existe
            if not os.path.exists(credentials_path):
                logger.error(f"Arquivo de credenciais não encontrado em: {credentials_path}")
                return
            
            # Escopo necessário para acesso ao Drive
            SCOPES = ['https://www.googleapis.com/auth/drive']
            
            # Carrega as credenciais
            self.credentials = service_account.Credentials.from_service_account_file(
                credentials_path, scopes=SCOPES)
                
            # Constrói o serviço
            self.service = build('drive', 'v3', credentials=self.credentials)
            logger.info("Serviço do Google Drive inicializado com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao inicializar o serviço do Google Drive: {str(e)}")
            raise

    def upload_pdf(self, file_path, file_name, folder_id=None):
        """
        Faz upload de um arquivo PDF para o Google Drive.
        
        Args:
            file_path (str): Caminho local do arquivo PDF
            file_name (str): Nome do arquivo no Google Drive
            folder_id (str, optional): ID da pasta no Google Drive. Se não fornecido, 
                                      faz upload para a raiz.
        
        Returns:
            dict: Informações do arquivo enviado, incluindo o ID e link
        """
        try:
            if not self.service:
                self.initialize_service()
                if not self.service:
                    logger.error("Não foi possível inicializar o serviço do Google Drive.")
                    return None
            
            file_metadata = {
                'name': file_name,
                'mimeType': 'application/pdf',
            }
            
            # Se um folder_id for fornecido, defina-o como o pai do arquivo
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            # Cria MediaFileUpload para o arquivo
            media = MediaFileUpload(file_path, mimetype='application/pdf', resumable=True)
            
            # Cria o arquivo no Google Drive
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()
            
            logger.info(f"Arquivo {file_name} enviado com sucesso para o Google Drive. ID: {file.get('id')}")
            
            # Configura permissões para tornar o arquivo acessível por link
            self.service.permissions().create(
                fileId=file.get('id'),
                body={'type': 'anyone', 'role': 'reader'},
                fields='id'
            ).execute()
            
            return {
                'file_id': file.get('id'),
                'web_link': file.get('webViewLink')
            }
        
        except Exception as e:
            logger.error(f"Erro ao fazer upload do arquivo para o Google Drive: {str(e)}")
            return None

    def get_folders(self, parent_id=None):
        """
        Lista todas as pastas em um diretório específico ou na raiz.
        
        Args:
            parent_id (str, optional): ID da pasta pai. Se não fornecido, lista pastas na raiz.
            
        Returns:
            list: Lista de dicionários contendo informações das pastas (id, name)
        """
        try:
            if not self.service:
                self.initialize_service()
                if not self.service:
                    return []
                
            query = "mimeType='application/vnd.google-apps.folder'"
            
            if parent_id:
                query += f" and '{parent_id}' in parents"
                
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields="files(id, name)"
            ).execute()
            
            return results.get('files', [])
            
        except Exception as e:
            logger.error(f"Erro ao listar pastas no Google Drive: {str(e)}")
            return []
    
    def create_folder(self, folder_name, parent_id=None):
        """
        Cria uma nova pasta no Google Drive.
        
        Args:
            folder_name (str): Nome da nova pasta
            parent_id (str, optional): ID da pasta pai onde a nova pasta será criada
            
        Returns:
            str: ID da pasta criada, ou None em caso de falha
        """
        try:
            if not self.service:
                self.initialize_service()
                if not self.service:
                    return None
                
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_id:
                file_metadata['parents'] = [parent_id]
                
            folder = self.service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()
            
            return folder.get('id')
            
        except Exception as e:
            logger.error(f"Erro ao criar pasta no Google Drive: {str(e)}")
            return None