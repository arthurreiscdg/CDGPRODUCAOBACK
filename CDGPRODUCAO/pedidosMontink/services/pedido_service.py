from ..models.webhook_pedido import Pedido, StatusPedido
from django.shortcuts import get_object_or_404
from ..views.webhook_enviar import WebhookService
import logging

logger = logging.getLogger(__name__)


class PedidoService:
    @staticmethod
    def listar_pedidos(filtros=None):
        """
        Lista todos os pedidos com filtros opcionais
        """
        queryset = Pedido.objects.select_related('status')
        
        if filtros:
            # Implementar filtros conforme necessário
            if 'numero_pedido' in filtros and filtros['numero_pedido']:
                queryset = queryset.filter(numero_pedido__icontains=filtros['numero_pedido'])
            
            if 'sku' in filtros and filtros['sku']:
                queryset = queryset.filter(sku__icontains=filtros['sku'])
            
            if 'status' in filtros and filtros['status']:
                queryset = queryset.filter(status=filtros['status'])
            
            if 'data_inicio' in filtros and filtros['data_inicio']:
                queryset = queryset.filter(criado_em__gte=filtros['data_inicio'])
                
            if 'data_fim' in filtros and filtros['data_fim']:
                queryset = queryset.filter(criado_em__lte=filtros['data_fim'])
        
        return queryset
    
    @staticmethod
    def obter_pedido(pedido_id):
        """
        Obtém um pedido específico pelo ID
        """
        return get_object_or_404(Pedido.objects.select_related('status'), id=pedido_id)    @staticmethod
    def atualizar_status_pedido(pedido_id, novo_status_id):
        """
        Atualiza o status de um pedido e envia webhook para os endpoints configurados.
        O status só é atualizado se todos os webhooks forem enviados com sucesso.
        """
        from django.db import transaction
        from ..models.webhook_config import WebhookEndpointConfig
        
        pedido = get_object_or_404(Pedido, id=pedido_id)
        status_anterior = pedido.status
        novo_status = get_object_or_404(StatusPedido, id=novo_status_id)
        
        # Se o status não mudou, não fazemos nada
        if pedido.status.id == novo_status.id:
            logger.info(f"Status do pedido #{pedido_id} não foi alterado (já era {pedido.status.nome})")
            return pedido
            
        # Verificar se existem endpoints configurados
        endpoints = WebhookEndpointConfig.objects.filter(ativo=True, auto_enviar=True)
        if not endpoints.exists():
            # Se não há endpoints configurados, atualizamos o status diretamente
            logger.info(f"Nenhum endpoint de webhook configurado. Atualizando status diretamente.")
            pedido.status = novo_status
            pedido.save(update_fields=['status', 'atualizado_em'])
            logger.info(f"Status do pedido #{pedido_id} alterado de {status_anterior.nome} para {novo_status.nome}")
            return pedido
        
        try:
            # Usamos uma transação para garantir atomicidade
            with transaction.atomic():
                # Tenta enviar os webhooks primeiro, sem alterar o status
                resultados = WebhookService.enviar_webhook_status(
                    pedido=pedido,
                    novo_status=novo_status,
                    old_status=status_anterior,
                    atualizar_pedido=False  # Não atualiza o pedido automaticamente
                )
                
                # Verifica se houve falha em algum endpoint
                falhas = sum(1 for r in resultados if not r.sucesso)
                if falhas > 0:
                    logger.error(f"Falha ao enviar {falhas} webhooks. Status do pedido #{pedido_id} NÃO foi alterado.")
                    raise Exception(f"Falha ao enviar webhooks para {falhas} endpoints. Status não foi alterado.")
                
                # Se todos os webhooks foram enviados com sucesso, atualiza o status
                pedido.status = novo_status
                pedido.save(update_fields=['status', 'atualizado_em'])
                
                logger.info(f"Status do pedido #{pedido_id} alterado de {status_anterior.nome} para {novo_status.nome}")
                logger.info(f"Webhooks enviados com sucesso: total={len(resultados)}")
                
                return pedido
                
        except Exception as e:
            logger.error(f"Erro ao processar atualização de status do pedido #{pedido_id}: {str(e)}")
            raise Exception(f"Não foi possível atualizar o status: {str(e)}")
    @staticmethod
    def listar_status():
        """
        Lista todos os status de pedido disponíveis
        """
        return StatusPedido.objects.filter(ativo=True).order_by('ordem')
    @staticmethod
    def atualizar_status_pedidos_em_lote(pedido_ids, novo_status_id):
        """
        Atualiza o status de múltiplos pedidos em lote
        
        Args:
            pedido_ids: Lista de IDs dos pedidos a serem atualizados
            novo_status_id: ID do novo status
            
        Returns:
            dict: Dicionário com resultados da operação
        """
        if not pedido_ids:
            return {
                "sucesso": False,
                "mensagem": "Nenhum pedido selecionado",
                "atualizados": 0,
                "falhas": 0,
                "detalhes": []
            }
            
        novo_status = get_object_or_404(StatusPedido, id=novo_status_id)
        resultados = []
        pedidos_atualizados = 0
        falhas = 0
        
        # Processa cada pedido individualmente
        for pedido_id in pedido_ids:
            try:
                # Usa o método existente para aproveitar o envio de webhooks
                pedido = PedidoService.atualizar_status_pedido(pedido_id, novo_status_id)
                resultados.append({
                    "id": pedido_id,
                    "numero_pedido": pedido.numero_pedido,
                    "sucesso": True,
                    "status_atual": pedido.status.nome,
                })
                pedidos_atualizados += 1
            except Exception as e:
                logger.error(f"Erro ao atualizar pedido #{pedido_id}: {str(e)}")
                resultados.append({
                    "id": pedido_id,
                    "sucesso": False,
                    "erro": str(e)
                })
                falhas += 1
                
        return {
            "sucesso": pedidos_atualizados > 0,
            "mensagem": f"{pedidos_atualizados} pedidos atualizados com sucesso. {falhas} falhas.",
            "atualizados": pedidos_atualizados,
            "falhas": falhas,
            "detalhes": resultados
        }