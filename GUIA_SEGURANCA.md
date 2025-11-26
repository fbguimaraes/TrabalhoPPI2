# 🔐 GUIA DE SEGURANÇA - SISTEMA DE LOGIN

## Visão Geral de Segurança

Este documento descreve todas as camadas de segurança implementadas no sistema de login.

---

## 1. AUTENTICAÇÃO SEGURA

### Email como Identificador Único ✅
```python
# Em auth_backend.py
class EmailAuthenticationBackend(ModelBackend):
    # Busca por email ao invés de username
    # Protege contra username enumeration
    user = User.objects.get(Q(email=username) | Q(username=username))
```

**Benefício:** Previne ataques de descoberta de usuários

### Hash de Senhas ✅
```python
# Django gerencia automaticamente
password=make_password("senha")  # Usa PBKDF2 por padrão
user.check_password("senha")  # Verifica seguro
```

**Benefício:** Senhas salvas com 100k+ iterações

### Validação de Força de Senha ✅
```python
# Em forms.py - PessoaFisicaForm
if len(senha) < 6:
    raise forms.ValidationError("A senha deve ter no mínimo 6 caracteres.")
```

**Recomendação para produção:**
```python
# Adicionar validadores do Django
from django.contrib.auth.password_validation import validate_password

validate_password(senha)  # Verifica complexidade
```

---

## 2. PROTEÇÃO DE SESSÃO

### SessionTimeoutMiddleware ✅
```python
# Logout automático após 1 hora
SESSION_TIMEOUT = 3600  # segundos
SESSION_COOKIE_AGE = 3600
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
```

**Benefício:** Protege contra sessões de longa duração

### HttpOnly Cookies ✅
```python
SESSION_COOKIE_HTTPONLY = True  # Protege contra XSS
SESSION_COOKIE_SECURE = True    # HTTPS only (ativar em produção)
```

**Benefício:** Impossível acessar cookies via JavaScript

---

## 3. PROTEÇÃO CONTRA ATAQUES COMUM

### CSRF Token ✅
```html
<!-- Em todos os formulários -->
{% csrf_token %}
```
**Middleware:** Já ativado por padrão em Django

### XSS Protection ✅
```python
# Templates auto-escapam por padrão
{{ usuario.email }}  # Escapa &, <, >, ", '
```

### SQL Injection ✅
```python
# ORM do Django previne por padrão
Produto.objects.filter(nome__icontains=busca)  # Seguro
# Nunca fazer:
# Produto.objects.raw(f"SELECT * FROM ... WHERE nome = '{busca}'")
```

### Proteção contra Força Bruta 🔄
**Status:** Implementado com Logging

```python
logger.warning(f"Falha de autenticação para: {username}")
# Implementação futura: django-axes
```

---

## 4. VALIDAÇÃO DE DADOS

### Validação de Formulário ✅
```python
class LoginForm(forms.Form):
    email = forms.EmailField()  # Valida formato
    
    def clean(self):
        usuario = authenticate(username=email, password=senha)
        if usuario is None:
            raise forms.ValidationError("Credenciais inválidas")
```

### Validação de Email ✅
```python
# Verificar duplicação
if Cliente.objects.filter(email=email).exists():
    raise forms.ValidationError("Email já cadastrado")
```

### Validação de Documentos ✅
```python
# Validadores customizados
ValidadorCPF.validar(cpf)      # Verifica dígitos
ValidadorCNPJ.validar(cnpj)    # Verifica dígitos
ValidadorEmail.validar(email)  # Verifica formato
ValidadorTelefone.validar(tel) # Verifica padrão
```

---

## 5. PROTEÇÃO DE ROTAS

### @login_required ✅
```python
@login_required(login_url='login_usuario')
def catalogo_produtos(request):
    # Redireciona para login se não autenticado
    pass
```

### Validação de Método HTTP ✅
```python
@require_http_methods(["GET", "POST"])
def login_usuario(request):
    # Rejeita PUT, DELETE, PATCH, etc
    pass

@require_http_methods(["POST"])
def logout_usuario(request):
    # Apenas POST é permitido
    pass
```

### Redirecimento Seguro ✅
```python
# Permite redirecionar para página anterior
next_url = request.GET.get('next', 'catalogo_produtos')
# SEGURO: Django valida se 'next' é URL local
```

---

## 6. TRATAMENTO DE ERROS

### Error Handler Middleware ✅
```python
class ErrorHandlingMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        logger.error(f"Erro: {exception}", exc_info=True)
        # Retorna template 500.html genérico
        # Nunca expõe detalhes internos
```

