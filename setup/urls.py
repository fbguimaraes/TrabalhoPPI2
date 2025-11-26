"""
URL configuration for setup project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from app import views


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Autenticação
    path('', views.login_usuario, name='login_usuario'),
    path('logout/', views.logout_usuario, name='logout_usuario'),
    path('cadastro/', views.cadastro_usuario, name='cadastro_usuario'),
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
    
    # Usuários
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    
    # Produtos
    path('catalogo/', views.catalogo_produtos, name='catalogo_produtos'),
    path('produto/<int:produto_id>/', views.detalhe_produto, name='detalhe_produto'),
    
    # Carrinho
    path('carrinho/', views.ver_carrinho, name='ver_carrinho'),
    path('carrinho/adicionar/<int:produto_id>/', views.adicionar_carrinho, name='adicionar_carrinho'),
    path('carrinho/atualizar/<int:item_id>/', views.atualizar_item_carrinho, name='atualizar_item_carrinho'),
    path('carrinho/remover/<int:item_id>/', views.remover_item_carrinho, name='remover_item_carrinho'),
    path('carrinho/limpar/', views.limpar_carrinho, name='limpar_carrinho'),
]

# Servir arquivos de mídia durante desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)