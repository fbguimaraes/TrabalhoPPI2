# 📖 GUIA DE USUÁRIO - SISTEMA DE LOJA

## Índice
1. [Primeiras Passos](#primeiras-passos)
2. [Cadastro](#cadastro)
3. [Login](#login)
4. [Navegação](#navegação)
5. [Catálogo](#catálogo)
6. [Perfil](#perfil)
7. [Troubleshooting](#troubleshooting)

---

## Primeiras Passos

### Instalação e Configuração

```bash
# 1. Clonar repositório
git clone https://github.com/fbguimaraes/TrabalhoPPI2.git
cd TrabalhoPPI2

# 2. Criar ambiente virtual
python -m venv venv

# 3. Ativar ambiente
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 4. Instalar dependências
pip install -r requirements.txt

# 5. Fazer migrações
python manage.py migrate

# 6. Criar superuser (administrador)
python manage.py createsuperuser

# 7. Rodar servidor
python manage.py runserver
```

### Acessando a Aplicação

- **Home:** http://localhost:8000/
- **Admin:** http://localhost:8000/admin/
- **Catálogo:** http://localhost:8000/catalogo/

---

## Cadastro

### Passo 1: Ir para Página de Cadastro

1. Na página de login, clique em **"Criar Conta"**
2. Você será redirecionado para a página de cadastro

### Passo 2: Escolher Tipo de Registro

- **Pessoa Física:** Indivíduo, freelancer, etc
- **Pessoa Jurídica:** Empresa, CNPJ, razão social, etc

### Passo 3: Preencher Dados

#### Para Pessoa Física:
- **Nome Completo:** Seu nome completo
- **CPF:** 000.000.000-00 (11 dígitos)
- **Data de Nascimento:** Sua data de nascimento
- **RG:** (opcional)
- **Email:** seu@email.com
- **Telefone Principal:** (00) 00000-0000
- **Telefone Secundário:** (opcional)

#### Para Pessoa Jurídica:
- **CNPJ:** 00.000.000/0000-00 (14 dígitos)
- **Razão Social:** Nome oficial da empresa
- **Nome Fantasia:** Nome comercial (opcional)
- **Data de Abertura:** Quando a empresa abriu
- **Inscrição Estadual:** (opcional)
- **Email:** contato@empresa.com
- **Telefone Principal:** (00) 00000-0000
- **Telefone Secundário:** (opcional)
- **Site:** https://www.empresa.com (opcional)

#### Endereço (Ambos os tipos):
- **CEP:** 00000-000 (8 dígitos)
  - Dica: Usar [ViaCEP](https://viacep.com.br) para buscar
- **Logradouro:** Rua, Avenida, etc
- **Número:** Número do endereço
- **Complemento:** Apto, Sala, etc (opcional)
- **Bairro:** Bairro
- **Cidade:** Cidade
- **Estado:** Sigla (ex: SP, RJ)
- **País:** Padrão "Brasil"

#### Credenciais:
- **Senha:** Mínimo 6 caracteres
- **Confirmar Senha:** Repita a mesma senha

### Passo 4: Enviar Cadastro

- Clique em **"Finalizar Cadastro"**
- Se tudo estiver certo, verá mensagem de sucesso
- Será redirecionado para login

### Possíveis Erros

| Erro | Causa | Solução |
|------|-------|--------|
| CPF inválido | Dígitos verificadores errados | Verificar novamente |
| CNPJ inválido | Dígitos verificadores errados | Usar CNPJ real |
| Email já existe | Email já cadastrado | Usar outro email |
| As senhas não conferem | Senhas diferentes | Digitar senhas iguais |
| Campo obrigatório vazio | Esqueceu de preencher | Preencher todos os *obrigatórios |

---

## Login

### Fazer Login

1. Ir para http://localhost:8000/
2. Preencher **Email** (o email do cadastro)
3. Preencher **Senha**
4. Clicar em **"Entrar"**

### Lembrete de Segurança

- ✅ Use senhas fortes (letras, números, caracteres especiais)
- ✅ Nunca compartilhe sua senha
- ✅ Logout ao terminar em computadores compartilhados
- ⏱️ Sessão expira em 1 hora de inatividade

### Se Esquecer a Senha

- Atualmente não há sistema de recuperação
- Contate o administrador do site

---

## Navegação

### Menu Principal

Na barra superior você encontra:
- 🛒 **Logo "Minha Loja"** - Volta para home
- 🔍 **Busca** - Procura por produtos
- 👤 **Seu Email** - Clique para ir ao perfil
- 🚪 **Sair** - Fazer logout

### Redirecionamentos Automáticos

| Situação | Redirecionamento |
|----------|-----------------|
| Não autenticado | Tenta acessar catálogo → Login |
| Sessão expirada | Automático para login |
| Conta desativada | Erro 403 Forbidden |
| Página não existe | Erro 404 (página amigável) |

---

## Catálogo

### Navegando Produtos

1. Após login, acesse http://localhost:8000/catalogo/
2. Verá lista de todos os produtos disponíveis

### Filtros Disponíveis

#### Por Categoria
- Na barra lateral esquerda, click em uma categoria
- Mostra apenas produtos daquela categoria
- Indicador de quantidade de produtos

#### Por Busca
- Digite na caixa "Buscar produtos..."
- Busca no nome e descrição
- Resultados em tempo real

#### Combinado
- Pode filtrar por categoria E buscar
- Exemplo: Categoria "Eletrônicos" + Busca "notebook"

### Informações do Produto

Cada card mostra:
- 📷 **Imagem** do produto
- 📌 **Categoria** (cor verde)
- 📝 **Nome** do produto
- 📄 **Descrição** (primeiras linhas)
- 💰 **Preço** (destacado em verde)
- ~~Preço Original~~ se em promoção
- 📦 **Estoque** - Disponibilidade
- ⭐ **Badges**:
  - -20% (desconto)
  - ⭐ Destaque
  - Sem Estoque

### Visualizar Detalhes

- Clique em "Ver Detalhes" no produto
- Página com informações completas
- Produtos relacionados (mesma categoria)

### Estatísticas do Catálogo

Na parte superior:
- 📦 **Total de Produtos** - Todos disponíveis
- ✅ **Em Estoque** - Com quantidade > 0
- ⭐ **Em Destaque** - Marcados como destaque

---

## Perfil

### Acessar Perfil

1. Clique no seu email na barra superior (👤)
2. Ou acesse http://localhost:8000/perfil/

### Informações Exibidas

#### Seção de Identificação
- 👤 Avatar (genérico)
- 📛 Nome/Razão Social
- 📧 Email
- 🏷️ Tipo (Pessoa Física ou Jurídica)

#### Dados Pessoais (PF)
- Nome completo
- CPF
- Data de nascimento
- RG (se preenchido)

#### Dados da Empresa (PJ)
- Razão Social
- Nome Fantasia
- CNPJ
- IE (se preenchido)
- Data de abertura
- Site (se preenchido)

#### Contato
- Telefone principal
- Telefone secundário
- Email

#### Endereço
- CEP
- Logradouro
- Número
- Complemento
- Bairro
- Cidade
- Estado
- País

### Editar Perfil

Atualmente não há função de editar
- Contate o administrador para alterações
- Ou crie uma nova conta

### Logout do Perfil

- Botão **"Fazer Logout"** na parte inferior
- Ou clique **"Sair"** na barra superior

---

## Troubleshooting

### "Email ou senha incorretos"

**Causas:**
- Email digitado errado
- Senha digitada errado
- Conta ainda não cadastrada

**Solução:**
```
1. Verificar capitalização (case-sensitive)
2. Limpar campo e digitar novamente
3. Ir para cadastro se não tiver conta
```

### "Sessão expirada"

**Causas:**
- Ficou inativo por mais de 1 hora
- Logout automático por segurança

**Solução:**
- Fazer login novamente
- Será redirecionado automaticamente

### "Categoria não encontrada"

**Causas:**
- Categoria foi deletada
- URL alterada manualmente

**Solução:**
- Ir para home ("/catalogo/")
- Escolher categoria válida

### Produto não aparece nos resultados

**Causas:**
- Produto está inativo (administrador deletou)
- Sem estoque e filtro ativo
- Busca não corresponde a nenhum campo

**Solução:**
- Limpar filtros e tentar novamente
- Verificar se categoria tem produtos

### Página branca/erro 500

**Causas:**
- Erro interno do servidor
- Banco de dados desconectado
- Configuração faltando

**Solução:**
```bash
# Verificar logs
tail -f logs/django.log

# Reiniciar servidor
python manage.py runserver

# Verificar banco
python manage.py check
```

### Não consigo fazer logout

**Causas:**
- Botão não clicável
- JavaScript desativado

**Solução:**
```
1. Fechar e reabrir navegador
2. Acessar http://localhost:8000/logout/
3. Cookies podem precisar limpar (F12 -> Aplicação -> Cookies)
```

---

## 💡 Dicas Úteis

### Busca Avançada
- Busca por parte do nome: "inver" encontra "Inversor"
- Busca por descrição também funciona
- Não é case-sensitive

### Performance
- Cada categoria carrega rapidamente (cache)
- Produtos paginados para melhor performance
- Primeira carga pode demorar um pouco

### Segurança
- Suas informações são criptografadas
- Cookies marcados como HttpOnly
- Sensível ao IP (mudança de IP requer re-login em produção)

### Acessibilidade
- Tecla TAB para navegar entre campos
- ENTER para submeter formulários
- Mobile-friendly para celulares

---

## ❓ FAQ

**P: Quantos produtos por página?**
R: Todos os produtos são carregados, mas paginados em 25 usuários (admin)

**P: Posso ter múltiplas contas?**
R: Sim, um email por conta

**P: Como funciona o cache?**
R: Categorias são cacheadas por 1 hora para performance

**P: É seguro usar meu email real?**
R: Sim, seu email é criptografado e protegido

**P: Posso deletar minha conta?**
R: Não, contate o administrador

---

**Versão:** 2.0
**Data:** 20 de Novembro de 2025
**Status:** ✅ Funcional
