import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Prefetch
from django.core.cache import cache
from django.views.decorators.http import require_http_methods
from django.http import Http404

from .models import Cliente, PessoaFisica, PessoaJuridica, Categoria, Produto, Carrinho, ItemCarrinho
from .forms import LoginForm, PessoaFisicaForm, PessoaJuridicaForm, EnderecoForm

logger = logging.getLogger(__name__)


# ==========================
# AUTENTICAÇÃO
# ==========================

@require_http_methods(["GET", "POST"])
def login_usuario(request):
    """
    View de login seguro com validação de formulário.
    
    GET: Exibe formulário de login
    POST: Autentica usuário
    
    Redireciona para catálogo se já autenticado.
    """
    # Se já está autenticado, redireciona
    if request.user.is_authenticated:
        logger.info(f"Usuário {request.user.email} já estava autenticado, redirecionando")
        return redirect("catalogo_produtos")
    
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            usuario = form.cleaned_data.get('usuario')
            if usuario:
                login(request, usuario)
                logger.info(f"Login bem-sucedido para: {usuario.email}")
                messages.success(request, f"Bem-vindo de volta, {usuario.email}!")
                
                # Redirecionar para página anterior se existir
                next_url = request.GET.get('next', 'catalogo_produtos')
                return redirect(next_url)
        else:
            logger.warning(f"Tentativa de login falhada para email: {request.POST.get('email')}")
            messages.error(request, "Email ou senha incorretos.")
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})


@require_http_methods(["POST"])
@login_required(login_url='login_usuario')
def logout_usuario(request):
    """
    View para fazer logout seguro.
    Limpa a sessão e redireciona para login.
    """
    email = request.user.email
    logout(request)
    logger.info(f"Logout realizado para: {email}")
    messages.success(request, "Logout realizado com sucesso!")
    return redirect("login_usuario")


@login_required(login_url='login_usuario')
def perfil_usuario(request):
    """
    View para exibir perfil do usuário autenticado.
    
    Busca dados adicionais (PF ou PJ) se existirem.
    """
    usuario = request.user
    dados_adicionais = None
    
    try:
        if usuario.tipo_cliente == 'pf':
            dados_adicionais = usuario.pf
        elif usuario.tipo_cliente == 'pj':
            dados_adicionais = usuario.pj
    except (PessoaFisica.DoesNotExist, PessoaJuridica.DoesNotExist):
        logger.warning(f"Dados de {usuario.tipo_cliente} não encontrados para user ID: {usuario.id}")
    
    context = {
        'usuario': usuario,
        'dados_adicionais': dados_adicionais,
        'tipo_cliente': usuario.tipo_cliente,
    }
    
    return render(request, 'perfil_usuario.html', context)


# ==========================
# CADASTRO DE USUÁRIOS
# ==========================

@require_http_methods(["GET", "POST"])
def cadastro_usuario(request):
    """
    View para cadastro de novo usuário (PF ou PJ).
    
    GET: Exibe formulário de escolha entre PF/PJ
    POST: Processa cadastro com validação de formulário
    """
    tipo = request.GET.get('tipo', request.POST.get('tipo', '')).lower()
    
    if request.method == "POST":
        try:
            if tipo == 'pf':
                return _cadastro_pessoa_fisica(request)
            elif tipo == 'pj':
                return _cadastro_pessoa_juridica(request)
            else:
                messages.error(request, "Tipo de cliente inválido.")
                logger.warning(f"Tentativa de cadastro com tipo inválido: {tipo}")
                return render(request, 'cadastro.html')
        except Exception as e:
            logger.error(f"Erro ao cadastrar usuário: {str(e)}", exc_info=True)
            messages.error(request, "Erro ao realizar cadastro. Tente novamente.")
            return render(request, 'cadastro.html', {'tipo_selecionado': tipo})
    
    return render(request, 'cadastro.html')


def _cadastro_pessoa_fisica(request):
    """Processa cadastro de Pessoa Física"""
    # Parse de endereço
    endereco_form = EnderecoForm(request.POST)
    form = PessoaFisicaForm(request.POST)
    senha = request.POST.get('senha')
    confirmar_senha = request.POST.get('confirmar_senha')
    
    # Validar senhas
    if senha != confirmar_senha:
        form.add_error(None, "As senhas não conferem.")
    elif len(senha) < 6:
        form.add_error(None, "A senha deve ter no mínimo 6 caracteres.")
    
    if form.is_valid() and endereco_form.is_valid():
        try:
            # Criar usuário
            email = form.cleaned_data['email']
            cliente = Cliente.objects.create_user(
                username=email,
                email=email,
                password=senha,
                tipo_cliente='pf'
            )
            
            # Criar pessoa física
            pf_data = form.cleaned_data
            endereco_data = endereco_form.cleaned_data
            
            PessoaFisica.objects.create(
                cliente=cliente,
                nome=pf_data['nome'],
                cpf=pf_data['cpf'],
                data_nascimento=pf_data['data_nascimento'],
                rg=pf_data.get('rg', ''),
                email=pf_data['email'],
                telefone_principal=pf_data['telefone_principal'],
                telefone_secundario=pf_data.get('telefone_secundario', ''),
                cep=endereco_data['cep'],
                logradouro=endereco_data['logradouro'],
                numero=endereco_data['numero'],
                complemento=endereco_data.get('complemento', ''),
                bairro=endereco_data['bairro'],
                cidade=endereco_data['cidade'],
                estado=endereco_data['estado'],
                pais=endereco_data['pais'],
            )
            
            logger.info(f"Novo cadastro PF: {email}")
            messages.success(request, "Cadastro realizado com sucesso! Faça login para continuar.")
            return redirect('login_usuario')
            
        except Exception as e:
            logger.error(f"Erro ao criar PF: {str(e)}", exc_info=True)
            messages.error(request, f"Erro ao cadastrar: {str(e)}")
            return render(request, 'cadastro.html', {
                'form': form,
                'endereco_form': endereco_form,
                'tipo_selecionado': 'pf'
            })
    else:
        # Retornar com erros
        if not form.is_valid() or not endereco_form.is_valid():
            logger.warning(f"Erros de validação em cadastro PF: {form.errors} / {endereco_form.errors}")
        
        return render(request, 'cadastro.html', {
            'form': form,
            'endereco_form': endereco_form,
            'tipo_selecionado': 'pf'
        })


def _cadastro_pessoa_juridica(request):
    """Processa cadastro de Pessoa Jurídica"""
    endereco_form = EnderecoForm(request.POST)
    form = PessoaJuridicaForm(request.POST)
    senha = request.POST.get('senha')
    confirmar_senha = request.POST.get('confirmar_senha')
    
    # Validar senhas
    if senha != confirmar_senha:
        form.add_error(None, "As senhas não conferem.")
    elif len(senha) < 6:
        form.add_error(None, "A senha deve ter no mínimo 6 caracteres.")
    
    if form.is_valid() and endereco_form.is_valid():
        try:
            # Criar usuário
            email = form.cleaned_data['email']
            cliente = Cliente.objects.create_user(
                username=email,
                email=email,
                password=senha,
                tipo_cliente='pj'
            )
            
            # Criar pessoa jurídica
            pj_data = form.cleaned_data
            endereco_data = endereco_form.cleaned_data
            
            PessoaJuridica.objects.create(
                cliente=cliente,
                cnpj=pj_data['cnpj'],
                razao_social=pj_data['razao_social'],
                nome_fantasia=pj_data.get('nome_fantasia', ''),
                data_abertura=pj_data['data_abertura'],
                inscricao_estadual=pj_data.get('inscricao_estadual', ''),
                email=pj_data['email'],
                telefone_principal=pj_data['telefone_principal'],
                telefone_secundario=pj_data.get('telefone_secundario', ''),
                site=pj_data.get('site', ''),
                cep=endereco_data['cep'],
                logradouro=endereco_data['logradouro'],
                numero=endereco_data['numero'],
                complemento=endereco_data.get('complemento', ''),
                bairro=endereco_data['bairro'],
                cidade=endereco_data['cidade'],
                estado=endereco_data['estado'],
                pais=endereco_data['pais'],
            )
            
            logger.info(f"Novo cadastro PJ: {email}")
            messages.success(request, "Cadastro realizado com sucesso! Faça login para continuar.")
            return redirect('login_usuario')
            
        except Exception as e:
            logger.error(f"Erro ao criar PJ: {str(e)}", exc_info=True)
            messages.error(request, f"Erro ao cadastrar: {str(e)}")
            return render(request, 'cadastro.html', {
                'form': form,
                'endereco_form': endereco_form,
                'tipo_selecionado': 'pj'
            })
    else:
        if not form.is_valid() or not endereco_form.is_valid():
            logger.warning(f"Erros de validação em cadastro PJ: {form.errors} / {endereco_form.errors}")
        
        return render(request, 'cadastro.html', {
            'form': form,
            'endereco_form': endereco_form,
            'tipo_selecionado': 'pj'
        })


