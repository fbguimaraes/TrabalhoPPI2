# 🎨 GUIA DE ESTILO - SISTEMA DE DESIGN

## Visão Geral

Este documento descreve o sistema de design padronizado do projeto Minha Loja. Todos os templates utilizam um arquivo CSS centralizado (`app/static/css/style.css`) com variáveis CSS e componentes reutilizáveis.

---

## 📁 Estrutura de Arquivos

```
app/
├── static/
│   └── css/
│       └── style.css          ← Estilos globais centralizados
└── templates/
    ├── login.html             ← Autenticação
    ├── cadastro.html          ← Registro de usuários
    ├── catalogo_produtos.html ← Listagem de produtos
    ├── detalhe_produto.html   ← Detalhes de produtos
    ├── perfil_usuario.html    ← Perfil do usuário
    ├── list_usuarios.html     ← Listagem de usuários (admin)
    ├── index.html             ← Página inicial (antiga)
    ├── 404.html               ← Página de erro
    └── 500.html               ← Página de erro
```

---

## 🎨 PALETA DE CORES

### Cores Primárias
```css
--primary-green: #16a34a      /* Verde principal */
--primary-dark: #15803d       /* Verde escuro (hover) */
--primary-light: #4ade80      /* Verde claro (badges) */
```

### Cores Secundárias
```css
--secondary-purple: #667eea     /* Roxo (gradientes) */
--secondary-purple-dark: #764ba2 /* Roxo escuro */
```

### Cores Neutras
```css
--text-dark: #111827            /* Texto principal */
--text-muted: #6b7280           /* Texto secundário */
--text-light: #9ca3af           /* Texto leve */
--bg-light: #f8fafc             /* Fundo leve */
--bg-lighter: #f9fafb           /* Fundo mais leve */
--bg-white: #ffffff             /* Fundo branco */
--border-light: #e5e7eb         /* Bordas */
```

### Cores de Estado
```css
/* Erro */
--error-bg: #fee2e2
--error-border: #ef4444
--error-text: #991b1b

/* Sucesso */
--success-bg: #dcfce7
--success-border: #16a34a
--success-text: #166534

/* Aviso */
--warning-bg: #fef3c7
--warning-border: #f59e0b
--warning-text: #92400e

/* Informação */
--info-bg: #dbeafe
--info-border: #3b82f6
--info-text: #1e40af
```

---

## 📐 ESPAÇAMENTO

```css
--spacing-xs:  4px
--spacing-sm:  8px
--spacing-md:  12px
--spacing-lg:  16px
--spacing-xl:  24px
--spacing-2xl: 32px
--spacing-3xl: 48px
```

**Uso:**
```html
<div style="padding: var(--spacing-lg); margin-bottom: var(--spacing-xl);">
```

---

## 🔤 TIPOGRAFIA

### Família de Fonte
```css
--font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif
```

### Tamanhos
```css
--font-size-xs:  0.75rem    (12px)
--font-size-sm:  0.875rem   (14px)
--font-size-base: 1rem      (16px)
--font-size-lg:  1.125rem   (18px)
--font-size-xl:  1.25rem    (20px)
--font-size-2xl: 1.5rem     (24px)
--font-size-3xl: 1.875rem   (30px)
```

### Hierarquia

```html
<h1>Título Principal</h1>    <!-- font-size-3xl, font-weight: 700 -->
<h2>Subtítulo</h2>           <!-- font-size-2xl, font-weight: 700 -->
<h3>Seção</h3>               <!-- font-size-xl, font-weight: 700 -->
<p>Parágrafo</p>             <!-- font-size-base, line-height: 1.6 -->
```

---

## 🔘 COMPONENTES

### Botões

