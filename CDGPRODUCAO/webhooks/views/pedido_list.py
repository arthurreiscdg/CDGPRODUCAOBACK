import logging
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from django.shortcuts import get_object_or_404
from webhooks.models import Pedido, Webhook
from webhooks.serializers import PedidoSerializer

logger = logging.getLogger(__name__)

class PedidoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações com o modelo Pedido.
    
    Este viewset permite listar, criar, atualizar e excluir pedidos,
    além de fornecer endpoints adicionais para operações específicas.
    """
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Personaliza a query com filtros opcionais."""
        queryset = Pedido.objects.all().order_by('-criado_em')
        
        # Filtro por número de pedido
        numero_pedido = self.request.query_params.get('numero_pedido')
        if numero_pedido:
            queryset = queryset.filter(numero_pedido=numero_pedido)
        
        # Filtro por status
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filtro por nome do cliente
        cliente = self.request.query_params.get('cliente')
        if cliente:
            queryset = queryset.filter(nome_cliente__icontains=cliente)
            
        return queryset
    
    @action(detail=False, methods=['post'])
    def criar_do_webhook(self, request):
        """
        Cria um novo pedido a partir de um webhook existente.
        
        Este endpoint recebe o ID de um webhook e cria um pedido
        com base no payload desse webhook.
        """
        webhook_id = request.data.get('webhook_id')
        if not webhook_id:
            return Response(
                {'error': 'ID do webhook é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            webhook = get_object_or_404(Webhook, id=webhook_id)
            pedido = Pedido.criar_do_webhook(webhook)
            
            serializer = self.get_serializer(pedido)
            return Response(
                {'message': 'Pedido criado com sucesso', 'data': serializer.data},
                status=status.HTTP_201_CREATED
            )
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            logger.error(f"Erro ao criar pedido do webhook: {str(e)}")
            return Response(
                {'error': 'Erro interno ao criar pedido'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def atualizar_status(self, request, pk=None):
        """
        Atualiza o status de um pedido existente.
        
        Este endpoint recebe o novo status e atualiza o pedido,
        opcionalmente enviando webhooks de notificação.
        """
        pedido = self.get_object()
        novo_status = request.data.get('status')
        
        if not novo_status:
            return Response(
                {'error': 'O status é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Atualiza o status do pedido
            pedido.status = novo_status
            pedido.save()
            
            # TODO: Enviar webhook de notificação de status se necessário
            
            serializer = self.get_serializer(pedido)
            return Response(
                {'message': 'Status atualizado com sucesso', 'data': serializer.data},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Erro ao atualizar status do pedido: {str(e)}")
            return Response(
                {'error': 'Erro interno ao atualizar status'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )