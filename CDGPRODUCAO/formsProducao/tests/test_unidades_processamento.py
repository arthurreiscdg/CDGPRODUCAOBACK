import os
import sys
import django
import json
import logging

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from rest_framework.test import APIClient
from formsProducao.serializers import ZeroHumSerializer
from django.core.files.uploadedfile import SimpleUploadedFile

# Função para testar o serializador diretamente
def testar_serializador():
    print("\n=== Testando o serializador diretamente ===")
    
    dados = {
        'nome': 'Teste',
        'email': 'teste@example.com',
        'titulo': 'Formulário de Teste',
        'data_entrega': '2025-05-30',
        'formato': 'A4',
        'cor_impressao': 'PB',
        'impressao': '1_LADO',
        'observacoes': 'Teste de unidades',
        'unidades': [
            {'nome': 'ARARUAMA', 'quantidade': 10},
            {'nome': 'CABO_FRIO', 'quantidade': 5}
        ]
    }
    
    serializer = ZeroHumSerializer(data=dados)
    if serializer.is_valid():
        print("✓ Serializador VÁLIDO")
        print(f"Dados validados: {serializer.validated_data}")
    else:
        print("✗ Serializador INVÁLIDO")
        print(f"Erros: {serializer.errors}")
    
    print("\n")

# Função para testar o envio via API no formato JSON
def testar_api_json():
    print("\n=== Testando a API via POST JSON ===")
    
    client = APIClient()
    
    dados = {
        'nome': 'Teste API',
        'email': 'teste-api@example.com',
        'titulo': 'Formulário de Teste API',
        'data_entrega': '2025-05-30',
        'formato': 'A4',
        'cor_impressao': 'PB',
        'impressao': '1_LADO',
        'observacoes': 'Teste de API',
        'unidades': [
            {'nome': 'ARARUAMA', 'quantidade': 10},
            {'nome': 'CABO_FRIO', 'quantidade': 5}
        ]
    }
    
    response = client.post('/api/formularios/zerohum/', 
                          data=json.dumps(dados), 
                          content_type='application/json')
    
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.data if hasattr(response, 'data') else response.content}")
    print("\n")

# Função para testar o envio via API com FormData (como o formulário faz)
def testar_api_formdata():
    print("\n=== Testando a API via POST FormData ===")
    
    client = APIClient()
    
    # Criar um arquivo PDF de teste
    conteudo_pdf = b'%PDF-1.4\nTeste de PDF'
    arquivo_pdf = SimpleUploadedFile("teste.pdf", conteudo_pdf, content_type="application/pdf")
    
    dados_json = {
        'nome': 'Teste FormData',
        'email': 'teste-form@example.com',
        'titulo': 'Formulário de Teste FormData',
        'data_entrega': '2025-05-30',
        'formato': 'A4',
        'cor_impressao': 'PB',
        'impressao': '1_LADO',
        'observacoes': 'Teste de FormData',
        'unidades': [
            {'nome': 'ARARUAMA', 'quantidade': 10},
            {'nome': 'CABO_FRIO', 'quantidade': 5}
        ]
    }
    
    dados_formdata = {
        'dados': json.dumps(dados_json),
        'arquivo': arquivo_pdf
    }
    
    response = client.post('/api/formularios/zerohum/', data=dados_formdata)
    
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.data if hasattr(response, 'data') else response.content}")
    print("\n")

if __name__ == '__main__':
    print("Iniciando testes do formulário ZeroHum")
    testar_serializador()
    testar_api_json()
    testar_api_formdata()
    print("Testes concluídos")
