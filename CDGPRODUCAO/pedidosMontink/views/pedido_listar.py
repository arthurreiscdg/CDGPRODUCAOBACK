from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models.webhook_pedido import Pedido, StatusPedido
from ..serializers.pedido_serializers import PedidoSerializer, PedidoListSerializer, StatusPedidoSerializer
from ..services.pedido_service import PedidoService
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter


class PedidoPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class WebhookListarView(generics.ListAPIView):
    """
    View para listar pedidos com filtros
    """
    serializer_class = PedidoListSerializer
    pagination_class = PedidoPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['numero_pedido', 'nome_cliente', 'sku', 'nome_produto']
    ordering_fields = ['numero_pedido', 'criado_em', 'status__ordem']
    ordering = ['-criado_em']

    def get_queryset(self):
        filtros = {}
        
        # Filtro por número do pedido
        numero_pedido = self.request.query_params.get('numero_pedido', None)
        if numero_pedido:
            filtros['numero_pedido'] = numero_pedido

        # Filtro por SKU
        sku = self.request.query_params.get('sku', None)
        if sku:
            filtros['sku'] = sku
            
        # Filtro por status
        status_id = self.request.query_params.get('status', None)
        if status_id:
            filtros['status'] = status_id
            
        # Filtro por data de emissão (criado_em)
        data_inicio = self.request.query_params.get('data_inicio', None)
        if data_inicio:
            filtros['data_inicio'] = data_inicio
            
        data_fim = self.request.query_params.get('data_fim', None)
        if data_fim:
            filtros['data_fim'] = data_fim
        
        return PedidoService.listar_pedidos(filtros)


class PedidoDetailView(generics.RetrieveAPIView):
    """
    View para obter detalhes de um pedido específico
    """
    serializer_class = PedidoSerializer
    queryset = Pedido.objects.select_related('status')
    

class AtualizarStatusPedidoView(APIView):
    """
    View para atualizar o status de um pedido
    """
    def patch(self, request, pk):
        status_id = request.data.get('status_id')
        if not status_id:
            return Response(
                {"erro": "ID do status não fornecido"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            pedido = PedidoService.atualizar_status_pedido(pk, status_id)
            return Response(PedidoSerializer(pedido).data)
        except Exception as e:
            return Response(
                {"erro": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class StatusPedidoListView(generics.ListAPIView):
    """
    View para listar todos os status de pedido disponíveis
    """
    queryset = StatusPedido.objects.filter(ativo=True).order_by('ordem')
    serializer_class = StatusPedidoSerializer


class AtualizarStatusPedidosEmLoteView(APIView):
    """
    View para atualizar o status de múltiplos pedidos em lote
    """
    def post(self, request):
        # Obtém os IDs dos pedidos e o novo status
        pedido_ids = request.data.get('pedido_ids', [])
        status_id = request.data.get('status_id')
        
        # Valida os dados recebidos
        if not pedido_ids:
            return Response(
                {"erro": "Nenhum pedido selecionado"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if not status_id:
            return Response(
                {"erro": "ID do status não fornecido"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Converte para lista se veio como string
        if isinstance(pedido_ids, str):
            try:
                pedido_ids = [int(pid.strip()) for pid in pedido_ids.split(',') if pid.strip()]
            except ValueError:
                return Response(
                    {"erro": "Formato inválido para IDs dos pedidos"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        # Realiza a atualização em lote
        try:
            resultado = PedidoService.atualizar_status_pedidos_em_lote(pedido_ids, status_id)
            return Response(resultado)
        except Exception as e:
            return Response(
                {"erro": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )