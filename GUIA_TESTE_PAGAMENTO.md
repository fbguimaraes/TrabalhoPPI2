# 🛒 Guia de Teste do Sistema de Pagamento

## Fluxo Completo de Compra

### Passo 1: Login
1. Acesse: `http://127.0.0.1:8000/`
2. Clique em "Login"
3. Email: `fabssguimaraes@gmail.com`
4. Senha: (a senha que você cadastrou)

### Passo 2: Adicionar Produto ao Carrinho
1. Clique em "Catálogo" ou acesse `/catalogo/`
2. Escolha um produto (ex: "Inversor Solar Fronius")
3. Clique no produto para ver detalhes
4. Selecione a quantidade (ex: 1)
5. Clique em "🛒 Adicionar ao Carrinho"
6. Será redirecionado para o catálogo

### Passo 3: Visualizar Carrinho
1. Clique em "🛒 Carrinho" no header
2. Ou acesse diretamente: `/carrinho/`
3. Você deve ver:
   - Produto adicionado
   - Quantidade
   - Preço unitário
   - Subtotal
   - Botão "Ir para Checkout"

### Passo 4: Checkout
1. Clique em "Ir para Checkout"
2. Preencha o formulário:
   - Nome
   - Sobrenome
   - Email
   - Endereço
   - CEP
   - Cidade
3. Clique em "Criar Pedido"

### Passo 5: Processamento de Pagamento
1. Você será direcionado para `/payment/process/`
2. Veja o resumo do pedido:
   - Itens comprados
   - Preços unitários
   - Total
3. Clique em "Pagar com Stripe"

#### Opções de Teste:

**Opção A: Com chaves reais do Stripe**
- Se tem chaves válidas no `.env`:
  - Será redirecionado para checkout.stripe.com
  - Use cartão de teste: `4242 4242 4242 4242`
  - Data: qualquer futura (ex: 12/25)
  - CVC: qualquer (ex: 123)

**Opção B: Modo de simulação (padrão)**
- Se as chaves não forem válidas:
  - Sistema redireciona automaticamente para página de sucesso
  - Mostra aviso: "Usando modo de simulação"

### Passo 6: Confirmação de Pagamento
1. Página de sucesso: `/payment/completed/`
2. Mensagem: "✅ Pagamento realizado com sucesso!"
3. Botão para voltar ao catálogo

## Verificação no Admin

### Ver Pedidos Criados
1. Acesse: `http://127.0.0.1:8000/admin/`
2. Login com credenciais de admin
3. Vá para "Orders"
4. Você deve ver o pedido criado com status "Pago" ✅

### Campos do Pedido
- Order ID
- Cliente (nome, email)
- Endereço
- Data criada
- Status "Paid" (checkbox marcado)
- Stripe ID (SIM_<id> ou session_id real)

## Debugging

### Se der erro 500:
1. Verifique o terminal onde o servidor está rodando
2. Procure por "ERROR" ou "Traceback"
3. Verifique se:
   - `.env` tem as variáveis corretas
   - Modelos estão com os nomes certos (produto.nome, não product.name)
   - Ordem foi criada antes de processar pagamento

### Logs Úteis:
- Terminal do servidor mostra todos os requests
- Arquivo `logs/` se existir
- Console do navegador (F12)

## Checklist Esperado

✅ Login funcionando
✅ Adicionar produtos ao carrinho
✅ Ver carrinho com itens
✅ Preencher formulário de checkout
✅ Criar Order no banco de dados
✅ Ver resumo de pagamento
✅ Redirecionar para Stripe (ou simulação)
✅ Marcar Order como "Paid"
✅ Ver pedido no admin
✅ Receber mensagem de sucesso

