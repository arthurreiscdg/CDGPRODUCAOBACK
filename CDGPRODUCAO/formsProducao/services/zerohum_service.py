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
            form_data = {
                **dados_form,
                'cod_op': cod_op
            }
            
            # Se o usuário estiver autenticado, vincula o formulário a ele
            if usuario and usuario.is_authenticated:
                form_data['usuario'] = usuario
            
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
                    formulario.unidades.create(**unidade)
            
            # Processa os arquivos PDF
            if arquivos_pdf:
                # Se tiver arquivos PDF para processar
                for arquivo, nome_arquivo in arquivos_pdf:
                    if not arquivo:
                        logger.warning(f"Arquivo PDF vazio ou inválido para {nome_arquivo}")
                        continue
                        
                    # Processa o upload do arquivo para o Drive ou salva localmente
                    if desenvolvimento_local:
                        # Salva localmente durante o desenvolvimento
                        caminho_local = cls.salvar_pdf_local(arquivo, f"{cls.PASTA_NOME}_{cod_op}_{nome_arquivo}.pdf")
                        
                        # Cria registro do ArquivoPDF
                        arquivo_pdf = ArquivoPDF.objects.create(
                            formulario=formulario,
                            nome=nome_arquivo,
                            arquivo=caminho_local
                        )
                        logger.info(f"Arquivo PDF salvo localmente: {caminho_local}")
                    else:
                        # Inicializa o serviço do Drive
                        drive_service = GoogleDriveService()
                        
                        # Garante que a pasta de destino existe
                        if not cls.PASTA_ID:
                            cls.setup_pasta_drive()
                        
                        # Salva o arquivo temporariamente
                        temp_file_path = cls.salvar_pdf_local(arquivo, f"{cls.PASTA_NOME}_{cod_op}_{nome_arquivo}.pdf")
                        
                        # Faz upload para o Google Drive
                        if temp_file_path:
                            upload_result = drive_service.upload_pdf(
                                temp_file_path, 
                                f"{cod_op}_{nome_arquivo}.pdf", 
                                cls.PASTA_ID
                            )
                            
                            # Cria o registro do ArquivoPDF
                            if upload_result and 'id' in upload_result:
                                arquivo_pdf = ArquivoPDF.objects.create(
                                    formulario=formulario,
                                    nome=nome_arquivo,
                                    link_download=upload_result.get('webContentLink', ''),
                                    web_view_link=upload_result.get('webViewLink', ''),
                                    json_link=json.dumps(upload_result)
                                )
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