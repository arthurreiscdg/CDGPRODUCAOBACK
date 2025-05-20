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
        Inicializa o serviço do Google Drive usando as credenciais do arquivo .env.
        """
        try:
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
            
            # Log para verificar se as credenciais estão sendo carregadas corretamente
            if not credentials_dict["private_key"] or not credentials_dict["client_email"]:
                logger.error("Credenciais do Google Drive não foram carregadas corretamente do arquivo .env")
                logger.error(f"Private Key disponível: {'Sim' if credentials_dict['private_key'] else 'Não'}")
                logger.error(f"Client Email disponível: {'Sim' if credentials_dict['client_email'] else 'Não'}")
                return
                
            # Carrega as credenciais a partir do dicionário
            self.credentials = service_account.Credentials.from_service_account_info(
                credentials_dict, scopes=SCOPES)
                
            # Constrói o serviço
            self.service = build('drive', 'v3', credentials=self.credentials)
            logger.info("Serviço do Google Drive inicializado com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao inicializar o serviço do Google Drive: {str(e)}")
            # Detalhar o erro para facilitar o diagnóstico
            import traceback
            logger.error(traceback.format_exc())
    def upload_pdf(self, file_path, file_name, folder_id=None):
        """
        Faz upload de um arquivo PDF para o Google Drive e configura as permissões adequadas.
        
        Args:
            file_path (str): Caminho local do arquivo PDF
            file_name (str): Nome do arquivo no Google Drive
            folder_id (str, optional): ID da pasta no Google Drive. Se não fornecido, 
                                      faz upload para a raiz.
        
        Returns:
            dict: Informações do arquivo enviado, incluindo ID e links
        
        Raises:
            Exception: Se houver qualquer erro durante o processo de upload
        """
        if not self.service:
            self.initialize_service()
            if not self.service:
                raise Exception("Não foi possível inicializar o serviço do Google Drive.")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        try:
            # Preparar metadados do arquivo
            file_metadata = {
                'name': file_name,
                'mimeType': 'application/pdf'
            }
            
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            # Configurar upload
            media = MediaFileUpload(
                file_path,
                mimetype='application/pdf',
                resumable=True,
                chunksize=1024*1024  # 1MB por chunk para melhor controle
            )
            
            # Criar arquivo no Drive com todos os campos necessários
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink, webContentLink, name, mimeType, size, createdTime, modifiedTime',
                supportsAllDrives=True
            ).execute()
            
            file_id = file.get('id')
            if not file_id:
                raise Exception("Upload falhou: não foi possível obter o ID do arquivo")
            
            # Configurar permissões
            permissions = [
                {'type': 'anyone', 'role': 'reader'},  # Acesso público para leitura
                {
                    'type': 'user',
                    'role': 'writer',
                    'emailAddress': 'arthur.casadagrafica@gmail.com'
                }  # Acesso de edição para o email específico
            ]
            
            for permission in permissions:
                self.service.permissions().create(
                    fileId=file_id,
                    body=permission,
                    fields='id',
                    sendNotificationEmail=False
                ).execute()
            
            # Gerar e verificar links
            web_view_link = file.get('webViewLink')
            web_content_link = file.get('webContentLink')
            
            # Link alternativo de download (mais confiável)
            download_link = f"https://drive.google.com/uc?export=download&id={file_id}"
            
            # Log dos links gerados
            logger.info(f"Upload do arquivo {file_name} concluído com sucesso")
            logger.info(f"ID: {file_id}")
            logger.info(f"View Link: {web_view_link}")
            logger.info(f"Download Link: {download_link}")
            
            # Retornar todas as informações relevantes
            return {
                'id': file_id,
                'name': file.get('name'),
                'mimeType': file.get('mimeType'),
                'size': file.get('size'),
                'createdTime': file.get('createdTime'),
                'modifiedTime': file.get('modifiedTime'),
                'webContentLink': web_content_link or download_link,
                'webViewLink': web_view_link,
                'downloadLink': download_link
            }
        
        except Exception as e:
            logger.error(f"Erro ao fazer upload do arquivo para o Google Drive: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
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
            
            folder_id = folder.get('id')
            
            # Adiciona permissão específica para o email arthur.casadagrafica@gmail.com
            self.service.permissions().create(
                fileId=folder_id,
                body={'type': 'user', 'role': 'reader', 'emailAddress': 'arthur.casadagrafica@gmail.com'},
                fields='id'
            ).execute()
            
            return folder_id
            
        except Exception as e:
            logger.error(f"Erro ao criar pasta no Google Drive: {str(e)}")
            return None
