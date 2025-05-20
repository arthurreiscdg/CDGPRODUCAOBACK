import logging
import os
import uuid
import json
from django.conf import settings
from django.utils import timezone
from formsProducao.services.google_drive_service import BaseFormularioGoogleDriveService
from formsProducao.models.formulario import Formulario
from formsProducao.models.unidade import Unidade
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
    def processar_formulario(cls, dados_form, arquivo_pdf=None, usuario=None):
        """
        Implementação customizada para processar um formulário ZeroHum
        
        Args:
            dados_form (dict): Dados do formulário validados
            arquivo_pdf (bytes, optional): Conteúdo do arquivo PDF
            usuario (User, optional): Usuário logado que está enviando o formulário
            
        Returns:
            Formulario: Objeto do formulário criado e processado
        """
        try:
            # Durante o desenvolvimento, se não houver credenciais do Google Drive,
            # podemos salvar os arquivos localmente
            # Verifica se existe o arquivo de credenciais ou se as variáveis de ambiente estão configuradas
            existe_arquivo_credenciais = os.path.exists(os.path.join(settings.BASE_DIR, 'credentials', 'google_drive_credentials.json'))
            existe_env_credenciais = bool(os.environ.get("GOOGLE_PRIVATE_KEY") and os.environ.get("GOOGLE_CLIENT_EMAIL"))
            
            desenvolvimento_local = not (existe_arquivo_credenciais or existe_env_credenciais)
            logger.info(f"Modo de desenvolvimento local: {desenvolvimento_local}")
            
            # Gera um código de operação único
            cod_op = cls.gerar_cod_op()
              # Extrair as unidades dos dados do formulário
            unidades_data = dados_form.pop('unidades', [])
            logger.info(f"Tipo de unidades_data: {type(unidades_data)}")
            logger.info(f"Unidades recebidas: {unidades_data}")
            
            # Se não houver unidades, verificar se foi um erro de processamento
            if not unidades_data:
                logger.warning("Nenhuma unidade encontrada nos dados do formulário")
            
            # Processamento avançado de unidades
            # Garantir que unidades_data seja uma lista de dicionários válidos
            processed_unidades = []
            
            # Caso 1: String JSON
            if isinstance(unidades_data, str):
                try:
                    unidades_data = json.loads(unidades_data)
                    logger.info(f"Unidades convertidas de string JSON: {unidades_data}")
                except Exception as e:
                    logger.error(f"Erro ao converter unidades de string JSON: {e}")
                    unidades_data = []
            
            # Caso 2: Dict único
            if isinstance(unidades_data, dict):
                unidades_data = [unidades_data]
                logger.info("Convertido objeto de unidades de dict para lista")
            
            # Caso 3: Lista de itens
            if isinstance(unidades_data, list):
                for item in unidades_data:
                    # Se o item for uma string, tentar converter para dict
                    if isinstance(item, str):
                        try:
                            item_dict = json.loads(item)
                            if isinstance(item_dict, dict) and 'nome' in item_dict and 'quantidade' in item_dict:
                                processed_unidades.append(item_dict)
                        except Exception as e:
                            logger.error(f"Erro ao processar item de unidade como string: {e}")
                    # Se o item for um dict, verificar campos necessários
                    elif isinstance(item, dict) and 'nome' in item and 'quantidade' in item:
                        processed_unidades.append(item)
            
            # Se conseguimos processar unidades, usar a versão processada
            if processed_unidades:
                unidades_data = processed_unidades
                logger.info(f"Unidades processadas com sucesso: {unidades_data}")
            elif not isinstance(unidades_data, list):
                unidades_data = []
                logger.warning("Unidades não é uma lista válida nem pode ser convertida para uma")
            
            # Dados do formulário para salvar
            form_data = {
                **dados_form,
                'cod_op': cod_op
            }
            
            # Caminho para salvar e link de download/visualização, inicialmente vazios
            link_download = None
            web_view_link = None
            json_link = None
            
            # Processar o upload do arquivo PDF para o Google Drive
            if arquivo_pdf:
                # Nome do arquivo para upload
                nome_arquivo = f"ZeroHum_{cod_op}.pdf"
                
                # Caminho temporário para salvar o PDF antes de enviar ao Drive
                temp_file_path = os.path.join(settings.BASE_DIR, 'temp', nome_arquivo)
                os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
                
                # Salvar arquivo temporariamente
                with open(temp_file_path, 'wb') as f:
                    f.write(arquivo_pdf.read() if hasattr(arquivo_pdf, 'read') else arquivo_pdf)
                
                # Se estivermos em modo desenvolvimento e não temos acesso ao Google Drive
                if desenvolvimento_local:
                    # Salvamos apenas localmente
                    form_data['arquivo'] = arquivo_pdf
                    form_data['link_download'] = f"/media/pdfs/{nome_arquivo}"
                    form_data['web_view_link'] = f"/media/pdfs/{nome_arquivo}"
                    logger.info(f"Arquivo salvo localmente em: {temp_file_path}")
                else:
                    # Inicializa o serviço do Google Drive
                    drive_service = GoogleDriveService()
                    
                    # Configurar a pasta no Google Drive se necessário
                    if cls.PASTA_ID is None:
                        cls.setup_pasta_drive()
                    
                    # Fazer upload do arquivo para o Google Drive
                    resultado_upload = drive_service.upload_pdf(
                        file_path=temp_file_path, 
                        file_name=nome_arquivo,
                        folder_id=cls.PASTA_ID
                    )
                    
                    if resultado_upload:
                        # Obter links do resultado do upload
                        file_id = resultado_upload.get('file_id')
                        web_view_link = resultado_upload.get('web_link')
                        link_download = resultado_upload.get('download_link')
                        
                        # Atualizar os dados do formulário com os links
                        form_data['link_download'] = link_download
                        form_data['web_view_link'] = web_view_link
                        
                        logger.info(f"Arquivo enviado para o Google Drive com sucesso. ID: {file_id}")
                        logger.info(f"Link de visualização: {web_view_link}")
                        logger.info(f"Link de download: {link_download}")
                    else:
                        logger.error("Falha ao fazer upload do arquivo para o Google Drive")
            
            # Criar o formulário no banco de dados
            formulario = Formulario.objects.create(
                **form_data,
                usuario=usuario
            )
            
            # Criar as unidades relacionadas ao formulário
            for unidade_data in unidades_data:
                if isinstance(unidade_data, dict):
                    Unidade.objects.create(
                        formulario=formulario,
                        nome=unidade_data.get('nome'),
                        quantidade=unidade_data.get('quantidade', 1)
                    )
                
            return formulario
                
        except Exception as e:
            logger.error(f"Erro ao processar formulário ZeroHum: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise e
