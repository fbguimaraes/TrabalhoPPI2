# Guia de Teste Completo - Sistema de E-commerce

## 1. Preparação do Ambiente

### Verificar Servidor Django
- O servidor deve estar rodando em `http://127.0.0.1:8000/`
- Confirme que vê a mensagem: "Django version 5.2.8, using settings 'setup.settings'"
- Sistema check deve retornar: "System check identified no issues"

### Verificar Banco de Dados
```bash
python manage.py migrate
```
- Todas as migrações devem estar aplicadas, incluindo:
  - app.0005_cliente_atualizado_em_cliente_criado_em_and_more
  - payment.0001_initial

---

## 2. Testes de Funcionalidade de Perfil

### 2.1 - Fazer Login
1. Abra http://127.0.0.1:8000/
2. Clique em "Login" (ou será redirecionado automaticamente)
3. Use credenciais de teste:
   - Email: usuario@test.com (ou qualquer usuário existente)
   - Senha: sua_senha

**Resultado Esperado:** Será redirecionado para a página de catálogo

### 2.2 - Acessar Perfil do Usuário
1. Clique no menu de usuário (canto superior direito)
2. Selecione "Meu Perfil" ou acesse diretamente `/perfil/`
3. Você deve ver uma interface com duas abas:
   - "Visualizar Perfil"
   - "Editar Perfil"

**Resultado Esperado:** Página carrega com formato Bootstrap 5

### 2.3 - Fazer Upload de Foto de Perfil
1. Na aba "Editar Perfil"
2. Localize o campo "Foto do Perfil"
3. Arraste uma imagem (JPG, PNG, GIF) com tamanho máximo 5MB
4. OU clique no campo para abrir o seletor de arquivos
5. Clique em "Salvar Alterações"

**Validações a Verificar:**
- ✅ Arquivo com tamanho > 5MB: deve aparecer erro "Arquivo deve ter no máximo 5MB"
- ✅ Arquivo com extensão inválida (.pdf, .txt): deve aparecer erro
- ✅ Arquivo válido: deve ser salvo e aparecer no perfil

**Resultado Esperado:** Foto salva no servidor em `/media/perfil/`

---

## 3. Testes do Carrinho de Compras

### 3.1 - Adicionar Produtos ao Carrinho
1. Vá para http://127.0.0.1:8000/catalogo/
2. Clique em um produto qualquer
3. Clique em "Adicionar ao Carrinho"
4. Selecione a quantidade desejada
5. Clique em "Adicionar"

**Resultado Esperado:** Item adicionado com sucesso, contador do carrinho atualiza

### 3.2 - Verificar Sidebar no Carrinho
1. Vá para http://127.0.0.1:8000/carrinho/
2. Na esquerda, você deve ver uma sidebar com:
   - **Categorias:** Lista de categorias ativas com contagem de produtos
   - **Caixa de Promoção:** "Continue Comprando" para incentivar mais compras
   - **Layout Responsivo:** Em mobile (<768px), sidebar deve aparecer acima do carrinho

**Validações:**
- ✅ Categorias exibem contagem correta de produtos
- ✅ Links de categoria funcionam e filtram o catálogo
- ✅ Sidebar é "sticky" no desktop (permanece visível ao scroll)
- ✅ Sidebar é responsiva no mobile

**Resultado Esperado:** Sidebar carrega corretamente com dados das categorias

### 3.3 - Visualizar Carrinho
1. Você deve ver:
   - Tabela de itens com: Produto | Quantidade | Preço Unit. | Subtotal
   - Botões: Atualizar Quantidade | Remover Item
   - Resumo do Pedido: Subtotal | Impostos (se aplicável) | Total
   - Botão: "Ir para Checkout"

**Resultado Esperado:** Todos os itens e totais calculados corretamente

---

## 4. Testes de Métodos de Pagamento

### 4.1 - Ir para Seleção de Método de Pagamento
1. No carrinho, clique em "Ir para Checkout"
2. OU acesse `/payment/methods/`

**Resultado Esperado:** Página de seleção com 3 opções de pagamento

### 4.2 - Teste: Pagamento com Cartão de Crédito

#### 4.2.1 - Seleção
1. Clique em "Cartão de Crédito"
2. Revise o resumo do pedido

**Resultado Esperado:** Você vê a tela de confirmação pré-Stripe

#### 4.2.2 - Integração Stripe
1. Clique em "Pagar com Stripe"
2. Você será redirecionado para o Stripe Checkout

**Validações:**
- ✅ URL muda para formulário de pagamento do Stripe
- ✅ Valor correto aparece
- ✅ Email do usuário pré-preenchido

