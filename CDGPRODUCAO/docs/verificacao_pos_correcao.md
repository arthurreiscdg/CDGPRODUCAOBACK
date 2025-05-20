# Verificação Pós-Correção do Upload de PDFs

Este documento contém instruções para verificar se as correções aplicadas ao sistema de upload de PDFs no Google Drive estão funcionando corretamente.

## 1. Verificação do Ambiente

Execute o script `tests/verificar_upload_pdf.py` para realizar uma verificação completa do ambiente e testar o upload de um PDF:

```bash
python tests/verificar_upload_pdf.py
```

Este script fará o seguinte:
- Verificar a conexão com o Google Drive
- Verificar a estrutura de pastas
- Criar um PDF de teste e fazer o upload
- Verificar se os links foram gerados corretamente

## 2. Verificação do Banco de Dados

Execute o script `tests/verificar_registros_formularios.py` para verificar os registros existentes no banco de dados:

```bash
python tests/verificar_registros_formularios.py
```

Este script fará o seguinte:
- Listar todos os formulários no banco de dados
- Identificar formulários sem links de download
- Mostrar detalhes dos 5 formulários mais recentes
- Opcionalmente, tentar corrigir formulários sem links

## 3. Teste Manual com a Interface Web

1. Abra o navegador e acesse a interface do sistema
2. Navegue até o formulário ZeroHum
3. Preencha os campos obrigatórios e anexe um arquivo PDF
4. Envie o formulário e verifique:
   - Se a submissão é bem-sucedida
   - Se o sistema mostra os links de download e visualização
   - Se os links realmente funcionam quando clicados

## 4. Verificação dos Logs

Verifique os arquivos de log para garantir que não há erros relacionados ao upload:

```bash
# Visualize os logs mais recentes
tail -n 100 logs/debug.log | grep "Google Drive\\|ZeroHum\\|upload_pdf"
```

## 5. Verificação no Google Drive

1. Acesse o [Google Drive](https://drive.google.com) usando a conta configurada
2. Verifique se a pasta "ZeroHum" foi criada
3. Abra a pasta e confirme se os arquivos PDF estão sendo salvos corretamente
4. Verifique as permissões de compartilhamento dos arquivos

## 6. Checklist Final

- [ ] A conexão com o Google Drive está funcionando
- [ ] A pasta "ZeroHum" está sendo criada corretamente
- [ ] Os PDFs estão sendo enviados para o Google Drive
- [ ] Os links de download e visualização estão sendo gerados
- [ ] Os links estão sendo salvos no banco de dados
- [ ] Os links funcionam corretamente quando acessados

## Problemas Comuns e Soluções

### Erro na Inicialização do Drive

Se o sistema não conseguir inicializar o Google Drive na inicialização do Django, execute manualmente:

```bash
python inicializar_drive.py
```

### Permissões de Pasta Inconsistentes

Se os arquivos estão sendo criados, mas não podem ser acessados por link, verifique as permissões:

```bash
python testar_drive_simples.py --check-permissions
```

### Arquivos Sem Links

Se os arquivos estão sendo enviados, mas os links não são gerados, tente corrigir os links:

```bash
python tests/verificar_registros_formularios.py
# Responda 's' quando perguntado sobre corrigir links
```

## Monitoramento Contínuo

Recomenda-se monitorar o sistema por algumas semanas após a correção para garantir que o problema foi completamente resolvido. Verifique periodicamente os logs e os novos formulários criados.
