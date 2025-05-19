"""
Script para testar o formato dos webhooks enviados.
Execute este script para verificar o formato do JSON enviado para os endpoints.
"""

import json
import datetime
from pprint import pprint

def test_webhook_payload():
    # Simular dados para o payload
    data_atual = datetime.datetime.now().isoformat()
    
    # Formato antigo do payload
    payload_antigo = {
        "evento": "atualizacao_status",
        "pedido_id": 123,
        "numero_pedido": 456789,
        "status_novo": {
            "id": 2,
            "nome": "Em Produção",
            "descricao": "O pedido está sendo produzido"
        },
        "data": data_atual,
        "detalhes_pedido": {
            "id": 123,
            "titulo": "Pedido de teste",
            "valor_pedido": "50.00",
            # ... outros campos
        }
    }
    
    # Novo formato do payload conforme solicitado
    payload_novo = {
        "data": data_atual,
        "access_token": "abc123",  # Este valor será obtido de cada endpoint
        "json": {
            "casa_grafica_id": "123",
            "status_id": 2,
            "status": "Em Produção"
        }
    }
    
    print("== Formato ANTIGO do payload ==")
    pprint(payload_antigo)
    print("\n== Formato NOVO do payload ==")
    pprint(payload_novo)
    print("\n== JSON do novo formato (como será enviado) ==")
    print(json.dumps(payload_novo, indent=2))

if __name__ == "__main__":
    test_webhook_payload()
