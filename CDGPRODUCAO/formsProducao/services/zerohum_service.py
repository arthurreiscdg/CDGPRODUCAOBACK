import logging
import os
import uuid
import json
import traceback
from django.conf import settings
from django.utils import timezone
from formsProducao.services.google_drive_service import BaseFormularioGoogleDriveService
from formsProducao.models.formulario import Formulario
from formsProducao.models.unidade import Unidade
from formsProducao.models.arquivopdf import ArquivoPDF
from formsProducao.utils.drive import GoogleDriveService

logger = logging.getLogger(__name__)

class ZeroHumService(BaseFormularioGoogleDriveService):
    """
    Serviço específico para o formulário ZeroHum
    """
    PASTA_ID = None
    PASTA_NOME = "ZeroHum"
    PREFIXO_COD_OP = "ZH"
    @classmethod
    def setup_pasta_drive(cls):
        """
        Configura a pasta no Google Drive para armazenar os arquivos do formulário.
        Se a pasta não existir, ela será criada.
        """
        try:
            drive_service = GoogleDriveService()
            
            # Procurar pela pasta usando o nome
            query = f"name = '{cls.PASTA_NOME}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
            results = drive_service.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)',
                supportsAllDrives=True
            ).execute()
            
            folders = results.get('files', [])
            
            if folders:
                # Usa a primeira pasta encontrada
                cls.PASTA_ID = folders[0]['id']
                logger.info(f"Pasta {cls.PASTA_NOME} encontrada no Drive. ID: {cls.PASTA_ID}")
            else:
                # Cria a pasta se não existir
                folder_metadata = {
                    'name': cls.PASTA_NOME,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                
                folder = drive_service.service.files().create(
                    body=folder_metadata,
                    fields='id',
                    supportsAllDrives=True
                ).execute()
                
                cls.PASTA_ID = folder.get('id')
                logger.info(f"Pasta {cls.PASTA_NOME} criada no Drive. ID: {cls.PASTA_ID}")
                
                # Configurar permissões da pasta
                permissions = [
                    {'type': 'anyone', 'role': 'reader'},  # Acesso público para leitura
                    {
                        'type': 'user',
                        'role': 'writer',
                        'emailAddress': 'arthur.casadagrafica@gmail.com'
                    }  # Acesso de edição para o email específico
                ]
                
                for permission in permissions:
                    drive_service.service.permissions().create(
                        fileId=cls.PASTA_ID,
                        body=permission,
                        fields='id',
                        sendNotificationEmail=False
                    ).execute()
            
            return cls.PASTA_ID
            
        except Exception as e:
            logger.error(f"Erro ao configurar pasta no Drive: {str(e)}")
            raise
    
    @classmethod
    def processar_formulario(cls, dados_form, arquivos_pdf=None, usuario=None):
        """
        Implementação customizada para processar um formulário ZeroHum
        
        Args:
            dados_form (dict): Dados do formulário validados
            arquivos_pdf (list, optional): Lista de tuplas com (arquivo, nome_arquivo)
            usuario (User, optional): Usuário logado que está enviando o formulário
            
        Returns:
            Formulario: Objeto do formulário criado e processado
        """    
        try:
            # Verifica se as credenciais do Google Drive estão configuradas
            if not os.environ.get("GOOGLE_PRIVATE_KEY") or not os.environ.get("GOOGLE_CLIENT_EMAIL"):
                raise ValueError("As credenciais do Google Drive não estão configuradas corretamente.")
            
            # Gera um código de operação único
            cod_op = cls.gerar_cod_op()
            
            # Extrair as unidades dos dados do formulário
            unidades_data = dados_form.pop('unidades', [])
            logger.info(f"Tipo de unidades_data: {type(unidades_data)}")
            logger.info(f"Unidades recebidas: {unidades_data}")
            
            # Se não houver unidades, verificar se foi um erro de processamento
            if not unidades_data:
                logger.warning("Nenhuma unidade recebida no formulário")
            
            # Processamento avançado de unidades
            # Garantir que unidades_data seja uma lista de dicionários válidos
            processed_unidades = []
            
            # Caso 1: String JSON
            if isinstance(unidades_data, str):
                try:
                    processed_unidades = json.loads(unidades_data)
                    logger.info(f"Unidades processadas de string JSON: {processed_unidades}")
                except Exception as e:
                    logger.error(f"Erro ao processar unidades como string JSON: {e}")
            
            # Caso 2: Dict único
            if isinstance(unidades_data, dict):
                processed_unidades = [unidades_data]
                logger.info(f"Unidades processadas de dict único: {processed_unidades}")
            
            # Caso 3: Lista de itens
            if isinstance(unidades_data, list):
                processed_unidades = unidades_data
                logger.info(f"Unidades processadas de lista: {processed_unidades}")
            
            # Se conseguimos processar unidades, usar a versão processada
            if processed_unidades:
                unidades_data = processed_unidades
            elif not isinstance(unidades_data, list):
                unidades_data = []
                logger.warning("Não foi possível processar unidades em um formato válido")
              # Dados do formulário para salvar
            form_data = {**dados_form}
            
            # Remover campos que são apenas do serializador e não do modelo
            if 'arquivos' in form_data:
                del form_data['arquivos']
            if 'arquivos_nomes' in form_data:
                del form_data['arquivos_nomes']
                
            # Adicionar código de operação
            form_data['cod_op'] = cod_op
            
            # Se o usuário estiver autenticado, vincula o formulário a ele
            if usuario and usuario.is_authenticated:
                form_data['usuario'] = usuario
            
            # Log dos campos limpos para depuração
            logger.debug(f"Campos para criação do formulário: {list(form_data.keys())}")
            
            # Salva o formulário no banco de dados
            formulario = Formulario.objects.create(**form_data)
            logger.info(f"Formulário {cod_op} criado com sucesso")
            
            # Cria as unidades relacionadas ao formulário
            for unidade_data in unidades_data:
                if isinstance(unidade_data, dict):
                    unidade = {
                        'formulario': formulario,
                        'nome': unidade_data.get('nome'),
                        'quantidade': unidade_data.get('quantidade', 1)
                    }
                    formulario.unidades.create(**unidade)            # Processa os arquivos PDF
            # Processa os arquivos PDF
            if arquivos_pdf:
                # Inicializa o serviço do Drive
                drive_service = GoogleDriveService()

                # Garante que a pasta de destino existe
                if not cls.PASTA_ID:
                    cls.setup_pasta_drive()
                    if not cls.PASTA_ID:
                        raise ValueError("Não foi possível criar ou encontrar a pasta no Google Drive")

                # Lista para armazenar os objetos ArquivoPDF criados
                arquivos_criados = []

                # Processa cada arquivo PDF
                for arquivo, nome_arquivo in arquivos_pdf:
                    if not arquivo:
                        logger.warning(f"Arquivo PDF vazio ou inválido para {nome_arquivo}")
                        continue
                    
                    try:
                        # Gera um nome único para o arquivo no Drive
                        nome_drive = f"{cod_op}_{nome_arquivo}"

                        # Criar diretório temporário se não existir
                        temp_dir = os.path.join(settings.BASE_DIR, 'temp')
                        os.makedirs(temp_dir, exist_ok=True)
                          # Salva o arquivo temporariamente
                        temp_file_path = os.path.join(temp_dir, nome_drive)
                        with open(temp_file_path, 'wb') as temp_file:
                            # Se for um InMemoryUploadedFile ou TemporaryUploadedFile
                            if hasattr(arquivo, 'read'):
                                # Posiciona o cursor no início do arquivo
                                arquivo.seek(0)
                                # Lê o conteúdo do arquivo em chunks para evitar problemas de memória
                                for chunk in arquivo.chunks():
                                    temp_file.write(chunk)
                            else:
                                # Se já for bytes, escreve diretamente
                                temp_file.write(arquivo)

                        try:
                            # Faz upload para o Google Drive
                            upload_result = drive_service.upload_pdf(
                                temp_file_path,
                                nome_drive,
                                cls.PASTA_ID
                            )

                            if upload_result and 'id' in upload_result:
                                # Cria o registro do ArquivoPDF com os links do Drive
                                arquivo_pdf = ArquivoPDF.objects.create(
                                    formulario=formulario,
                                    nome=nome_arquivo,
                                    link_download=upload_result['webContentLink'],
                                    web_view_link=upload_result['webViewLink'],
                                    json_link=json.dumps(upload_result)
                                )
                                arquivos_criados.append(arquivo_pdf)
                                logger.info(f"Arquivo PDF '{nome_arquivo}' enviado com sucesso para o Drive")
                            else:
                                raise ValueError(f"Falha no upload do arquivo '{nome_arquivo}' para o Google Drive")

                        finally:
                            # Limpa o arquivo temporário
                            try:
                                if os.path.exists(temp_file_path):
                                    os.remove(temp_file_path)
                            except Exception as e:
                                logger.warning(f"Erro ao remover arquivo temporário: {e}")

                    except Exception as e:
                        logger.error(f"Erro ao processar arquivo PDF '{nome_arquivo}': {str(e)}")
                        # Se houver erro, exclui todos os arquivos já criados e propaga o erro
                        for arquivo_pdf in arquivos_criados:
                            try:
                                arquivo_pdf.delete()
                            except Exception as del_error:
                                logger.error(f"Erro ao excluir arquivo PDF após falha: {str(del_error)}")
                        raise

                        logger.info(f"Arquivo PDF enviado para o Google Drive: {upload_result.get('webViewLink', '')}")
                        
                        # Apaga o arquivo temporário
                        try:
                            os.remove(temp_file_path)
                        except Exception as e:
                            logger.warning(f"Não foi possível remover o arquivo temporário: {e}")

            
            return formulario
            
        except Exception as e:
            logger.error(f"Erro ao processar formulário ZeroHum: {str(e)}")
            logger.error(traceback.format_exc())
            raise