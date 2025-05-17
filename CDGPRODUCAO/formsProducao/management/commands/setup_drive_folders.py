import os
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from formsProducao.services.form_services import (
    ZeroHumService, PensiService, EliteService, coleguiumService
)

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Configura as pastas do Google Drive para os formulários'

    def handle(self, *args, **options):
        self.stdout.write('Verificando configurações do Google Drive...')
        
        # Verifica se o diretório credentials existe
        credentials_path = os.path.join(settings.BASE_DIR, 'credentials')
        if not os.path.exists(credentials_path):
            os.makedirs(credentials_path)
            self.stdout.write(self.style.WARNING(
                f'Criado diretório de credenciais em: {credentials_path}'
            ))
        
        # Verifica se o arquivo de credenciais existe
        credentials_file = os.path.join(credentials_path, 'google_drive_credentials.json')
        if not os.path.exists(credentials_file):
            self.stdout.write(self.style.ERROR(
                f'Arquivo de credenciais do Google Drive não encontrado em: {credentials_file}. '
                f'Por favor, coloque o arquivo JSON de credenciais do serviço neste local.'
            ))
            return
        
        self.stdout.write(self.style.SUCCESS('Arquivo de credenciais encontrado.'))
        
        # Configura pastas para cada tipo de formulário
        self.setup_form_folder(ZeroHumService, 'ZeroHum')
        self.setup_form_folder(PensiService, 'Pensi')
        self.setup_form_folder(EliteService, 'Elite')
        self.setup_form_folder(coleguiumService, 'coleguium')
        
        self.stdout.write(self.style.SUCCESS('Configuração de pastas do Google Drive concluída.'))
    
    def setup_form_folder(self, service_class, folder_name):
        """Configura pasta para um tipo de formulário específico"""
        self.stdout.write(f'Configurando pasta para {folder_name}...')
        
        try:
            folder_id = service_class.setup_pasta_drive()
            if folder_id:
                self.stdout.write(self.style.SUCCESS(
                    f'Pasta {folder_name} configurada com sucesso. ID: {folder_id}'
                ))
            else:
                self.stdout.write(self.style.ERROR(
                    f'Falha ao configurar pasta {folder_name}'
                ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Erro ao configurar pasta {folder_name}: {str(e)}'
            ))
