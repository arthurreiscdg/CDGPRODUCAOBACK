from django.db import transaction
from ..models import Pedido, StatusPedido
from .webhook_service import WebhookService


class PedidoService:
    """
    Serviço para gerenciamento de pedidos.
    Implementa a lógica de alteração de status e outras operações relacionadas a pedidos.
    """
    
    @staticmethod
    def obter_pedido(pedido_id):
        """
        Obtém um pedido pelo seu ID.
        
        Args:
            pedido_id (int): ID do pedido
            
        Returns:
            Pedido: Instância do pedido ou None se não encontrado
        """
        try:
            return Pedido.objects.get(id=pedido_id)
        except Pedido.DoesNotExist:
            return None
    
    @staticmethod
    def obter_pedido_por_numero(numero_pedido):
        """
        Obtém um pedido pelo seu número de pedido.
        
        Args:
            numero_pedido (int): Número do pedido
            
        Returns:
            Pedido: Instância do pedido ou None se não encontrado
        """
        try:
            return Pedido.objects.get(numero_pedido=numero_pedido)
        except Pedido.DoesNotExist:
            return None
    
    @classmethod
    @transaction.atomic
    def alterar_status(cls, pedido_id, novo_status_nome, enviar_webhook=True):
        """
        Altera o status de um pedido e opcionalmente envia webhook de notificação.
        
        Args:
            pedido_id (int): ID do pedido
            novo_status_nome (str): Nome do novo status
            enviar_webhook (bool): Se True, envia webhook de notificação
            
        Returns:
            tuple: (Pedido, StatusPedido, list) - Pedido atualizado, status e webhooks enviados (se aplicável)
        """
        # Obtém o pedido
        pedido = cls.obter_pedido(pedido_id)
        if not pedido:
            return None, None, []
        
        # Obtém ou cria o status
        status, _ = StatusPedido.objects.get_or_create(
            nome=novo_status_nome,
            defaults={'descricao': f'Status {novo_status_nome}'}
        )
        
        # Atualiza o pedido
        pedido.status = status
        pedido.save(update_fields=['status', 'atualizado_em'])
        
        webhooks_enviados = []
        # Envia webhook de atualização se solicitado
        if enviar_webhook:
            webhooks_enviados = WebhookService.enviar_webhook_status(pedido, status.nome)
        
        return pedido, status, webhooks_enviados
    
    @classmethod
    def listar_pedidos(cls, filtros=None, ordenacao='-criado_em'):
        """
        Lista pedidos com filtros opcionais.
        
        Args:
            filtros (dict): Dicionário de filtros para aplicar à query
            ordenacao (str): Campo para ordenação
            
        Returns:
            QuerySet: Pedidos filtrados e ordenados
        """
        query = Pedido.objects.all()
        
        if filtros:
            query = query.filter(**filtros)
            
        return query.order_by(ordenacao)
