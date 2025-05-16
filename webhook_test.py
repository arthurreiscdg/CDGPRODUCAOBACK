import json
import hmac
import hashlib
import requests
import random
import time
import argparse

def main():
    # Processar argumentos da linha de comando
    parser = argparse.ArgumentParser(description='Envia webhooks de teste com assinatura')
    parser.add_argument('--url', default='http://127.0.0.1:8000/api/webhooks/receber/', help='URL para enviar os webhooks')
    parser.add_argument('--secret', default='sua-chave-secreta-aqui', help='Chave secreta para assinar os webhooks')
    parser.add_argument('--count', type=int, default=3, help='Número de webhooks para enviar')
    parser.add_argument('--invalid-signature', action='store_true', help='Envia um webhook com assinatura inválida para testar rejeição')
    args = parser.parse_args()

    # URL do endpoint que irá receber os webhooks
    url = args.url
    secret_key = args.secret
    count = args.count

    print(f"Enviando {count} webhook(s) para {url}")
    print(f"Chave secreta: {secret_key}")
    print("-" * 50)
    
    # Lista de nomes para gerar pedidos de teste
    nomes = ["João Silva", "Maria Oliveira", "Carlos Souza", "Ana Paula", "Rafael Lima", 
             "Juliana Mendes", "Pedro Alves", "Fernanda Rocha", "Lucas Martins", "Patrícia Gonçalves"]

    # Envia webhooks com assinatura válida
    for i in range(count):
        nome_cliente = random.choice(nomes)
        # Gerando número de pedido único baseado no timestamp
        numero_pedido = int(time.time() * 1000) % 100000 + i
        documento_cliente = f"{random.randint(100, 999)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(10, 99)}"
        
        # Criando o payload do webhook
        payload = {
            "valor_pedido": round(random.uniform(100, 500), 2),
            "custo_envio": round(random.uniform(10, 30), 2),
            "etiqueta_envio": f"https://exemplo.com/etiqueta_{numero_pedido}.pdf",
            "metodo_envio": 1,
            "numero_pedido": numero_pedido,
            "nome_cliente": nome_cliente,
            "documento_cliente": documento_cliente,
            "email_cliente": f"{nome_cliente.lower().replace(' ', '').replace('ç', 'c').replace('á', 'a').replace('í', 'i')}@exemplo.com",
            "produtos": [{
                "nome": "Cartão de Visita",
                "sku": f"CV-{i:03}",
                "quantidade": random.choice([500, 1000, 1500]),
                "id_sku": i + 1,
                "designs": {
                    "capa_frente": f"https://exemplo.com/design_frente_{i}.jpg",
                    "capa_verso": f"https://exemplo.com/design_verso_{i}.jpg"
                },
                "mockups": {
                    "capa_frente": f"https://exemplo.com/mockup_frente_{i}.jpg",
                    "capa_costas": f"https://exemplo.com/mockup_verso_{i}.jpg"
                },
                "arquivo_pdf": f"https://exemplo.com/arquivo_{i}.pdf"
            }],
            "informacoes_adicionais": {
                "nome": "Loja Teste",
                "telefone": "(11) 99999-9999",
                "email": "loja@teste.com"
            },
            "endereco_envio": {
                "nome_destinatario": nome_cliente,
                "endereco": "Rua Teste",
                "numero": str(random.randint(1, 999)),
                "complemento": f"Apto {random.randint(10, 99)}",
                "cidade": "São Paulo",
                "uf": "SP",
                "cep": f"{random.randint(10000, 99999)}-{random.randint(100, 999)}",
                "bairro": "Centro",
                "telefone": f"(11) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                "pais": "Brasil"
            }
        }

        # Converte o payload para JSON
        payload_json = json.dumps(payload)
        
        # Gera a assinatura HMAC SHA-256
        signature = hmac.new(
            secret_key.encode('utf-8'),
            payload_json.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    # Configura os cabeçalhos com a assinatura
        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature,
            "X-Webhook-Event": "novo_pedido"
        }

        # Envia o webhook
        try:
            print(f"[{i+1}] Enviando webhook para pedido #{numero_pedido} com assinatura válida...")
            response = requests.post(url, data=payload_json, headers=headers)
            print(f"[{i+1}] Status Code: {response.status_code}")
            print(f"Resposta: {response.text}\n")
            
            # Espera um pouco entre os envios
            time.sleep(1)
        except Exception as e:
            print(f"[{i+1}] Erro ao enviar webhook: {str(e)}\n")

    # Teste opcional: envia webhook com assinatura inválida
    if args.invalid_signature:
        # Gera um pedido de teste
        nome_cliente = random.choice(nomes)
        numero_pedido = int(time.time() * 1000) % 100000 + count
        payload = {
            "valor_pedido": round(random.uniform(100, 500), 2),
            "numero_pedido": numero_pedido,
            "nome_cliente": nome_cliente,
            "documento_cliente": f"{random.randint(100, 999)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(10, 99)}",
            "email_cliente": f"{nome_cliente.lower().replace(' ', '')}@exemplo.com",
            "produtos": [{
                "nome": "Cartão de Visita Teste Falha",
                "sku": "CV-INVALID",
                "quantidade": 1000
            }]
        }
        
        # Converte o payload para JSON
        payload_json = json.dumps(payload)
        
        # Gera uma assinatura inválida (usando chave errada)
        invalid_signature = hmac.new(
            "chave_errada".encode('utf-8'),
            payload_json.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        # Configura os cabeçalhos com a assinatura inválida
        headers = {
            "Content-Type": "application/json",
            "X-Hub-Signature": f"sha256={invalid_signature}",
            "X-Webhook-Event": "novo_pedido"
        }

        # Envia o webhook
        try:
            print("\nTESTE DE SEGURANÇA: Enviando webhook com assinatura inválida...")
            response = requests.post(url, data=payload_json, headers=headers)
            print(f"Status Code: {response.status_code}")
            print(f"Resposta: {response.text}\n")
        except Exception as e:
            print(f"Erro ao enviar webhook com assinatura inválida: {str(e)}\n")

    print("Todos os webhooks de teste foram enviados!")

if __name__ == "__main__":
    main()