# ==========================
# PRODUTOS E CATÁLOGO
# ==========================

@login_required(login_url='login_usuario')
def catalogo_produtos(request):
    """
    View do catálogo de produtos com filtros e busca.
    
    Filtros:
        - categoria (ID)
        - busca (texto)
    
    Usa cache e otimização de queries.
    """
    categoria_id = request.GET.get('categoria')
    busca = request.GET.get('busca', '').strip()
    
    # Cache de categorias
    cache_key = 'categorias_ativas'
    categorias = cache.get(cache_key)
    if not categorias:
        categorias = Categoria.objects.filter(ativa=True).prefetch_related('produtos').order_by('ordem', 'nome')
        cache.set(cache_key, categorias, 3600)  # Cache por 1 hora
    
    # Query de produtos com otimização
    produtos = Produto.objects.filter(ativo=True).select_related('categoria')
    
    categoria_selecionada = None
    if categoria_id:
        try:
            categoria_selecionada = Categoria.objects.get(id=categoria_id, ativa=True)
            produtos = produtos.filter(categoria=categoria_selecionada)
        except Categoria.DoesNotExist:
            raise Http404("Categoria não encontrada.")
    
    # Busca
    if busca:
        produtos = produtos.filter(
            Q(nome__icontains=busca) | 
            Q(descricao__icontains=busca)
        )
    
    # Ordenação
    produtos = produtos.order_by('-em_destaque', '-criado_em')
    
    # Estatísticas
    total_produtos = produtos.count()
    produtos_em_estoque = produtos.filter(estoque__gt=0).count()
    produtos_destaque = produtos.filter(em_destaque=True).count()
    
    # Enriquecer categorias
    for cat in categorias:
        cat.total_ativos = cat.produtos.filter(ativo=True).count()
        cat.em_estoque = cat.produtos.filter(ativo=True, estoque__gt=0).count()
    
    context = {
        'categorias': categorias,
        'produtos': produtos,
        'categoria_selecionada': categoria_selecionada,
        'busca': busca,
        'total_produtos': total_produtos,
        'produtos_em_estoque': produtos_em_estoque,
        'produtos_destaque': produtos_destaque,
    }
    
    return render(request, 'catalogo_produtos.html', context)


@login_required(login_url='login_usuario')
def detalhe_produto(request, produto_id):
    """
    Exibe detalhes de um produto específico.
    
    Mostra também produtos relacionados da mesma categoria.
    """
    produto = get_object_or_404(Produto, id=produto_id, ativo=True)
    
    # Produtos relacionados
    produtos_relacionados = Produto.objects.filter(
        categoria=produto.categoria,
        ativo=True
    ).exclude(id=produto.id).order_by('-em_destaque', '-criado_em')[:4]
    
    context = {
        'produto': produto,
        'produtos_relacionados': produtos_relacionados,
    }
    
    return render(request, 'detalhe_produto.html', context)


# ==========================
# ADMINISTRAÇÃO DE USUÁRIOS
# ==========================