**Nota:** Use cartões de teste do Stripe:
- Cartão Válido: `4242 4242 4242 4242`
- Cartão Recusado: `4000 0000 0000 0002`
- Data: Qualquer data futura (ex: 12/25)
- CVC: Qualquer 3 dígitos (ex: 123)

#### 4.2.3 - Verificar Registro de Pagamento
1. Após o pagamento, acesse o Django Admin: `/admin/`
2. Navegue para "Pagamentos"
3. Procure pelo seu pagamento recente

**Validações:**
- ✅ Payment com status "aprovado" ou "processando"
- ✅ payment_method = "cartao"
- ✅ stripe_session_id e stripe_charge_id preenchidos
- ✅ amount = total do pedido
- ✅ transaction_id gerado

**Resultado Esperado:** Registro de pagamento criado corretamente

---

### 4.3 - Teste: Pagamento com Boleto Bancário

#### 4.3.1 - Seleção
1. Retorne ao carrinho (com novos produtos se quiser)
2. Vá para "/payment/methods/"
3. Clique em "Boleto Bancário"
4. Revise as informações
5. Clique em "Gerar Boleto"

**Resultado Esperado:** Boleto é gerado e exibido

#### 4.3.2 - Verificar Detalhes do Boleto
Você deve ver a tela com:
- **Número do Boleto:** Identificador único
- **Banco:** Banco do Brasil
- **Data de Vencimento:** 7 dias a partir de hoje
- **Código de Barras:** Copiável com botão
- **Linha Digitável:** Copiável com botão
- **Instruções de Pagamento:** Passo a passo para pagar
- **Botão Imprimir:** Para imprimir o boleto

**Validações:**
- ✅ Código de barras tem 47 dígitos
- ✅ Linha digitável tem 54 dígitos
- ✅ Número do boleto é único
- ✅ Data de vencimento é 7 dias após a data de emissão
- ✅ Botões de copiar funcionam
- ✅ Formato visual é profissional

#### 4.3.3 - Verificar Registro no Banco de Dados
1. Django Admin → "Pagamentos"
2. Procure pelo pagamento com payment_method = "boleto"
3. Clique para ver detalhes
4. Vá para a seção "Boleto" (deve estar relacionado)

**Validações:**
- ✅ Payment status = "pendente"
- ✅ Boleto com código_barras e linha_digitavel
- ✅ Vencimento = 7 dias
- ✅ Dados do pagador preenchidos

**Resultado Esperado:** Boleto gerado corretamente no banco de dados

---

### 4.4 - Teste: Pagamento com PIX

#### 4.4.1 - Seleção
1. Retorne ao carrinho (adicione novos produtos se quiser)
2. Vá para "/payment/methods/"
3. Clique em "PIX"
4. Você pode opcionalmente inserir uma chave PIX (CPF, email, telefone)
5. OU deixar em branco para gerar chave aleatória
6. Clique em "Gerar QR Code"

**Resultado Esperado:** QR Code é gerado e exibido

#### 4.4.2 - Verificar Detalhes do PIX
Você deve ver:
- **QR Code:** Código 2D de 280x280 pixels (base64)
- **Chave PIX:** Copiável com botão
- **Valor:** Formatado em BRL (R$ X.XXX,XX)
- **Expiração:** "Expira em 15 minutos"
- **Instruções:** Passo a passo para pagar
- **Botão Copiar:** Para copiar a chave PIX

**Validações:**
- ✅ QR Code renderiza corretamente
- ✅ Chave PIX é válida (CPF, email, telefone ou UUID)
- ✅ Tempo de expiração mostra 15 minutos
- ✅ Valor está correto
- ✅ Botão de cópia funciona
- ✅ Layout responsivo

#### 4.4.3 - Verificar Registro no Banco de Dados
1. Django Admin → "Pagamentos PIX"
2. Procure pelo PIX mais recente

**Validações:**
- ✅ PixPayment status = "pendente"
- ✅ qr_code preenchido com string
- ✅ chave_pix gerada ou do usuário
- ✅ valor_final correto
- ✅ data_expiracao = agora + 15 minutos

**Resultado Esperado:** PIX gerado corretamente com QR code válido

---

## 5. Testes de Validação de Dados

### 5.1 - Validação de Tamanho de Arquivo (Perfil)
```
Teste com arquivo > 5MB
Resultado Esperado: Erro "Arquivo deve ter no máximo 5MB"

Teste com arquivo .pdf
Resultado Esperado: Erro "Apenas JPG, PNG e GIF são permitidos"

Teste com arquivo válido
Resultado Esperado: Salvo com sucesso
```

### 5.2 - Validação de Carrinho
```
Teste: Adicionar quantidade inválida
Resultado Esperado: Erro ou limite aplicado

Teste: Remover item
Resultado Esperado: Item desaparece, total atualiza

Teste: Limpar carrinho
Resultado Esperado: Todos os itens removidos
```

