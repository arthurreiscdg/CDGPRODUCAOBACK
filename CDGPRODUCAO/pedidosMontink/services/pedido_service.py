from ..models.webhook_pedido import Pedido, StatusPedido
from django.shortcuts import get_object_or_404


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
        Atualiza o status de um pedido
        """
        pedido = get_object_or_404(Pedido, id=pedido_id)
        status = get_object_or_404(StatusPedido, id=novo_status_id)
        
        pedido.status = status
        pedido.save(update_fields=['status', 'atualizado_em'])
        
        return pedido
    
    @staticmethod
    def listar_status():
        """
        Lista todos os status de pedido disponíveis
        """
        return StatusPedido.objects.filter(ativo=True).order_by('ordem')