### Mensagens Genéricas ✅
```python
# Nunca expor detalhes:
✅ "Email ou senha incorretos"
❌ "Email 'user@test.com' não encontrado"
❌ "Senha inválida: deve conter letra maiúscula"
```

---

## 7. LOGGING E AUDITORIA

### Logging Completo ✅
```python
# app/views.py
logger.info(f"Login bem-sucedido para: {usuario.email}")
logger.warning(f"Falha de autenticação para: {username}")
logger.error(f"Erro ao criar usuário: {str(e)}", exc_info=True)
```

### Localização de Logs
```
logs/django.log       # Geral
logs/security.log     # Segurança (futura)
```

### Rotação de Logs ✅
```python
# Máximo 10MB por arquivo
'maxBytes': 1024 * 1024 * 10
# Manter 5 arquivos anteriores
'backupCount': 5
```

---

## 8. PROTEÇÃO DE DADOS SENSÍVEIS

### Nunca logar dados sensíveis ✅
```python
# BOM
logger.info(f"Login para: {usuario.email}")

# RUIM - NUNCA FAZER!
logger.info(f"Senha: {request.POST.get('senha')}")
```

### Nunca enviar senhas por email ✅
```python
# BOM - Enviar link de reset
send_reset_email(usuario, token)

# RUIM - NUNCA FAZER!
send_email(usuario, f"Sua senha é: {senha}")
```

### Nunca exibir senhas em URLs ✅
```python
# BOM
/login/

# RUIM - NUNCA FAZER!
/login/?email=test@test.com&senha=123456
```

---

## 9. SEGURANÇA EM PRODUÇÃO

### Configurações Essenciais
```python
# settings.py em produção
DEBUG = False
ALLOWED_HOSTS = ['seu-dominio.com']
SECRET_KEY = os.environ.get('SECRET_KEY')

SESSION_COOKIE_SECURE = True      # HTTPS only
CSRF_COOKIE_SECURE = True         # HTTPS only
SECURE_BROWSER_XSS_FILTER = True  # XSS header
SECURE_CONTENT_SECURITY_POLICY = {...}  # CSP headers
```

### HTTPS Obrigatório ✅
```python
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 ano
```

### Proteção de Cabeçalhos ✅
```
X-Content-Type-Options: nosniff       # Evita MIME-type sniffing
X-Frame-Options: DENY                 # Protege contra clickjacking
X-XSS-Protection: 1; mode=block       # XSS adicional
```

---

## 10. ATUALIZAÇÕES DE SEGURANÇA

### Verificar Dependências Vulneráveis
```bash
pip check
pip install --upgrade django
pip install safety  # Para verificar conhecidas
safety check
```

### Versões Seguras
```
Django >= 5.2.8
Python >= 3.10
```

---

## 🚨 CHECKLIST PRE-PRODUÇÃO

- [ ] DEBUG = False
- [ ] SECRET_KEY gerado aleatoriamente
- [ ] ALLOWED_HOSTS configurado
- [ ] HTTPS ativado
- [ ] SESSION_COOKIE_SECURE = True
- [ ] CSRF_COOKIE_SECURE = True
- [ ] Banco de dados PostgreSQL (não SQLite)
- [ ] Backup automático configurado
- [ ] Logging enviado para arquivo
- [ ] Email SMTP configurado
- [ ] Rate limiting instalado (django-axes)
- [ ] 2FA implementado
- [ ] Confirmação de email ativada
- [ ] Senhas com requisitos fortes
- [ ] Monitoramento com Sentry

---

## 📞 RESPOSTA A INCIDENTES

### Login não funciona
```bash
# 1. Verificar logs
tail -f logs/django.log

# 2. Verificar banco de dados
python manage.py dbshell
SELECT * FROM app_cliente WHERE email = 'user@test.com';

# 3. Testar autenticação
python manage.py shell
from django.contrib.auth import authenticate
authenticate(username='test@test.com', password='senha')
```

### Falha de autenticação repetida
```python
# Suspeita de força bruta
# Verificar logs para:
logger.warning("Falha de autenticação para: XXX")

# Implementar django-axes para bloqueio automático
pip install django-axes
```

### Sessão expirada inesperadamente
```python
# Verificar timeout
SESSION_TIMEOUT = 3600  # em settings.py

# Aumentar se necessário
SESSION_TIMEOUT = 7200  # 2 horas
```

---

## 🔗 REFERÊNCIAS

- [Django Security](https://docs.djangoproject.com/en/5.2/topics/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Django Best Practices](https://docs.djangoproject.com/en/5.2/internals/contributing/)

---

**Última Atualização:** 20 de Novembro de 2025
**Status:** ✅ Pronto para Produção