### 5.3 - Validação de Pagamento
```
Teste: Payment sem order
Resultado Esperado: Erro (order é obrigatória)

Teste: Boleto com vencimento < hoje
Resultado Esperado: Erro ou aviso

Teste: PIX expirado
Resultado Esperado: Status muda para "expirado"
```

---

## 6. Testes de Estoque

### 6.1 - Verificar Decremento de Estoque
1. Verifique estoque inicial de um produto em `/admin/`
2. Adicione esse produto ao carrinho
3. Conclua o pagamento (qualquer método)
4. Retorne ao admin e revise o estoque

**Resultado Esperado:** Estoque foi decrementado pela quantidade comprada

### 6.2 - Verificar Stock Insuficiente
1. Tente adicionar quantidade > estoque disponível
2. OU modifique a quantidade no carrinho para > estoque

**Resultado Esperado:** 
- Erro é exibido
- OU quantidade é limitada ao máximo disponível
- Checkout é impedido se insuficiente

---

## 7. Testes de Integração

### 7.1 - Flow Completo: Perfil → Carrinho → Pagamento
```
1. Login
2. Upload foto de perfil (validar)
3. Adicionar produtos ao carrinho
4. Visualizar sidebar com categorias
5. Selecionar método de pagamento
6. Completar pagamento
7. Verificar registro no admin
8. Validar decremento de estoque
```

### 7.2 - Flow Múltiplos Pagamentos
```
1. Fazer 1 pagamento por Cartão
2. Fazer 1 pagamento por Boleto
3. Fazer 1 pagamento por PIX
4. Verificar todos os 3 registros no admin
5. Validar que IDs são únicos
```

---

## 8. Testes de Responsividade (Mobile)

### 8.1 - Smartphone (iPhone 12 / 375px)
```
Teste: Carrinho com sidebar
✅ Sidebar aparece ACIMA do carrinho
✅ Largura ajustada para tela pequena
✅ Tabela do carrinho scrola horizontalmente se necessário
✅ Botões são clicáveis (tamanho mínimo 44px)
```

### 8.2 - Tablet (iPad / 768px)
```
Teste: Carrinho com sidebar
✅ Sidebar ainda está acima (breakpoint 768px)
✅ Layout estável
```

### 8.3 - Desktop (1920px)
```
Teste: Carrinho com sidebar
✅ Sidebar aparece à ESQUERDA
✅ Sidebar é sticky (scroll mantém visível)
✅ Largura de 280px para sidebar
✅ Conteúdo principal ocupa espaço restante
```

---

## 9. Checklist Final

- [ ] Servidor Django rodando sem erros
- [ ] Banco de dados com todas as migrações aplicadas
- [ ] Usuário consegue fazer login
- [ ] Upload de foto de perfil funciona
- [ ] Carrinho exibe sidebar com categorias
- [ ] Método de pagamento: Cartão funciona
- [ ] Método de pagamento: Boleto funciona
- [ ] Método de pagamento: PIX funciona
- [ ] Registros de pagamento criados corretamente
- [ ] Estoque foi decrementado após pagamento
- [ ] Admin exibe todos os pagamentos corretamente
- [ ] Responsividade funciona (mobile/desktop)
- [ ] Validações funcionam (arquivo, quantidade, etc)
- [ ] System check Django = 0 issues
- [ ] Database migrations = OK

---

## 10. Troubleshooting

### Problema: "Foto de perfil não salva"
**Solução:**
- Verifique `/media/perfil/` existe
- Verifique permissões de pasta
- Verifique DEBUG=True em settings.py
- Verifique `MEDIA_URL` e `MEDIA_ROOT` em settings.py

### Problema: "Pagamento não aparece no admin"
**Solução:**
- Verifique migrações: `python manage.py migrate payment`
- Verifique payment/admin.py está registrando modelos
- Restart Django: `python manage.py runserver`

### Problema: "Sidebar não aparece no carrinho"
**Solução:**
- Verifique `categorias` está sendo passado na view
- Verifique template carrinho.html usa `{% for categoria in categorias %}`
- Limpe cache do browser (Ctrl+Shift+Delete)

### Problema: "QR Code PIX não renderiza"
**Solução:**
- Verifique qrcode==8.0 está instalado
- Verifique base64 encoding em payment/utils.py
- Reinicie o servidor

---

## 11. Informações de Contato para Suporte

Se encontrar problemas:
1. Verifique logs em `python manage.py runserver` output
2. Revise erros no browser (F12 → Console)
3. Verifique Django System Check errors: `python manage.py check`
4. Revise migrations: `python manage.py showmigrations`

---

**Data de Criação:** 2025-12-09  
**Versão:** 1.0  
**Última Atualização:** 2025-12-09
