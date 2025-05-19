

import logging
import os
import uuid
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
    def processar_formulario(cls, dados_form, arquivo_pdf=None):
        """
        Implementação customizada para processar um formulário ZeroHum
        
        Args:
            dados_form (dict): Dados do formulário validados
            arquivo_pdf (bytes, optional): Conteúdo do arquivo PDF
            
        Returns:
            Formulario: Objeto do formulário criado e processado
        """
        try:
            # Durante o desenvolvimento, se não houver credenciais do Google Drive,
            # podemos salvar os arquivos localmente
            desenvolvimento_local = not os.path.exists(os.path.join(settings.BASE_DIR, 'credentials', 'google_drive_credentials.json'))
            
            # Gera um código de operação único
            cod_op = cls.gerar_cod_op()
            
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
                form_data['arquivo'] = f"pdfs/{nome_arquivo}"
            
            # Cria o formulário no banco de dados
            formulario = Formulario.objects.create(**form_data)
            
            # Se não estiver em desenvolvimento local, tenta fazer upload para o Google Drive
            if not desenvolvimento_local and arquivo_pdf:
                # Usa a implementação do serviço base
                return super().processar_formulario(dados_form, arquivo_pdf)
            
            return formulario
                
        except Exception as e:
            logger.error(f"Erro ao processar formulário ZeroHum: {str(e)}")
            raise
