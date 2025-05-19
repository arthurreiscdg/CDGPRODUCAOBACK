

import logging
import os
import uuid
import json
from django.conf import settings
from django.utils import timezone
from formsProducao.services.google_drive_service import BaseFormularioGoogleDriveService
from formsProducao.models.formulario import Formulario

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
        try:            # Durante o desenvolvimento, se não houver credenciais do Google Drive,
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
            
            # Dados do formulário para salvar
            form_data = {
                **dados_form,
                'cod_op': cod_op
            }
            
            # Se estivermos em modo de desenvolvimento local
            if desenvolvimento_local and arquivo_pdf:
                # Cria a pasta de mídia se não existir
                media_dir = os.path.join(settings.MEDIA_ROOT, 'pdfs')
                if not os.path.exists(media_dir):
                    os.makedirs(media_dir)
                
                # Gera um nome de arquivo único
                nome_arquivo = f"{cls.PREFIXO_COD_OP}_{cod_op}.pdf"
                caminho_arquivo = os.path.join(media_dir, nome_arquivo)
                
                # Salva o arquivo PDF
                with open(caminho_arquivo, 'wb') as f:
                    f.write(arquivo_pdf)
                
                # Define o link local
                form_data['link_download'] = f"/media/pdfs/{nome_arquivo}"
                form_data['arquivo'] = f"pdfs/{nome_arquivo}"              # Cria o formulário no banco de dados, incluindo o usuário que enviou
            formulario = Formulario.objects.create(
                **form_data,
                usuario=usuario
            )
            
            # Cria as unidades relacionadas ao formulário
            from formsProducao.models.unidade import Unidade
            for unidade_data in unidades_data:
                Unidade.objects.create(
                    formulario=formulario,
                    nome=unidade_data['nome'],
                    quantidade=unidade_data['quantidade']
                )
              # Se não estiver em desenvolvimento local, tenta fazer upload para o Google Drive
            if not desenvolvimento_local and arquivo_pdf:
                try:
                    # Salva o arquivo temporariamente para fazer o upload
                    nome_arquivo = f"{cls.PASTA_NOME}_{cod_op}.pdf"
                    caminho_local = cls.salvar_pdf_local(arquivo_pdf, nome_arquivo)
                    
                    if caminho_local:
                        # Configura a pasta no Google Drive se necessário
                        if cls.PASTA_ID is None:
                            cls.setup_pasta_drive()
                            
                        # Faz upload para o Google Drive
                        from formsProducao.utils.drive import GoogleDriveService
                        drive_service = GoogleDriveService()
                        resultado_upload = drive_service.upload_pdf(
                            caminho_local, 
                            nome_arquivo,
                            cls.PASTA_ID
                        )
                        
                        # Log do resultado do upload
                        logger.info(f"Resultado do upload para o Google Drive: {resultado_upload}")
                        if resultado_upload:
                            # Atualiza o formulário com os links
                            download_link = resultado_upload.get('download_link')
                            web_view_link = resultado_upload.get('web_link')
                            logger.info(f"Link de download: {download_link}")
                            logger.info(f"Link de visualização: {web_view_link}")
                            formulario.link_download = download_link
                            formulario.web_view_link = web_view_link
                              # Obtém as unidades relacionadas a este formulário
                            unidades = formulario.unidades.all()
                            unidades_json = []
                            for unidade in unidades:
                                unidades_json.append({
                                    'nome': unidade.nome,
                                    'quantidade': unidade.quantidade
                                })
                            
                            # Cria um JSON com os detalhes do formulário
                            dados_json = {
                                'cod_op': cod_op,
                                'nome': dados_form.get('nome'),
                                'email': dados_form.get('email'),
                                'unidades': unidades_json,
                                'titulo': dados_form.get('titulo'),
                                'data_entrega': str(dados_form.get('data_entrega')),
                                'link_pdf': download_link,
                                'link_visualizacao': web_view_link
                            }
                            
                            formulario.json_link = json.dumps(dados_json)
                            formulario.save()
                            
                        # Remove o arquivo temporário
                        if os.path.exists(caminho_local):
                            os.remove(caminho_local)
                except Exception as e:
                    logger.error(f"Erro ao fazer upload para o Google Drive: {str(e)}")
                    # Mas não falha se o upload não funcionar, já que o arquivo já foi salvo localmente
            
            return formulario
                
        except Exception as e:
            logger.error(f"Erro ao processar formulário ZeroHum: {str(e)}")
            raise
