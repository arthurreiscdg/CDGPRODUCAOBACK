import requests
import json
import hmac
import hashlib
import time
import argparse

def criar_payload_teste():
    """Cria um payload de exemplo no formato especificado"""
    return {
        "valor_pedido": 159.90,
        "custo_envio": 15.00,
        "etiqueta_envio": "https://exemplo.com/etiqueta.pdf",
        "metodo_envio": 2,
        "numero_pedido": int(time.time()),  # Usa timestamp para garantir número único
        "nome_cliente": "Cliente de Teste",
        "documento_cliente": "123.456.789-00",
        "email_cliente": "cliente.teste@exemplo.com",
        "produtos": [
            {
                "nome": "Produto de Teste - Tamanho M",
                "sku": "TESTE-123",
                "quantidade": 1,
                "id_sku": 456,
                "designs": {
                    "capa_frente": "https://exemplo.com/design/frente.png",
                    "capa_verso": "https://exemplo.com/design/verso.png"
                },
                "mockups": {
                    "capa_frente": "https://exemplo.com/mockup/frente.png",
                    "capa_costas": "https://exemplo.com/mockup/costas.png"
                },
                "arquivo_pdf": "https://exemplo.com/arquivo/produto.pdf"
            }
        ],
        "informacoes_adicionais": {
            "nome": "Loja de Teste",
            "telefone": "(11) 98765-4321",
            "email": "contato@lojateste.com.br"
        },
        "endereco_envio": {
            "nome_destinatario": "Destinatário de Teste",
            "endereco": "Rua de Teste",
            "numero": "123",
            "complemento": "Sala 42",
            "cidade": "Cidade de Teste",
            "uf": "SP",
            "cep": "01234-567",
            "bairro": "Bairro de Teste",
            "telefone": "(11) 91234-5678",
            "pais": "Brasil"
        }
    }

def calcular_assinatura(payload, secret_key):
    """Calcula a assinatura HMAC-SHA256 para o payload usando a secret key"""
    payload_bytes = json.dumps(payload).encode('utf-8')
    return hmac.new(
        key=secret_key.encode('utf-8'),
        msg=payload_bytes,
        digestmod=hashlib.sha256
    ).hexdigest()

def enviar_webhook(url, payload, secret_key=None):
    """Envia um webhook para a URL especificada com o payload fornecido"""
    headers = {
        'Content-Type': 'application/json'
    }
    
    # Se uma secret key foi fornecida, calcular e incluir a assinatura
    if secret_key:
        assinatura = calcular_assinatura(payload, secret_key)
        headers['X-Signature'] = assinatura
        print(f"\nAssinatura calculada: {assinatura}")

    # Converte o payload para JSON
    payload_json = json.dumps(payload)
    
    print("\nEnviando webhook para:", url)
    print("\nHeaders:", headers)
    print("\nPayload:", payload_json[:200] + "..." if len(payload_json) > 200 else payload_json)
    
    # Envia a requisição
    try:
        resposta = requests.post(url, headers=headers, data=payload_json)
        print("\n\nResposta do servidor:")
        print(f"Status: {resposta.status_code}")
        print("Headers:", dict(resposta.headers))
        try:
            print("Corpo:", json.dumps(resposta.json(), indent=2))
        except:
            print("Corpo:", resposta.text[:500])
        
        return resposta
    except Exception as e:
        print(f"\nErro ao enviar webhook: {e}")
        return None

if __name__ == "__main__":
    # Configurar argumentos de linha de comando
    parser = argparse.ArgumentParser(description='Envia um webhook de teste')
    parser.add_argument('--url', type=str, required=True, help='URL para enviar o webhook')
    parser.add_argument('--secret', type=str, help='Secret key para assinar o webhook (opcional)')
    
    args = parser.parse_args()
    
    # Criar payload de teste
    payload = criar_payload_teste()
    
    # Enviar webhook
    enviar_webhook(args.url, payload, args.secret)

# Para executar este script:
# python webhook_teste.py --url http://localhost:8000/api/webhooks/receber/ --secret SuaSecretKeyAqui
