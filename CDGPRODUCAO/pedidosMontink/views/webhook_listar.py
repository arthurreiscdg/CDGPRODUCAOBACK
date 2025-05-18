from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from ..models.webhook_pedido import Pedido, StatusPedido
from ..serializers.pedido_serializers import PedidoListSerializer, StatusPedidoSerializer


class WebhookListarView(APIView):
    """
    View para listar todos os pedidos recebidos via webhook.
    Suporta paginação e filtros básicos.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retorna uma lista paginada de pedidos recebidos via webhook.
        
        Parâmetros de consulta:
        - page: número da página (padrão: 1)
        - page_size: número de registros por página (padrão: 10)
        - search: termo de busca (opcional)
        - status: filtrar por status do pedido (opcional)
        - order_by: ordenar por campo (padrão: -criado_em)
        """
        try:
            # Parâmetros de paginação
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            
            # Parâmetros de filtro
            search = request.query_params.get('search', None)
            status_id = request.query_params.get('status', None)
            order_by = request.query_params.get('order_by', '-criado_em')
            
            # Aplicar filtros
            queryset = Pedido.objects.all()
            
            if search:
                queryset = queryset.filter(
                    Q(numero_pedido__icontains=search) |
                    Q(nome_cliente__icontains=search) |
                    Q(email_cliente__icontains=search) |
                    Q(nome_produto__icontains=search)
                )
            
            if status_id:
                queryset = queryset.filter(status_id=status_id)
            
            # Ordenação
            queryset = queryset.order_by(order_by)
            
            # Paginação
            start = (page - 1) * page_size
            end = start + page_size
            
            # Total de registros
            total = queryset.count()
            
            # Serialização
            serializer = PedidoListSerializer(queryset[start:end], many=True)
            
            return Response({
                'results': serializer.data,
                'count': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StatusPedidoListView(APIView):
    """
    View para listar todos os status de pedidos disponíveis.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Retorna uma lista de todos os status de pedidos disponíveis.
        """
        try:
            queryset = StatusPedido.objects.filter(ativo=True).order_by('ordem')
            serializer = StatusPedidoSerializer(queryset, many=True)
            
            return Response({
                'results': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)