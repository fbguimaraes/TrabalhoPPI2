# 🚀 Guia de Deployment - Produção

## 📍 Índice

1. [Pré-Requisitos](#pré-requisitos)
2. [Configuração de Produção](#configuração-de-produção)
3. [Database](#database)
4. [Servidor Web](#servidor-web)
5. [HTTPS e Segurança](#https-e-segurança)
6. [Monitoramento](#monitoramento)
7. [Troubleshooting](#troubleshooting)

---

## 🔍 Pré-Requisitos

### Sistema Operacional
- Linux (Ubuntu 20.04+, Debian 10+) - **Recomendado**
- macOS (Big Sur+)
- Windows Server 2019+

### Dependências do Sistema
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3.10 python3-pip python3-venv
sudo apt-get install postgresql postgresql-contrib
sudo apt-get install redis-server
sudo apt-get install nginx
sudo apt-get install certbot python3-certbot-nginx
```

### Versões Mínimas
- Python 3.10+
- PostgreSQL 12+
- Redis 5+
- Nginx 1.18+

---

## ⚙️ Configuração de Produção

### 1. Clonar Repositório

```bash
# HTTPS
git clone https://seu-repo.git /var/www/ecommerce

# SSH
git clone git@seu-repo.git /var/www/ecommerce

# Entrar no diretório
cd /var/www/ecommerce
```

### 2. Criar Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
pip install gunicorn    # Servidor WSGI
pip install whitenoise  # Static files
pip install psycopg2-binary  # PostgreSQL
```

### 4. Configurar .env Produção

```env
# Django
SECRET_KEY=gera-uma-chave-secreta-aleatoria-aqui
DEBUG=False
ALLOWED_HOSTS=seudominio.com,www.seudominio.com

# Database PostgreSQL
DATABASE_URL=postgresql://usuario:senha@localhost:5432/ecommerce_db

# Stripe
STRIPE_SECRET_KEY=sk_live_sua_chave_produca
STRIPE_PUBLISHABLE_KEY=pk_live_sua_chave_publica
STRIPE_API_VERSION=2024-11-20
STRIPE_WEBHOOK_SECRET=whsec_sua_secret_webhook

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=seu-email@gmail.com

# Redis
REDIS_URL=redis://localhost:6379/0

# Segurança
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_SECURITY_POLICY={
    "default-src": ("'self'",),
    "script-src": ("'self'", "cdn.jsdelivr.net"),
    "style-src": ("'self'", "cdn.jsdelivr.net", "'unsafe-inline'"),
    "img-src": ("'self'", "data:", "https:"),
}
```

### 5. Gerar SECRET_KEY Segura

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### 6. Atualizar settings.py

```python
# settings.py

from decouple import config
import os

# Security
DEBUG = config('DEBUG', default=False, cast=bool)
SECRET_KEY = config('SECRET_KEY')
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

# Database
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=600
    )
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Whitenoise
if not DEBUG:
    MIDDLEWARE = [
        'whitenoise.middleware.WhiteNoiseMiddleware',
    ] + MIDDLEWARE

# HTTPS/Security
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'

# Stripe
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = config('STRIPE_PUBLISHABLE_KEY')
STRIPE_API_VERSION = config('STRIPE_API_VERSION', '2024-11-20')
STRIPE_WEBHOOK_SECRET = config('STRIPE_WEBHOOK_SECRET', '')

# Email
EMAIL_BACKEND = config('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', 'localhost')
EMAIL_PORT = config('EMAIL_PORT', 25, cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', False, cast=bool)
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', 'noreply@ecommerce.com')

# Redis
REDIS_URL = config('REDIS_URL', 'redis://localhost:6379/0')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/django/django.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
```

### 7. Migrations e Dados

```bash
# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Aplicar migrations
python manage.py migrate

# Criar super usuário
python manage.py createsuperuser

# Carregar dados de exemplo (se houver)
# python manage.py loaddata fixtures.json
```

---

## 🗄️ Database

### PostgreSQL Setup

```bash
# Criar usuário
sudo -u postgres psql
CREATE USER ecommerce_user WITH PASSWORD 'sua-senha-forte-aqui';
ALTER ROLE ecommerce_user SET client_encoding TO 'utf8';
ALTER ROLE ecommerce_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE ecommerce_user SET default_transaction_deferrable TO on;
ALTER ROLE ecommerce_user SET timezone TO 'UTC';

# Criar database
CREATE DATABASE ecommerce_db;

# Dar permissões
GRANT ALL PRIVILEGES ON DATABASE ecommerce_db TO ecommerce_user;

# Sair
\q
```

### Backup Automático

```bash
# Criar script de backup
sudo nano /home/backup_db.sh

#!/bin/bash
BACKUP_DIR="/backups/database"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
pg_dump -U ecommerce_user ecommerce_db | gzip > $BACKUP_DIR/ecommerce_db_$TIMESTAMP.sql.gz

# Fazer executável
sudo chmod +x /home/backup_db.sh

# Agendar backup diário (crontab)
sudo crontab -e

# Adicionar linha:
0 2 * * * /home/backup_db.sh
```

---

## 🔧 Servidor Web

### Gunicorn Setup

```bash
# Criar arquivo de configuração
sudo nano /etc/gunicorn.d/ecommerce.conf.py

import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
max_requests = 1000
timeout = 30
keepalive = 5
```

### Nginx Configuration

```nginx
# /etc/nginx/sites-available/ecommerce

upstream ecommerce_app {
    server 127.0.0.1:8000;
}

# Redirect HTTP para HTTPS
server {
    listen 80;
    server_name seudominio.com www.seudominio.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS
server {
    listen 443 ssl http2;
    server_name seudominio.com www.seudominio.com;

    # SSL
    ssl_certificate /etc/letsencrypt/live/seudominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seudominio.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Logging
    access_log /var/log/nginx/ecommerce_access.log;
    error_log /var/log/nginx/ecommerce_error.log;

    # Tamanho máximo de upload
    client_max_body_size 50M;

    # Static files
    location /static/ {
        alias /var/www/ecommerce/staticfiles/;
        expires 365d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /var/www/ecommerce/media/;
        expires 7d;
        add_header Cache-Control "public";
    }

    # Proxy para Gunicorn
    location / {
        proxy_pass http://ecommerce_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

### Systemd Service

```bash
# /etc/systemd/system/ecommerce.service

[Unit]
Description=E-commerce Django Application
After=network.target postgres.service redis.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/ecommerce
Environment="PATH=/var/www/ecommerce/venv/bin"

ExecStart=/var/www/ecommerce/venv/bin/gunicorn \
    --workers 4 \
    --worker-class sync \
    --bind 127.0.0.1:8000 \
    --timeout 30 \
    setup.wsgi:application

ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed

[Install]
WantedBy=multi-user.target
```

### Ativar Serviço

```bash
# Habilitar na inicialização
sudo systemctl enable ecommerce

# Iniciar
sudo systemctl start ecommerce

# Status
sudo systemctl status ecommerce

# Logs
sudo journalctl -u ecommerce -f
```

---

## 🔐 HTTPS e Segurança

### Let's Encrypt (SSL Gratuito)

```bash
# Instalar Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obter certificado
sudo certbot certonly --nginx -d seudominio.com -d www.seudominio.com

# Renovação automática (já vem configurada)
sudo systemctl start certbot.timer
sudo systemctl enable certbot.timer
```

### Segurança do Servidor

```bash
# Firewall (UFW)
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS

# SSH (desabilitar root)
sudo nano /etc/ssh/sshd_config

PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes

sudo systemctl restart ssh

# Fail2Ban
sudo apt-get install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## 📊 Monitoramento

### Logs

```bash
# Django
sudo tail -f /var/log/django/django.log

# Nginx
sudo tail -f /var/log/nginx/ecommerce_access.log
sudo tail -f /var/log/nginx/ecommerce_error.log

# Sistema
sudo journalctl -u ecommerce -f
```

### Uptime Monitoring

```bash
# Instalar Uptime Robot gratuito
# https://uptimerobot.com

# Configure para monitorar:
# https://seudominio.com/
# https://seudominio.com/admin/
# https://seudominio.com/payment/methods/
```

### Health Check

```python
# views.py - Adicionar
from django.http import JsonResponse
from django.db import connection

def health_check(request):
    try:
        # Testa DB
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse({
            'status': 'ok',
            'database': 'connected'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=500)

# urls.py
path('health/', health_check, name='health_check'),
```

### Monitoramento de Performance

```bash
# New Relic (gratuito)
pip install newrelic

# Instruir aplicação
NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program \
  gunicorn --workers 4 setup.wsgi:application
```

---

## 🐛 Troubleshooting

### Problema: 502 Bad Gateway

```bash
# Verificar se Gunicorn está rodando
sudo systemctl status ecommerce

# Reiniciar
sudo systemctl restart ecommerce

# Ver logs
sudo journalctl -u ecommerce -n 50
```

### Problema: Database Connection Error

```bash
# Testar conexão
psql -U ecommerce_user -d ecommerce_db -c "SELECT 1"

# Verificar DATABASE_URL em .env
cat .env | grep DATABASE_URL

# Recriar migrations
python manage.py migrate --verbosity 3
```

### Problema: Static Files Não Carregam

```bash
# Recoletar
python manage.py collectstatic --noinput --clear

# Verificar permissões
sudo chown -R www-data:www-data /var/www/ecommerce/staticfiles/
sudo chmod -R 755 /var/www/ecommerce/staticfiles/
```

### Problema: Memory Leak

```bash
# Monitorar uso de memória
free -h
ps aux | grep gunicorn

# Limitar workers
# Em /etc/systemd/system/ecommerce.service
ExecStart=/var/www/ecommerce/venv/bin/gunicorn \
    --workers 2 \
    --max-requests 1000
```

### Problema: Stripe Webhook Falha

```bash
# Verificar STRIPE_WEBHOOK_SECRET em .env
echo $STRIPE_WEBHOOK_SECRET

# Testar endpoint
curl -X POST https://seudominio.com/payment/webhook/ \
  -H "stripe-signature: test"

# Ver logs de erro
sudo tail -f /var/log/django/django.log | grep webhook
```

---

## 📋 Checklist de Deployment

### Pré-Deployment
- [ ] SECRET_KEY alterada
- [ ] DEBUG=False
- [ ] DATABASE_URL configurado
- [ ] ALLOWED_HOSTS correto
- [ ] Stripe keys de produção
- [ ] Email configurado
- [ ] HTTPS/SSL configurado
- [ ] Backup do banco criado

### Pós-Deployment
- [ ] Migrations aplicadas
- [ ] Super usuário criado
- [ ] Static files coletados
- [ ] Logs funcionando
- [ ] Health check respondendo
- [ ] Admin acessível
- [ ] Pagamentos testados
- [ ] Email funcionando
- [ ] Uptime monitoring ativo
- [ ] Backup automático funcionando

---

## 📞 Contato de Suporte

Se encontrar problemas em produção:

1. **Verificar logs:**
   ```bash
   sudo tail -f /var/log/django/django.log
   sudo tail -f /var/log/nginx/ecommerce_error.log
   ```

2. **Reiniciar serviço:**
   ```bash
   sudo systemctl restart ecommerce
   sudo systemctl restart nginx
   ```

3. **Testar manualmente:**
   ```bash
   python manage.py shell
   >>> from django.db import connection
   >>> connection.ensure_connection()
   ```

---

**Data:** 2025-12-09  
**Versão:** 1.0  
**Mantidor:** Sistema de E-commerce PPI2
