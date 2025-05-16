import requests
import json
import hmac
import hashlib

# URL da sua API (substitua pela URL real)
api_url = "http://127.0.0.1:8000/api/webhooks/receber/"

# Secret key configurada no WebhookConfig (substitua pela sua secret key)
secret_key = "123"

# Dados do pedido de teste conforme o formato especificado
payload = {
    "valor_pedido": 85.90,
    "custo_envio": 15.50,
    "etiqueta_envio": "https://exemplo.com/etiqueta/12345.pdf",
    "metodo_envio": 1,
    "numero_pedido": 12345,
    "nome_cliente": "João Silva",
    "documento_cliente": "123.456.789-10",
    "email_cliente": "joao.silva@exemplo.com",
    "produtos": [
        {
            "nome": "Agenda Personalizada A5 - Papel Couché 250g",
            "sku": "AP-A5-C250",
            "quantidade": 2,
            "id_sku": 123,
            "designs": {
                "capa_frente": "https://exemplo.com/designs/12345_frente.jpg",
                "capa_verso": "https://exemplo.com/designs/12345_verso.jpg"
            },
            "mockups": {
                "capa_frente": "https://exemplo.com/mockups/12345_frente.jpg",
                "capa_costas": "https://exemplo.com/mockups/12345_costas.jpg"
            },
            "arquivo_pdf": "https://exemplo.com/arquivos/12345.pdf"
        }
    ],
    "informacoes_adicionais": {
        "nome": "Loja do João",
        "telefone": "(11) 99999-9999",
        "email": "contato@lojadojoao.com"
    },
    "endereco_envio": {
        "nome_destinatario": "Maria Silva",
        "endereco": "Rua das Flores",
        "numero": "123",
        "complemento": "Apto 45",
        "cidade": "São Paulo",
        "uf": "SP",
        "cep": "01234-567",
        "bairro": "Centro",
        "telefone": "(11) 88888-8888",
        "pais": "Brasil"
    }
}

# Converte o payload para JSON
payload_json = json.dumps(payload)

# Calcula a assinatura HMAC-SHA256
assinatura = hmac.new(
    secret_key.encode('utf-8'),
    payload_json.encode('utf-8'),
    hashlib.sha256
).hexdigest()

# Prepara os headers da requisição
headers = {
    'Content-Type': 'application/json',
    'X-Webhook-Signature': assinatura
}

# Função para enviar o webhook
def enviar_webhook():
    try:
        # Envia a requisição POST
        response = requests.post(
            api_url,
            data=payload_json,
            headers=headers
        )
        
        # Exibe informações da resposta
        print(f"Status Code: {response.status_code}")
        print(f"Resposta: {response.text}")
        
        # Verifica se a requisição foi bem-sucedida
        if response.status_code in [200, 201]:
            print("✅ Webhook enviado com sucesso!")
        else:
            print("❌ Falha ao enviar webhook")
            
    except Exception as e:
        print(f"❌ Erro ao enviar webhook: {str(e)}")

# Executa o envio
if __name__ == "__main__":
    print("Enviando webhook de teste...")
    print(f"Payload: {payload_json[:100]}...")
    print(f"Assinatura: {assinatura}")
    enviar_webhook()