#### Botão Primário
```html
<button class="btn btn-primary">Enviar</button>
```
- Verde (#16a34a)
- Texto branco
- Hover: verde escuro + sombra

#### Botão Secundário
```html
<button class="btn btn-secondary">Cancelar</button>
```
- Fundo cinza (#f3f4f6)
- Texto escuro
- Hover: verde

#### Botão Perigo
```html
<button class="btn btn-danger">Deletar</button>
```
- Vermelho (#ef4444)
- Texto branco

#### Botão Outline
```html
<button class="btn btn-outline">Opção</button>
```
- Borda verde
- Fundo transparente
- Texto verde

---

### Mensagens de Feedback

#### Erro
```html
<div class="message error">
  ❌ Campo obrigatório
</div>
```

#### Sucesso
```html
<div class="message success">
  ✓ Operação concluída
</div>
```

#### Aviso
```html
<div class="message warning">
  ⚠️ Estoque baixo
</div>
```

#### Informação
```html
<div class="message info">
  ℹ️ Informação importante
</div>
```

---

### Cards/Caixas

```html
<div class="card">
  <h3>Título</h3>
  <p>Conteúdo</p>
</div>
```

Características:
- Fundo branco
- Borda arredondada (12px)
- Sombra suave
- Transição hover (elevação + sombra)

---

### Badges

```html
<span class="badge badge-success">✓ Ativo</span>
<span class="badge badge-error">❌ Erro</span>
<span class="badge badge-warning">⚠️ Aviso</span>
<span class="badge badge-info">ℹ️ Info</span>
```

---

### Formulários

#### Campo de Texto
```html
<div class="form-group">
  <label for="email" class="required">Email</label>
  <input type="email" id="email" placeholder="seu@email.com">
  <span class="form-error">Email inválido</span>
  <span class="form-help">Digite um email válido</span>
</div>
```

Estados:
- `.valid` - Borda verde + fundo verde claro
- `.invalid` - Borda vermelha + fundo vermelho claro
- `:focus` - Borda verde + sombra verde

---

### Grid de Produtos

```html
<div class="products-grid">
  <div class="product-card">
    <img class="product-image" src="...">
    <div class="product-info">
      <div class="product-category">Eletrônicos</div>
      <h3 class="product-name">Produto</h3>
      <p class="product-description">Descrição...</p>
      <div class="product-price">
        <span class="price-current">R$ 99.90</span>
        <span class="price-original">R$ 199.90</span>
      </div>
      <button class="product-button">Ver Detalhes</button>
    </div>
  </div>
</div>
```

Responsividade:
- Desktop: 4 colunas
- Tablet (1024px): 3 colunas
- Mobile (768px): 2 colunas
- Celular (480px): 1 coluna

---

### Paginação

```html
<div class="pagination">
  <a href="?page=1">«</a>
  <a href="?page=2">1</a>
  <span class="current">2</span>
  <a href="?page=3">3</a>
  <a href="?page=5">»</a>
</div>
```

---

### Tabelas

```html
<table>
  <thead>
    <tr>
      <th>Coluna</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Dados</td>
    </tr>
  </tbody>
</table>
```

Estilo:
- Cabeçalho: verde com texto branco
- Linhas alternadas com fundo cinza
- Hover: fundo mais escuro

---

## 📱 RESPONSIVIDADE

### Breakpoints

```css
/* Desktop (padrão) */
@media (max-width: 1024px) { ... }  /* Tablets */
@media (max-width: 768px) { ... }   /* Tablets pequenos */
@media (max-width: 480px) { ... }   /* Celulares */
```

### Layout Responsivo

#### Header
- Desktop: horizontal, logo + busca + nav
- Tablet: flexbox com wrap
- Mobile: vertical

#### Main Container
- Desktop: flex (sidebar + content)
- Mobile: column (sidebar acima)

#### Grid de Produtos
- Desktop: 4 colunas (minmax 280px)
- Tablet: 3 colunas (minmax 200px)
- Mobile: 1 coluna

---

## 🌊 SOMBRAS

```css
--shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.05)        /* Sutil */
--shadow-md: 0 4px 12px rgba(0, 0, 0, 0.1)        /* Médio */
--shadow-lg: 0 10px 40px rgba(0, 0, 0, 0.15)      /* Grande */
```

Uso:
- Hover de cards: `box-shadow: var(--shadow-md)`
- Cards padrão: `box-shadow: var(--shadow-sm)`
- Modais: `box-shadow: var(--shadow-lg)`

---

## ⏱️ TRANSIÇÕES

```css
--transition-fast: 0.15s ease-in-out
--transition-base: 0.3s ease-in-out
--transition-slow: 0.5s ease-in-out
```

Uso:
```css
.element {
  transition: all var(--transition-base);
}
```

---

## 🔲 RAIOS DE BORDA

```css
--rounded-sm: 6px           /* Botões */
--rounded-md: 8px           /* Formulários */
--rounded-lg: 12px          /* Cards */
--rounded-full: 9999px      /* Círculos/badges */
```

---

## 📋 CHECKLIST DE ESTILO

Ao criar/modificar um template, verificar:

- [ ] Carregado `{% load static %}`
- [ ] Link para `{% static 'css/style.css' %}`
- [ ] Usado `var(--cor-primaria)` para cores
- [ ] Usado `var(--spacing-*)` para espaçamento
- [ ] Componentes com classes padronizadas (`.btn`, `.card`, etc)
- [ ] Titles com formato correto ("Página - Minha Loja")
- [ ] Responsividade testada (480, 768, 1024px)
- [ ] Acessibilidade: labels associadas, focus states
- [ ] Sem estilos inline (exceto layouts especiais)

---

## 🔄 COMO ADICIONAR NOVOS ESTILOS

1. **Adicione à variável CSS em `style.css`:**
   ```css
   :root {
     --nova-cor: #123456;
   }
   ```

2. **Use nos templates:**
   ```html
   <div style="color: var(--nova-cor);">Texto</div>
   ```

3. **Evite estilos inline:**
   - ✅ Bom: `<div class="card">`
   - ❌ Ruim: `<div style="background: white; border-radius: 12px;">`

---

## 🎭 EXEMPLOS DE USO

### Página de Login
```html
{% load static %}
<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="{% static 'css/style.css' %}">
</head>
<body>
  <div class="login-container">
    <form>
      <div class="form-group">
        <label for="email" class="required">Email</label>
        <input type="email" id="email" required>
      </div>
      <button type="submit" class="btn btn-primary">Entrar</button>
    </form>
  </div>
</body>
</html>
```

### Página de Listagem
```html
<div class="products-grid">
  {% for item in items %}
  <div class="card">
    <h3>{{ item.nome }}</h3>
    <p>{{ item.descricao }}</p>
  </div>
  {% endfor %}
</div>
```

---

## 📞 SUPORTE

Para dúvidas sobre estilos ou adicionar novos componentes:
1. Verificar `app/static/css/style.css`
2. Consultar exemplos em templates existentes
3. Manter consistência com paleta de cores e espaçamento

---

**Versão:** 1.0  
**Data:** 20 de Novembro de 2025  
**Status:** ✅ Ativo
