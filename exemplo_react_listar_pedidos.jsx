// Exemplo de código React para listar pedidos

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, 
  Paper, Typography, Button, TextField, MenuItem, Select, 
  FormControl, InputLabel, Box, Pagination, CircularProgress
} from '@mui/material';

// URL da API do backend
const API_URL = 'http://seu-backend-url/api/pedidosmontink/pedidos/';

const ListaPedidos = () => {
  // Estado para armazenar os pedidos
  const [pedidos, setPedidos] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Estados para filtros e paginação
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [totalPages, setTotalPages] = useState(0);
  const [search, setSearch] = useState('');
  const [statusList, setStatusList] = useState([]);
  const [statusFiltro, setStatusFiltro] = useState('');
  const [orderBy, setOrderBy] = useState('-criado_em');

  // Busca a lista de status disponíveis
  const fetchStatusList = async () => {
    try {
      const response = await axios.get('http://seu-backend-url/api/pedidosmontink/pedidos/status/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      setStatusList(response.data.results);
    } catch (error) {
      console.error('Erro ao buscar lista de status:', error);
    }
  };

  // Função para buscar os pedidos
  const fetchPedidos = async () => {
    setLoading(true);
    try {
      const params = {
        page,
        page_size: pageSize,
        search: search || undefined,
        status: statusFiltro || undefined,
        order_by: orderBy
      };

      const response = await axios.get(API_URL, {
        params,
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      setPedidos(response.data.results);
      setTotalPages(response.data.total_pages);
    } catch (error) {
      console.error('Erro ao buscar pedidos:', error);
    } finally {
      setLoading(false);
    }
  };

  // Efeito para carregar os pedidos quando os filtros mudarem
  useEffect(() => {
    fetchPedidos();
  }, [page, pageSize, orderBy]);

  // Efeito para carregar a lista de status no carregamento inicial
  useEffect(() => {
    fetchStatusList();
  }, []);

  // Função para lidar com a mudança de página
  const handlePageChange = (event, value) => {
    setPage(value);
  };

  // Função para aplicar filtros
  const aplicarFiltros = () => {
    setPage(1); // Reset para a primeira página ao aplicar filtros
    fetchPedidos();
  };

  // Função para formatar a data
  const formatarData = (dataString) => {
    const data = new Date(dataString);
    return data.toLocaleDateString('pt-BR') + ' ' + 
           data.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
  };

  // Função para formatar valores monetários
  const formatarValor = (valor) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(valor);
  };

  return (
    <div>
      <Typography variant="h4" gutterBottom>
        Pedidos Recebidos
      </Typography>

      {/* Filtros */}
      <Box mb={3} display="flex" flexWrap="wrap" gap={2} alignItems="flex-end">
        <TextField
          label="Buscar"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          size="small"
          variant="outlined"
        />

        <FormControl size="small" style={{ minWidth: 200 }}>
          <InputLabel>Status</InputLabel>
          <Select
            value={statusFiltro}
            onChange={(e) => setStatusFiltro(e.target.value)}
            label="Status"
          >
            <MenuItem value="">Todos</MenuItem>
            {statusList.map((status) => (
              <MenuItem key={status.id} value={status.id}>
                {status.nome}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <Button 
          variant="contained" 
          color="primary" 
          onClick={aplicarFiltros}
        >
          Filtrar
        </Button>
      </Box>

      {/* Tabela de pedidos */}
      {loading ? (
        <Box display="flex" justifyContent="center" my={4}>
          <CircularProgress />
        </Box>
      ) : (
        <>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Nº Pedido</TableCell>
                  <TableCell>Cliente</TableCell>
                  <TableCell>Produto</TableCell>
                  <TableCell>Valor</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Data</TableCell>
                  <TableCell>Ações</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {pedidos.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} align="center">
                      Nenhum pedido encontrado
                    </TableCell>
                  </TableRow>
                ) : (
                  pedidos.map((pedido) => (
                    <TableRow key={pedido.id}>
                      <TableCell>#{pedido.numero_pedido}</TableCell>
                      <TableCell>{pedido.nome_cliente}</TableCell>
                      <TableCell>{`${pedido.nome_produto} (${pedido.quantidade})`}</TableCell>
                      <TableCell>{formatarValor(pedido.valor_pedido)}</TableCell>
                      <TableCell>
                        <span
                          style={{
                            backgroundColor: pedido.status_cor || '#777',
                            color: '#fff',
                            padding: '3px 10px',
                            borderRadius: '10px',
                            fontSize: '12px',
                            fontWeight: 'bold',
                          }}
                        >
                          {pedido.status_nome}
                        </span>
                      </TableCell>
                      <TableCell>{formatarData(pedido.criado_em)}</TableCell>
                      <TableCell>
                        <Button
                          variant="outlined"
                          size="small"
                          onClick={() => {/* Navegação para detalhes */}}
                        >
                          Ver detalhes
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>

          {/* Paginação */}
          <Box mt={2} display="flex" justifyContent="center">
            <Pagination
              count={totalPages}
              page={page}
              onChange={handlePageChange}
              color="primary"
            />
          </Box>
        </>
      )}
    </div>
  );
};

export default ListaPedidos;
