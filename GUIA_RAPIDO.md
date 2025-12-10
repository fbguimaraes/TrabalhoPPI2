# 🚀 Guia Rápido de Início

## ⚡ Setup em 5 Minutos

### 1. Preparar Ambiente
```bash
# Entrar no diretório
cd "c:\Users\fbznn\Nova pasta\trabalhoPPI2"

# Ativar virtual environment
.\env\Scripts\activate

# Instalar dependências (se não instaladas)
pip install -r requirements.txt
```

### 2. Configurar Banco de Dados
```bash
# Aplicar migrações
python manage.py migrate

# Criar super usuário (admin)
python manage.py createsuperuser
# Username: admin
# Email: admin@example.com
# Password: (sua senha)
```

### 3. Iniciar Servidor
```bash
python manage.py runserver
```

**Acesso:**
- 🌐 Site: http://127.0.0.1:8000/
- 🔐 Admin: http://127.0.0.1:8000/admin/
- 💳 Pagamento: http://127.0.0.1:8000/payment/methods/

---

## 📋 Fluxo Básico de Teste

### 1. Login
1. Vá para http://127.0.0.1:8000/
2. Faça login com suas credenciais

### 2. Adicionar Produto ao Carrinho
1. Vá para "/catalogo/"
2. Clique em um produto
3. Clique "Adicionar ao Carrinho"
4. Escolha quantidade
5. Clique "Adicionar"

### 3. Ir para Checkout
1. Vá para "/carrinho/"
2. Veja a sidebar com categorias (novo!)
3. Clique "Ir para Checkout"

### 4. Escolher Método de Pagamento
Escolha um dos 3:

#### Opção A: Cartão de Crédito
- Clique em "Cartão de Crédito"
- Clique "Pagar com Stripe"
- Use cartão de teste: `4242 4242 4242 4242`
- Data: `12/25` | CVC: `123`
- Pague

#### Opção B: Boleto
- Clique em "Boleto Bancário"
- Clique "Gerar Boleto"
- Copie código de barras ou linha digitável
- Vencimento em 7 dias

#### Opção C: PIX
- Clique em "PIX"
- Deixe em branco para chave aleatória OU insira sua chave
- Clique "Gerar QR Code"
- Escaneie o QR com app PIX
- Pague

### 5. Verificar Pagamento no Admin
1. Vá para http://127.0.0.1:8000/admin/
2. Clique em "Pagamentos"
3. Veja seu pagamento listado
4. Clique para ver detalhes
5. Verifique se estoque foi decrementado

---

## 🔧 Configuração Stripe (Opcional)

Para testar cartão de crédito:

### 1. Criar Conta Stripe
1. Vá para https://dashboard.stripe.com
2. Registre-se (gratuito)
3. Vá para "Developers" → "API keys"
4. Copie "Secret key" e "Publishable key"

### 2. Configurar .env
```env
STRIPE_SECRET_KEY=sk_test_sua_chave_aqui
STRIPE_PUBLISHABLE_KEY=pk_test_sua_chave_aqui
STRIPE_API_VERSION=2024-11-20
```

### 3. Testar Cartões
| Cartão | Número | Resultado |
|--------|--------|-----------|
| Válido | 4242 4242 4242 4242 | ✅ Aprovado |
| Recusado | 4000 0000 0000 0002 | ❌ Recusado |
| CVC Inválido | 4000 0000 0000 0127 | ❌ CVC falha |

Data: Qualquer futura (ex: 12/25)  
CVC: Qualquer 3 dígitos (ex: 123)

---

## 📸 Upload de Foto de Perfil

### Onde?
1. Vá para "/perfil/"
2. Clique na aba "Editar Perfil"
3. Arraste uma imagem no campo "Foto do Perfil"

### Requisitos
- ✅ Formatos: JPG, PNG, GIF
- ✅ Tamanho máximo: 5MB
- ✅ Resolução: Qualquer (será redimensionada)

### Onde fica salva?
```
/media/perfil/seu_nome_arquivo.jpg
```

---

## 🛒 Sidebar do Carrinho (NOVO!)

### O que é?
Menu lateral que aparece no carrinho com:
- Lista de categorias com contagem de produtos
- Caixa de promoção "Continue Comprando"
- Links diretos para filtrar por categoria

### Como funciona?
1. Vai para "/carrinho/"
2. No desktop (>768px): sidebar aparece à esquerda
3. No mobile (<768px): sidebar aparece acima da tabela
4. Clique em uma categoria para filtrar produtos
5. Volte ao carrinho para continuar

---

## 🐛 Verificar Problemas

### Servidor não inicia?
```bash
python manage.py check
```

### Migrações não aplicadas?
```bash
python manage.py showmigrations
python manage.py migrate
```

### Erro de módulo?
```bash
pip install -r requirements.txt
```

### Erro de arquivo?
```bash
python manage.py collectstatic
```

---

## 📊 Banco de Dados

### Ver Dados no Admin
1. http://127.0.0.1:8000/admin/
2. Usuário: `admin`
3. Senha: (que você criou)

### Modelos Disponíveis
- **App:**
  - Clientes
  - Categorias
  - Produtos
  - Carrinhos
  - Itens do Carrinho

- **Payment:**
  - Pagamentos
  - Boletos
  - Pagamentos PIX

- **Orders:**
  - Pedidos
  - Itens do Pedido

---

## 📞 Contato de Suporte

### Documentação Completa
- 📖 Veja `DOCUMENTACAO_TECNICA.md`
- 🧪 Veja `GUIA_TESTE_SISTEMA_COMPLETO.md`

### Informações Técnicas
- Framework: Django 5.2.8
- Python: 3.12.4
- Banco de Dados: SQLite (desenvolvimento)
- Framework CSS: Bootstrap 5.3.0

### Erros Comuns
```
Erro: "Foto não salva"
→ Verifique pasta /media/perfil/ tem permissão de escrita

Erro: "Pagamento não aparece no admin"
→ Reinicie o servidor: python manage.py runserver

Erro: "QR Code não aparece"
→ Instale qrcode: pip install qrcode[pil]==8.0

Erro: "Sidebar não aparece no carrinho"
→ Limpe cache do browser: Ctrl+Shift+Delete
```

---

## 🎯 Checklist de Verificação

Após iniciar o servidor:

- [ ] Servidor rodando em http://127.0.0.1:8000/
- [ ] Consegue fazer login
- [ ] Página do catálogo carrega
- [ ] Admin em http://127.0.0.1:8000/admin/ funciona
- [ ] Pode adicionar produtos ao carrinho
- [ ] Sidebar aparece no carrinho
- [ ] Foto de perfil pode ser enviada
- [ ] Página de pagamento carrega
- [ ] Stripe conectado (se configurado)

---

**Pronto! 🎉 Sistema funcionando.**

Se houver dúvidas, consulte a documentação completa em `DOCUMENTACAO_TECNICA.md`