@login_required(login_url='login_usuario')
def lista_usuarios(request):
    """
    Lista todos os usuários cadastrados (PF e PJ).
    
    Filtro: tipo (todos, pf, pj)
    Paginação: 25 por página
    """
    tipo_filtro = request.GET.get('tipo', 'todos')
    pagina = request.GET.get('page', 1)
    
    # Query otimizada com select_related
    usuarios_pf = PessoaFisica.objects.select_related('cliente').filter(
        cliente__is_active=True
    ).order_by('-cliente__date_joined')
    
    usuarios_pj = PessoaJuridica.objects.select_related('cliente').filter(
        cliente__is_active=True
    ).order_by('-cliente__date_joined')
    
    # Montar lista combinada
    usuarios = []
    
    if tipo_filtro in ['todos', 'pf']:
        for pf in usuarios_pf:
            usuarios.append({
                'tipo': 'Pessoa Física',
                'documento': pf.cpf,
                'nome': pf.nome,
                'email': pf.email,
                'telefone': pf.telefone_principal,
                'cidade': pf.cidade,
                'estado': pf.estado,
                'pais': pf.pais,
            })
    
    if tipo_filtro in ['todos', 'pj']:
        for pj in usuarios_pj:
            usuarios.append({
                'tipo': 'Pessoa Jurídica',
                'documento': pj.cnpj,
                'nome': pj.razao_social,
                'nome_fantasia': pj.nome_fantasia or '-',
                'email': pj.email,
                'telefone': pj.telefone_principal,
                'cidade': pj.cidade,
                'estado': pj.estado,
                'pais': pj.pais,
            })
    
    # Paginação
    paginator = Paginator(usuarios, 25)  # 25 usuários por página
    
    try:
        usuarios_pagina = paginator.page(pagina)
    except PageNotAnInteger:
        usuarios_pagina = paginator.page(1)
    except EmptyPage:
        usuarios_pagina = paginator.page(paginator.num_pages)
    
    context = {
        'usuarios': usuarios_pagina,
        'tipo_filtro': tipo_filtro,
        'total_usuarios': len(usuarios),
    }
    
    return render(request, 'list_usuarios.html', context)


# ==========================
# CARRINHO DE COMPRAS
# ==========================

@login_required(login_url='login_usuario')
@require_http_methods(["POST"])
def adicionar_carrinho(request, produto_id):
    """Adiciona um produto ao carrinho"""
    produto = get_object_or_404(Produto, id=produto_id, ativo=True)
    
    # Validar estoque
    if not produto.tem_estoque():
        messages.error(request, f"Produto '{produto.nome}' indisponível no momento.")
        return redirect('catalogo_produtos')
    
    try:
        # Obter ou criar carrinho
        carrinho, created = Carrinho.objects.get_or_create(cliente=request.user)
        
        # Obter quantidade do request
        quantidade = int(request.POST.get('quantidade', 1))
        
        # Validar quantidade
        if quantidade < 1:
            messages.error(request, "Quantidade inválida.")
            return redirect('detalhe_produto', produto_id=produto_id)
        
        if quantidade > produto.estoque:
            messages.warning(request, f"Quantidade solicitada indisponível. Estoque: {produto.estoque}")
            quantidade = produto.estoque
        
        # Obter ou criar item no carrinho
        item, item_created = ItemCarrinho.objects.get_or_create(
            carrinho=carrinho,
            produto=produto,
            defaults={'preco_unitario': produto.preco_final(), 'quantidade': quantidade}
        )
        
        # Se o item já existia, atualizar quantidade
        if not item_created:
            nova_quantidade = item.quantidade + quantidade
            if nova_quantidade > produto.estoque:
                messages.warning(request, f"Quantidade máxima disponível: {produto.estoque}")
                nova_quantidade = produto.estoque
            item.quantidade = nova_quantidade
            item.save()
            logger.info(f"Item {produto.id} atualizado no carrinho do usuário {request.user.email}")
        else:
            logger.info(f"Produto {produto.id} adicionado ao carrinho do usuário {request.user.email}")
        
        messages.success(request, f"'{produto.nome}' adicionado ao carrinho! ({item.quantidade}x)")
        
    except ValueError:
        messages.error(request, "Quantidade deve ser um número válido.")
    except Exception as e:
        logger.error(f"Erro ao adicionar produto ao carrinho: {str(e)}")
        messages.error(request, "Erro ao adicionar produto ao carrinho.")
    
    # Redirecionar para a página anterior (produto ou catálogo)
    next_url = request.POST.get('next', 'catalogo_produtos')
    return redirect(next_url)


