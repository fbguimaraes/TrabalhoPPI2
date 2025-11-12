from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.db.models import Q
from .models import Cliente, PessoaFisica, PessoaJuridica, Categoria, Produto
from django.db import IntegrityError


# ==========================
# VIEWS DE USUÁRIOS
# ==========================

def cadastrar_usuario(request):
    if request.method == "POST":
        tipo = request.POST.get("tipo_cliente")
        email = request.POST.get("email")

        try:
            # Verificar se o email já existe
            if Cliente.objects.filter(email=email).exists():
                messages.error(request, "Este email já está cadastrado no sistema.")
                return render(request, "index.html")

            # Criar usuário base (Cliente)
            cliente = Cliente.objects.create(
                username=email,
                email=email,
                tipo_cliente=tipo,
                password=make_password("123456")
            )

            # Pessoa Física
            if tipo == "PF" or tipo.lower() == "pf":
                cpf = request.POST.get("cpf")
                
                if PessoaFisica.objects.filter(cpf=cpf).exists():
                    cliente.delete()
                    messages.error(request, "Este CPF já está cadastrado no sistema.")
                    return render(request, "index.html")

                PessoaFisica.objects.create(
                    cliente=cliente,
                    nome=request.POST.get("nome"),
                    cpf=cpf,
                    data_nascimento=request.POST.get("data_nascimento"),
                    rg=request.POST.get("rg"),
                    email=email,
                    telefone_principal=request.POST.get("telefone_principal"),
                    telefone_secundario=request.POST.get("telefone_secundario"),
                    cep=request.POST.get("cep"),
                    logradouro=request.POST.get("logradouro"),
                    numero=request.POST.get("numero"),
                    complemento=request.POST.get("complemento"),
                    bairro=request.POST.get("bairro"),
                    cidade=request.POST.get("cidade"),
                    estado=request.POST.get("estado"),
                    pais=request.POST.get("pais"),
                )

            # Pessoa Jurídica
            else:
                cnpj = request.POST.get("cnpj")
                
                if PessoaJuridica.objects.filter(cnpj=cnpj).exists():
                    cliente.delete()
                    messages.error(request, "Este CNPJ já está cadastrado no sistema.")
                    return render(request, "index.html")

                PessoaJuridica.objects.create(
                    cliente=cliente,
                    cnpj=cnpj,
                    razao_social=request.POST.get("razao_social"),
                    nome_fantasia=request.POST.get("nome_fantasia"),
                    data_abertura=request.POST.get("data_abertura"),
                    inscricao_estadual=request.POST.get("inscricao_estadual"),
                    email=email,
                    telefone_principal=request.POST.get("telefone_principal"),
                    telefone_secundario=request.POST.get("telefone_secundario"),
                    site=request.POST.get("site"),
                    cep=request.POST.get("cep"),
                    logradouro=request.POST.get("logradouro"),
                    numero=request.POST.get("numero"),
                    complemento=request.POST.get("complemento"),
                    bairro=request.POST.get("bairro"),
                    cidade=request.POST.get("cidade"),
                    estado=request.POST.get("estado"),
                    pais=request.POST.get("pais"),
                )

            messages.success(request, "Cadastro realizado com sucesso!")
            return redirect("lista_usuarios")

        except IntegrityError:
            messages.error(request, "Erro ao realizar cadastro. Verifique os dados informados.")
            return render(request, "index.html")
        
        except Exception as e:
            messages.error(request, f"Erro inesperado: {str(e)}")
            return render(request, "index.html")

    return render(request, "index.html")


def lista_usuarios(request):
    tipo_filtro = request.GET.get("tipo", "todos")
    
    usuarios = []
    
    if tipo_filtro == "pf":
        for pf in PessoaFisica.objects.all():
            usuarios.append({
                'tipo': 'Pessoa Física',
                'documento': pf.cpf,
                'nome': pf.nome,
                'nome_fantasia': '-',
                'email': pf.email,
                'telefone': pf.telefone_principal,
                'cidade': pf.cidade,
                'estado': pf.estado,
                'pais': pf.pais,
            })
    
    elif tipo_filtro == "pj":
        for pj in PessoaJuridica.objects.all():
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
    
    else:
        for pf in PessoaFisica.objects.all():
            usuarios.append({
                'tipo': 'Pessoa Física',
                'documento': pf.cpf,
                'nome': pf.nome,
                'nome_fantasia': '-',
                'email': pf.email,
                'telefone': pf.telefone_principal,
                'cidade': pf.cidade,
                'estado': pf.estado,
                'pais': pf.pais,
            })
        
        for pj in PessoaJuridica.objects.all():
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

    return render(request, "list_usuarios.html", {
        "usuarios": usuarios,
        "tipo_filtro": tipo_filtro
    })


# ==========================
# VIEWS DE PRODUTOS
# ==========================

def catalogo_produtos(request):
    # Pegar categoria selecionada (se houver)
    categoria_id = request.GET.get('categoria')
    busca = request.GET.get('busca', '').strip()
    
    # Buscar todas as categorias ativas
    categorias = Categoria.objects.filter(ativa=True)
    
    # Filtrar produtos ativos
    produtos = Produto.objects.filter(ativo=True)
    
    # Aplicar filtro de categoria
    categoria_selecionada = None
    if categoria_id:
        try:
            categoria_selecionada = Categoria.objects.get(id=categoria_id, ativa=True)
            produtos = produtos.filter(categoria=categoria_selecionada)
        except Categoria.DoesNotExist:
            pass
    
    # Aplicar busca
    if busca:
        produtos = produtos.filter(
            Q(nome__icontains=busca) | 
            Q(descricao__icontains=busca)
        )
    
    # Ordenar: destaque primeiro, depois mais recentes
    produtos = produtos.order_by('-em_destaque', '-criado_em')
    
    # Estatísticas
    total_produtos = produtos.count()
    produtos_em_estoque = produtos.filter(estoque__gt=0).count()
    produtos_destaque = produtos.filter(em_destaque=True).count()
    
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


def detalhe_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id, ativo=True)
    
    # Produtos relacionados da mesma categoria
    produtos_relacionados = Produto.objects.filter(
        categoria=produto.categoria,
        ativo=True
    ).exclude(id=produto.id).order_by('-em_destaque', '-criado_em')[:4]
    
    context = {
        'produto': produto,
        'produtos_relacionados': produtos_relacionados,
    }
    
    return render(request, 'detalhe_produto.html', context)