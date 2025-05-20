import os
import uuid
import json
import logging
import traceback
from django.utils import timezone
from django.conf import settings
from formsProducao.utils.drive import GoogleDriveService
from formsProducao.models.formulario import Formulario
from formsProducao.models.arquivopdf import ArquivoPDF
from formsProducao.services.form_services import FormularioService

logger = logging.getLogger(__name__)

class BaseFormularioGoogleDriveService(FormularioService):
    """
    Classe base para serviços de formulário que usam o Google Drive
    """
    # ID da pasta do Google Drive para armazenar os formulários
    # Isso deve ser sobrescrito nas classes filhas
    PASTA_ID = None
    PASTA_NOME = None
    PREFIXO_COD_OP = None  # Deve ser sobrescrito (ex: 'ZH', 'PS', etc.)
    
    @classmethod
    def gerar_cod_op(cls):
        """Gera um código de operação único para cada formulário."""
        # Formato: Prefixo + ano + mês + dia + 4 dígitos aleatórios
        agora = timezone.now()
        prefixo = agora.strftime('%Y%m%d')
        aleatorio = str(uuid.uuid4().int)[:4]
        return f"{cls.PREFIXO_COD_OP}{prefixo}{aleatorio}"
    
    @classmethod
    def setup_pasta_drive(cls):
        """
        Configura a pasta do Google Drive para o formulário se ainda não existir.
        Deve ser chamado na inicialização do aplicativo.
        """
        try:
            # Inicializa o serviço do Google Drive
            drive_service = GoogleDriveService()
            
            # Verifica se já temos o ID da pasta
            if cls.PASTA_ID is not None:
                logger.info(f"Pasta {cls.PASTA_NOME} já configurada com ID: {cls.PASTA_ID}")
                return cls.PASTA_ID
                
            # Verifica se já existe uma pasta com o nome especificado
            pastas = drive_service.get_folders()
            for pasta in pastas:
                if pasta.get('name') == cls.PASTA_NOME:
                    cls.PASTA_ID = pasta.get('id')
                    logger.info(f"Pasta {cls.PASTA_NOME} encontrada com ID: {cls.PASTA_ID}")
                    return cls.PASTA_ID
                
            # Se não encontrou a pasta, cria uma nova
            logger.info(f"Pasta {cls.PASTA_NOME} não encontrada. Criando nova pasta...")
            cls.PASTA_ID = drive_service.create_folder(cls.PASTA_NOME)
            
            if cls.PASTA_ID:
                logger.info(f"Pasta {cls.PASTA_NOME} criada com sucesso. ID: {cls.PASTA_ID}")
            else:
                logger.error(f"Falha ao criar pasta {cls.PASTA_NOME} no Google Drive.")
                
            return cls.PASTA_ID
                
        except Exception as e:
            logger.error(f"Erro ao configurar pasta {cls.PASTA_NOME} no Google Drive: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    @classmethod
    def processar_formulario(cls, dados_form, arquivos_pdf=None, usuario=None):
        """
        Processa um formulário, salvando-o no banco de dados e 
        fazendo upload dos PDFs no Google Drive.
        
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
                        caminho_local = cls.salvar_pdf_local(arquivo, f"{cls.PASTA_NOME}_{cod_op}.pdf")
                        
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
            logger.error(f"Erro ao processar formulário: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    @classmethod
    def atualizar_formulario(cls, formulario, dados_atualizados, arquivos_pdf=None):
        """
        Atualiza um formulário existente, com suporte a upload de novos PDFs no Google Drive.
        
        Args:
            formulario (Formulario): Instância do formulário a ser atualizado
            dados_atualizados (dict): Novos dados para o formulário
            arquivos_pdf (list, optional): Lista de tuplas com (arquivo, nome_arquivo)
            
        Returns:
            Formulario: Objeto do formulário atualizado
        """
        try:
            # Verifica se existe o arquivo de credenciais ou se as variáveis de ambiente estão configuradas
            existe_arquivo_credenciais = os.path.exists(os.path.join(settings.BASE_DIR, 'credentials', 'google_drive_credentials.json'))
            existe_env_credenciais = bool(os.environ.get("GOOGLE_PRIVATE_KEY") and os.environ.get("GOOGLE_CLIENT_EMAIL"))
            
            desenvolvimento_local = not (existe_arquivo_credenciais or existe_env_credenciais)
            logger.info(f"Modo de desenvolvimento local: {desenvolvimento_local}")
              # Lista de campos que são apenas do serializador e não devem ser salvos no modelo
            campos_apenas_serializador = ['arquivos', 'arquivos_nomes', 'cod_op', 'criado_em', 'atualizado_em', 'unidades']
            
            # Atualiza os campos do formulário com os novos dados
            for campo, valor in dados_atualizados.items():
                # Não atualiza campos somente leitura, relações especiais ou campos apenas do serializador
                if campo not in campos_apenas_serializador:
                    setattr(formulario, campo, valor)
            
            # Atualiza as unidades se necessário
            if 'unidades' in dados_atualizados:
                unidades_data = dados_atualizados['unidades']
                
                # Remove todas as unidades existentes
                formulario.unidades.all().delete()
                
                # Cria as novas unidades
                for unidade_data in unidades_data:
                    if isinstance(unidade_data, dict):
                        unidade = {
                            'formulario': formulario,
                            'nome': unidade_data.get('nome'),
                            'quantidade': unidade_data.get('quantidade', 1)
                        }
                        formulario.unidades.create(**unidade)
            
            # Salva as alterações do formulário
            formulario.save()
            
            # Processa os novos arquivos PDF se houver
            if arquivos_pdf:
                for arquivo, nome_arquivo in arquivos_pdf:
                    if not arquivo:
                        logger.warning(f"Arquivo PDF vazio ou inválido para {nome_arquivo}")
                        continue
                    
                    # Processa o upload do arquivo para o Drive ou salva localmente
                    if desenvolvimento_local:
                        # Salva localmente durante o desenvolvimento
                        caminho_local = cls.salvar_pdf_local(arquivo, f"{cls.PASTA_NOME}_{formulario.cod_op}_{nome_arquivo}.pdf")
                        
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
                        temp_file_path = cls.salvar_pdf_local(arquivo, f"{cls.PASTA_NOME}_{formulario.cod_op}_{nome_arquivo}.pdf")
                        
                        # Faz upload para o Google Drive
                        if temp_file_path:
                            upload_result = drive_service.upload_pdf(
                                temp_file_path, 
                                f"{formulario.cod_op}_{nome_arquivo}.pdf", 
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
            logger.error(f"Erro ao atualizar formulário: {str(e)}")
            logger.error(traceback.format_exc())
            raise