@login_required(login_url='login_usuario')
def ver_carrinho(request):
    """Exibe o carrinho de compras do usuário"""
    try:
        carrinho = Carrinho.objects.get(cliente=request.user)
        itens = carrinho.itens.select_related('produto').all()
    except Carrinho.DoesNotExist:
        carrinho = None
        itens = []
    
    context = {
        'carrinho': carrinho,
        'itens': itens,
        'total_itens': sum(item.quantidade for item in itens),
        'total_preco': sum(item.subtotal() for item in itens),
    }
    
    return render(request, 'carrinho.html', context)


@login_required(login_url='login_usuario')
@require_http_methods(["POST"])
def atualizar_item_carrinho(request, item_id):
    """Atualiza a quantidade de um item no carrinho"""
    item = get_object_or_404(ItemCarrinho, id=item_id, carrinho__cliente=request.user)
    
    try:
        nova_quantidade = int(request.POST.get('quantidade', item.quantidade))
        
        if nova_quantidade <= 0:
            # Remover item
            produto_nome = item.produto.nome
            item.delete()
            messages.success(request, f"'{produto_nome}' removido do carrinho.")
            logger.info(f"Item {item.id} removido do carrinho do usuário {request.user.email}")
        elif nova_quantidade > item.produto.estoque:
            messages.error(request, f"Quantidade máxima: {item.produto.estoque}")
        else:
            item.quantidade = nova_quantidade
            item.save()
            messages.success(request, f"Quantidade atualizada para {nova_quantidade}.")
            logger.info(f"Item {item.id} atualizado no carrinho do usuário {request.user.email}")
    
    except ValueError:
        messages.error(request, "Quantidade deve ser um número válido.")
    except Exception as e:
        logger.error(f"Erro ao atualizar item: {str(e)}")
        messages.error(request, "Erro ao atualizar item.")
    
    return redirect('ver_carrinho')


@login_required(login_url='login_usuario')
@require_http_methods(["POST"])
def remover_item_carrinho(request, item_id):
    """Remove um item do carrinho"""
    item = get_object_or_404(ItemCarrinho, id=item_id, carrinho__cliente=request.user)
    
    try:
        produto_nome = item.produto.nome
        item.delete()
        messages.success(request, f"'{produto_nome}' removido do carrinho.")
        logger.info(f"Item {item.id} removido do carrinho do usuário {request.user.email}")
    except Exception as e:
        logger.error(f"Erro ao remover item: {str(e)}")
        messages.error(request, "Erro ao remover item.")
    
    return redirect('ver_carrinho')


@login_required(login_url='login_usuario')
@require_http_methods(["POST"])
def limpar_carrinho(request):
    """Limpa o carrinho completamente"""
    try:
        carrinho = Carrinho.objects.get(cliente=request.user)
        quantidade_itens = carrinho.itens.count()
        carrinho.limpar()
        messages.success(request, f"Carrinho limpo ({quantidade_itens} itens removidos).")
        logger.info(f"Carrinho do usuário {request.user.email} foi limpo.")
    except Carrinho.DoesNotExist:
        messages.info(request, "Carrinho vazio.")
    except Exception as e:
        logger.error(f"Erro ao limpar carrinho: {str(e)}")
        messages.error(request, "Erro ao limpar carrinho.")
    
    return redirect('ver_carrinho')


def carrinho_context(request):
    """Context processor para incluir dados do carrinho em todos os templates"""
    if request.user.is_authenticated:
        try:
            carrinho = Carrinho.objects.get(cliente=request.user)
            total_itens = carrinho.total_itens()
        except Carrinho.DoesNotExist:
            total_itens = 0
    else:
        total_itens = 0
    
    return {'carrinho_total_itens': total_itens}
