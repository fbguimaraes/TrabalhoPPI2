# 🛠️ GUIA PRÁTICO - COMO TESTAR O SISTEMA DE PAGAMENTO

## 🚀 Início Rápido (5 minutos)

### 1. Certifique-se que o Servidor Está Rodando
```bash
# No terminal, na pasta do projeto:
.\venv\Scripts\Activate.ps1
python manage.py runserver 8000
```

✅ Deve exibir: `Starting development server at http://127.0.0.1:8000/`

### 2. Abra o Navegador
```
http://127.0.0.1:8000/
```

### 3. Faça Login
- Email: `fabssguimaraes@gmail.com`
- Senha: (a que você cadastrou)

---

## 🛍️ Fluxo Passo a Passo

### Passo 1: Ir ao Catálogo
1. Clique em "Catálogo" na home
2. Ou acesse: `/catalogo/`
3. Veja lista de produtos disponíveis

### Passo 2: Escolher um Produto
1. Clique em qualquer produto (ex: "Inversor Solar Fronius")
2. Será aberto detalhe com:
   - Imagem grande
   - Descrição
   - Preço
   - Estoque disponível
   - Campo de quantidade
   - Botão "🛒 Adicionar ao Carrinho"

### Passo 3: Adicionar ao Carrinho
1. Altere a quantidade se quiser (ex: 2)
2. Clique no botão "🛒 Adicionar ao Carrinho"
3. Será redirecionado para catálogo
4. ✅ Produto adicionado com sucesso!

### Passo 4: Visualizar Carrinho
1. Clique em "🛒 Carrinho" no header
2. Ou acesse: `/carrinho/`
3. Veja:
   - Imagem do produto
   - Nome
   - Preço unitário
   - Quantidade
   - Subtotal
   - **TOTAL A PAGAR**

### Passo 5: Ir para Checkout
1. Clique no botão "Ir para Checkout"
2. Ou acesse: `/orders/create/`

### Passo 6: Preencher Dados de Entrega
Preencha o formulário com:
- **Nome**: (seu nome)
- **Sobrenome**: (seu sobrenome)
- **Email**: (seu email)
- **Endereço**: (rua e número)
- **CEP**: (12345-678)
- **Cidade**: (sua cidade)

✅ Todos os campos são obrigatórios

### Passo 7: Criar Pedido
1. Clique no botão "Criar Pedido"
2. Sistema irá:
   - Criar Order no banco de dados
   - Criar OrderItems com preços
   - Limpar carrinho
   - Redirecionar para pagamento

### Passo 8: Resumo de Pagamento
Você será levado para `/payment/process/` onde verá:
- Lista de itens comprados
- Preço de cada item
- **TOTAL A PAGAR**
- Botão "Pagar com Stripe"

### Passo 9: Processar Pagamento
1. Clique no botão "Pagar com Stripe"
2. **Opções:**

#### Opção A: Modo Simulação (padrão)
- Se as chaves do Stripe não forem válidas
- Sistema exibe: "⚠️ Usando modo de simulação"
- Automaticamente marca pedido como pago
- Redireciona para página de sucesso

#### Opção B: Stripe Real (com chaves)
- Se tiver chaves válidas no `.env`
- Será redirecionado para checkout.stripe.com
- Use cartão de teste: `4242 4242 4242 4242`
- Qualquer data futura e CVC
- Após pagamento, retorna para sucesso

### Passo 10: Confirmar Sucesso
Página `/payment/completed/` exibe:
- ✅ "Pagamento realizado com sucesso!"
- Botão "Voltar ao Catálogo"
- **Seu pedido foi criado e pago!**

---

## 📊 Verificar Pedido no Admin

### 1. Acessar Admin
```
http://127.0.0.1:8000/admin/
```

Faça login com credenciais de admin (superuser)

