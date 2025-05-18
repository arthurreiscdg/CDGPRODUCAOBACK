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
        return get_object_or_404(Pedido.objects.select_related('status'), id=pedido_id)
    @staticmethod
    def atualizar_status_pedido(pedido_id, novo_status_id):
        """
        Atualiza o status de um pedido e envia webhook para os endpoints configurados
        """
        pedido = get_object_or_404(Pedido, id=pedido_id)
        status_anterior = pedido.status
        novo_status = get_object_or_404(StatusPedido, id=novo_status_id)
        
        # Se o status não mudou, não fazemos nada
        if pedido.status.id == novo_status.id:
            logger.info(f"Status do pedido #{pedido_id} não foi alterado (já era {pedido.status.nome})")
            return pedido
        
        # Atualiza o status no banco de dados
        pedido.status = novo_status
        pedido.save(update_fields=['status', 'atualizado_em'])
        
        logger.info(f"Status do pedido #{pedido_id} alterado de {status_anterior.nome} para {novo_status.nome}")
        
        try:
            # Envia webhook para todos os endpoints configurados
            resultados = WebhookService.enviar_webhook_status(
                pedido=pedido,
                novo_status=novo_status,
                old_status=status_anterior
            )
            
            # Registra o resultado no log
            sucessos = sum(1 for r in resultados if r.sucesso)
            falhas = len(resultados) - sucessos
            
            if resultados:
                logger.info(f"Webhooks enviados para pedido #{pedido_id}: total={len(resultados)}, sucessos={sucessos}, falhas={falhas}")
            else:
                logger.info(f"Nenhum webhook foi configurado para envio automático para o pedido #{pedido_id}")
                
        except Exception as e:
            logger.error(f"Erro ao enviar webhooks para pedido #{pedido_id}: {str(e)}")
        
        return pedido
    
    @staticmethod
    def listar_status():
        """
        Lista todos os status de pedido disponíveis
        """
        return StatusPedido.objects.filter(ativo=True).order_by('ordem')