### 2. Ver Orders
1. No menu lateral, clique em "Orders"
2. Veja lista de todos os pedidos criados
3. Para cada order, veja:
   - Order ID (#1, #2, #3...)
   - Cliente (nome)
   - Email
   - Data criada
   - **Paid** (checkbox) - ✅ deve estar marcado
   - Stripe ID

### 3. Clicar em um Order
1. Clique em um pedido
2. Veja detalhes completos:
   - Primeiro e último nome
   - Email
   - Endereço completo
   - Cidade e CEP
   - Data de criação e atualização
   - Status "Paid"
   - Stripe ID

### 4. Ver OrderItems
Na mesma página, role para baixo e veja:
- **Order Items:**
  - Produto (nome)
  - Preço (capturado no momento da compra)
  - Quantidade
  - Total

---

## 🧪 Testes Automáticos

### Teste de Fluxo Completo
```bash
python test_payment_flow.py
```

Resultado esperado:
```
✅ Cliente encontrado
✅ Carrinho preparado
✅ Produtos adicionados
✅ Order criada
✅ OrderItems criados
✅ Pagamento simulado
✅ TESTE COMPLETO COM SUCESSO!
```

### Teste HTTP
```bash
python test_http_checkout.py
```

Resultado esperado:
```
✅ Preparando ambiente
✅ Fazendo login
✅ Acessando carrinho
✅ Criando pedido
✅ Processando pagamento
✅ TESTE COMPLETO COM SUCESSO!
```

### Teste de Carrinho
```bash
python test_full_cart_flow.py
```

Resultado esperado:
```
✅ Cliente encontrado
✅ Carrinho preparado
✅ Produtos adicionados
✅ Total calculado corretamente
✅ TESTE CONCLUÍDO COM SUCESSO!
```

---

## 🐛 Resolução de Problemas

### Problema: "Erro 500" na página de pagamento

**Causa**: Atributo de produto incorreto
**Solução**: ✅ Já foi corrigido! (product.nome em vez de product.name)

### Problema: "Carrinho vazio" após checkout

**Causa**: Carrinho foi limpo propositalmente
**Solução**: Comece nova compra - clique em novo produto

### Problema: "Dados inválidos" no formulário de checkout

**Solução**:
1. Verifique se todos os campos foram preenchidos
2. Certifique-se de que Email é válido
3. CEP deve estar no formato: 12345-678

### Problema: "Pedido não criado"

**Solução**:
1. Verifique se está logado
2. Certifique-se de que carrinho tem itens
3. Verifique logs no terminal (erros em vermelho)

### Problema: "Stripe error"

**Solução**:
1. Se não tem chaves, sistema usa modo simulação (OK)
2. Se quer testar com chaves reais:
   - Adicione em `.env`
   - Use cartão de teste do Stripe

---

## ✅ Checklist de Funcionalidades

- [ ] Conseguir fazer login
- [ ] Acessar catálogo de produtos
- [ ] Ver detalhe de um produto
- [ ] Adicionar produto ao carrinho
- [ ] Ver carrinho com itens
- [ ] Remover item do carrinho
- [ ] Preencher formulário de checkout
- [ ] Criar pedido
- [ ] Ver resumo de pagamento
- [ ] Processar pagamento
- [ ] Receber confirmação de sucesso
- [ ] Ver pedido no admin
- [ ] Confirmar pedido está marcado como "PAID"

---

## 📈 Próximas Melhorias (Opcional)

1. **Email de Confirmação**
   - Enviar comprovante para o email do cliente

2. **Webhook de Stripe**
   - Receber notificações de pagamento em tempo real
   - Atualizar status automaticamente

3. **Dashboard de Pedidos**
   - Página para usuário ver seus pedidos
   - Histórico de compras

4. **Relatórios**
   - Dashboard administrativo
   - Gráficos de vendas
   - Total de receita

---

## 📞 Ajuda Rápida

| Problema | Solução |
|----------|---------|
| Servidor não inicia | Ative venv: `.\venv\Scripts\Activate.ps1` |
| Porta 8000 ocupada | Mude porta: `runserver 8001` |
| Erro de autenticação | Verifique se está logado |
| Produto não aparece | Certifique-se que `ativo=True` |
| Preço errado | Verifique `produto.preco` |
| Carrinho não aparece | Use `/carrinho/` manualmente |

---

## 🎉 Resumo

Você agora pode:

✅ Fazer login
✅ Adicionar produtos ao carrinho
✅ Fazer checkout
✅ Simular pagamento
✅ Confirmar pedido
✅ Ver pedidos no admin

**Tudo está funcionando!** 🚀

Para usar com chaves reais do Stripe, siga as instruções em `IMPLEMENTACAO_PAGAMENTO.md`.

