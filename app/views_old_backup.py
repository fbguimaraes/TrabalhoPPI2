from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Cliente, PessoaFisica, PessoaJuridica, Categoria, Produto
from .validators import ValidadorCPF, ValidadorCNPJ, ValidadorEmail, ValidadorTelefone, ValidadorCEP, ValidadorData
from django.db import IntegrityError


# ==========================
# VIEWS DE AUTENTICAÇÃO
# ==========================

def login_usuario(request):
    """View de login de usuários"""
    if request.user.is_authenticated:
        return redirect("catalogo_produtos")
    
    if request.method == "POST":
        email = request.POST.get("email")
        senha = request.POST.get("senha")
        
        if not email or not senha:
            messages.error(request, "Email e senha são obrigatórios.")
            return render(request, "login.html", {"email": email})
        
        # Tenta autenticar usando email como username
        usuario = authenticate(request, username=email, password=senha)
        
        if usuario is not None:
            login(request, usuario)
            messages.success(request, f"Bem-vindo de volta, {email}!")
            return redirect("catalogo_produtos")
        else:
            messages.error(request, "Email ou senha incorretos.")
            return render(request, "login.html", {"email": email})
    
    return render(request, "login.html")


def logout_usuario(request):
    """View para deslogar usuário"""
    logout(request)
    messages.success(request, "Logout realizado com sucesso!")
    return redirect("login_usuario")


@login_required(login_url='login_usuario')
def perfil_usuario(request):
    """View para exibir o perfil do usuário logado"""
    usuario = request.user
    
    # Tentar pegar dados da Pessoa Física ou Jurídica
    dados_adicionais = None
    tipo_cliente = usuario.tipo_cliente
    
    if tipo_cliente == 'pf':
        try:
            dados_adicionais = usuario.pf
        except:
            dados_adicionais = None
    elif tipo_cliente == 'pj':
        try:
            dados_adicionais = usuario.pj
        except:
            dados_adicionais = None
    
    context = {
        'usuario': usuario,
        'dados_adicionais': dados_adicionais,
        'tipo_cliente': tipo_cliente,
    }
    
    return render(request, 'perfil_usuario.html', context)
# VIEWS DE USUÁRIOS
# ==========================

def cadastro_usuario(request):
    """View de cadastro de usuários (nova view separada)"""
    if request.method == "POST":
        tipo = request.POST.get("tipo_cliente")
        email = request.POST.get("email")
        senha = request.POST.get("senha")
        confirmar_senha = request.POST.get("confirmar_senha")
        erros = []

        # Validar senhas
        if not senha or not confirmar_senha:
            erros.append("Senha e confirmação são obrigatórias")
        elif senha != confirmar_senha:
            erros.append("As senhas não conferem")
        elif len(senha) < 6:
            erros.append("A senha deve ter pelo menos 6 caracteres")

        try:
            # ==================== VALIDAÇÕES PESSOA FÍSICA ====================
            if tipo == "PF" or tipo.lower() == "pf":
                cpf = request.POST.get("cpf")
                nome = request.POST.get("nome")
                data_nascimento = request.POST.get("data_nascimento")
                telefone_principal = request.POST.get("telefone_principal")
                telefone_secundario = request.POST.get("telefone_secundario", "")
                cep = request.POST.get("cep")
                
                # Validar CPF
                cpf_valido, msg_cpf = ValidadorCPF.validar(cpf)
                if not cpf_valido:
                    erros.append(f"CPF: {msg_cpf}")
                
                # Validar Nome
                if not nome or len(nome.strip()) < 3:
                    erros.append("Nome completo deve ter pelo menos 3 caracteres")
                
                # Validar Data de Nascimento
                if data_nascimento:
                    data_valida, msg_data = ValidadorData.validar(data_nascimento, "Data de nascimento")
                    if not data_valida:
                        erros.append(f"Data de nascimento: {msg_data}")
                else:
                    erros.append("Data de nascimento é obrigatória")
                
                # Validar Email
                email_valido, msg_email = ValidadorEmail.validar(email)
                if not email_valido:
                    erros.append(f"Email: {msg_email}")
                
                # Validar Telefone Principal
                telefone_valido, msg_tel = ValidadorTelefone.validar(telefone_principal)
                if not telefone_valido:
                    erros.append(f"Telefone principal: {msg_tel}")
                
                # Validar Telefone Secundário (se preenchido)
                if telefone_secundario:
                    telefone_sec_valido, msg_tel_sec = ValidadorTelefone.validar(telefone_secundario)
                    if not telefone_sec_valido:
                        erros.append(f"Telefone secundário: {msg_tel_sec}")
                
                # Validar CEP
                cep_valido, msg_cep = ValidadorCEP.validar(cep)
                if not cep_valido:
                    erros.append(f"CEP: {msg_cep}")
                
                # Validar campos de endereço
                logradouro = request.POST.get("logradouro")
                numero = request.POST.get("numero")
                bairro = request.POST.get("bairro")
                cidade = request.POST.get("cidade")
                estado = request.POST.get("estado")
                
                if not logradouro or not logradouro.strip():
                    erros.append("Logradouro é obrigatório")
                if not numero or not numero.strip():
                    erros.append("Número é obrigatório")
                if not bairro or not bairro.strip():
                    erros.append("Bairro é obrigatório")
                if not cidade or not cidade.strip():
                    erros.append("Cidade é obrigatória")
                if not estado or len(estado.strip()) != 2:
                    erros.append("Estado deve conter 2 caracteres")
                
                # Se houver erros, retornar com mensagens
                if erros:
                    for erro in erros:
                        messages.error(request, erro)
                    return render(request, "cadastro.html", {
                        'tipo_selecionado': 'pf',
                        'form_data': request.POST
                    })
                
                # Verificar se o email já existe
                if Cliente.objects.filter(email=email).exists():
                    messages.error(request, "Este email já está cadastrado no sistema.")
                    return render(request, "cadastro.html", {'tipo_selecionado': 'pf', 'form_data': request.POST})

                # Verificar se o CPF já existe
                if PessoaFisica.objects.filter(cpf=cpf).exists():
                    messages.error(request, "Este CPF já está cadastrado no sistema.")
                    return render(request, "cadastro.html", {'tipo_selecionado': 'pf', 'form_data': request.POST})

                # Criar usuário base (Cliente)
                cliente = Cliente.objects.create(
                    username=email,
                    email=email,
                    tipo_cliente="pf",
                    password=make_password(senha)
                )

                PessoaFisica.objects.create(
                    cliente=cliente,
                    nome=nome,
                    cpf=cpf,
                    data_nascimento=data_nascimento,
                    rg=request.POST.get("rg", ""),
                    email=email,
                    telefone_principal=telefone_principal,
                    telefone_secundario=telefone_secundario,
                    cep=cep,
                    logradouro=logradouro,
                    numero=numero,
                    complemento=request.POST.get("complemento", ""),
                    bairro=bairro,
                    cidade=cidade,
                    estado=estado,
                    pais=request.POST.get("pais", "Brasil"),
                )

                messages.success(request, "Cadastro realizado com sucesso! Faça login para continuar.")
                return redirect("login_usuario")

            # ==================== VALIDAÇÕES PESSOA JURÍDICA ====================
            else:
                cnpj = request.POST.get("cnpj")
                razao_social = request.POST.get("razao_social")
                data_abertura = request.POST.get("data_abertura")
                telefone_principal = request.POST.get("telefone_principal")
                telefone_secundario = request.POST.get("telefone_secundario", "")
                cep = request.POST.get("cep")
                
                # Validar CNPJ
                cnpj_valido, msg_cnpj = ValidadorCNPJ.validar(cnpj)
                if not cnpj_valido:
                    erros.append(f"CNPJ: {msg_cnpj}")
                
                # Validar Razão Social
                if not razao_social or len(razao_social.strip()) < 3:
                    erros.append("Razão social deve ter pelo menos 3 caracteres")
                
                # Validar Data de Abertura
                if data_abertura:
                    data_valida, msg_data = ValidadorData.validar(data_abertura, "Data de abertura")
                    if not data_valida:
                        erros.append(f"Data de abertura: {msg_data}")
                else:
                    erros.append("Data de abertura é obrigatória")
                
                # Validar Email
                email_valido, msg_email = ValidadorEmail.validar(email)
                if not email_valido:
                    erros.append(f"Email: {msg_email}")
                
                # Validar Telefone Principal
                telefone_valido, msg_tel = ValidadorTelefone.validar(telefone_principal)
                if not telefone_valido:
                    erros.append(f"Telefone principal: {msg_tel}")
                
                # Validar Telefone Secundário (se preenchido)
                if telefone_secundario:
                    telefone_sec_valido, msg_tel_sec = ValidadorTelefone.validar(telefone_secundario)
                    if not telefone_sec_valido:
                        erros.append(f"Telefone secundário: {msg_tel_sec}")
                
                # Validar CEP
                cep_valido, msg_cep = ValidadorCEP.validar(cep)
                if not cep_valido:
                    erros.append(f"CEP: {msg_cep}")
                
                # Validar campos de endereço
                logradouro = request.POST.get("logradouro")
                numero = request.POST.get("numero")
                bairro = request.POST.get("bairro")
                cidade = request.POST.get("cidade")
                estado = request.POST.get("estado")
                
                if not logradouro or not logradouro.strip():
                    erros.append("Logradouro é obrigatório")
                if not numero or not numero.strip():
                    erros.append("Número é obrigatório")
                if not bairro or not bairro.strip():
                    erros.append("Bairro é obrigatório")
                if not cidade or not cidade.strip():
                    erros.append("Cidade é obrigatória")
                if not estado or len(estado.strip()) != 2:
                    erros.append("Estado deve conter 2 caracteres")
                
                # Se houver erros, retornar com mensagens
                if erros:
                    for erro in erros:
                        messages.error(request, erro)
                    return render(request, "cadastro.html", {
                        'tipo_selecionado': 'pj',
                        'form_data': request.POST
                    })
                
                # Verificar se o email já existe
                if Cliente.objects.filter(email=email).exists():
                    messages.error(request, "Este email já está cadastrado no sistema.")
                    return render(request, "cadastro.html", {'tipo_selecionado': 'pj', 'form_data': request.POST})

                # Verificar se o CNPJ já existe
                if PessoaJuridica.objects.filter(cnpj=cnpj).exists():
                    messages.error(request, "Este CNPJ já está cadastrado no sistema.")
                    return render(request, "cadastro.html", {'tipo_selecionado': 'pj', 'form_data': request.POST})

                # Criar usuário base (Cliente)
                cliente = Cliente.objects.create(
                    username=email,
                    email=email,
                    tipo_cliente="pj",
                    password=make_password(senha)
                )

                PessoaJuridica.objects.create(
                    cliente=cliente,
                    cnpj=cnpj,
                    razao_social=razao_social,
                    nome_fantasia=request.POST.get("nome_fantasia", ""),
                    data_abertura=data_abertura,
                    inscricao_estadual=request.POST.get("inscricao_estadual", ""),
                    email=email,
                    telefone_principal=telefone_principal,
                    telefone_secundario=telefone_secundario,
                    site=request.POST.get("site", ""),
                    cep=cep,
                    logradouro=logradouro,
                    numero=numero,
                    complemento=request.POST.get("complemento", ""),
                    bairro=bairro,
                    cidade=cidade,
                    estado=estado,
                    pais=request.POST.get("pais", "Brasil"),
                )

                messages.success(request, "Cadastro realizado com sucesso! Faça login para continuar.")
                return redirect("login_usuario")

        except IntegrityError:
            messages.error(request, "Erro ao realizar cadastro. Verifique os dados informados.")
            return render(request, "cadastro.html")
        
        except Exception as e:
            messages.error(request, f"Erro inesperado: {str(e)}")
            return render(request, "cadastro.html")

    return render(request, "cadastro.html")
    if request.method == "POST":
        tipo = request.POST.get("tipo_cliente")
        email = request.POST.get("email")
        erros = []

        try:
            # ==================== VALIDAÇÕES PESSOA FÍSICA ====================
            if tipo == "PF" or tipo.lower() == "pf":
                cpf = request.POST.get("cpf")
                nome = request.POST.get("nome")
                data_nascimento = request.POST.get("data_nascimento")
                telefone_principal = request.POST.get("telefone_principal")
                telefone_secundario = request.POST.get("telefone_secundario", "")
                cep = request.POST.get("cep")
                
                # Validar CPF
                cpf_valido, msg_cpf = ValidadorCPF.validar(cpf)
                if not cpf_valido:
                    erros.append(f"CPF: {msg_cpf}")
                
                # Validar Nome
                if not nome or len(nome.strip()) < 3:
                    erros.append("Nome completo deve ter pelo menos 3 caracteres")
                
                # Validar Data de Nascimento
                if data_nascimento:
                    data_valida, msg_data = ValidadorData.validar(data_nascimento, "Data de nascimento")
                    if not data_valida:
                        erros.append(f"Data de nascimento: {msg_data}")
                else:
                    erros.append("Data de nascimento é obrigatória")
                
                # Validar Email
                email_valido, msg_email = ValidadorEmail.validar(email)
                if not email_valido:
                    erros.append(f"Email: {msg_email}")
                
                # Validar Telefone Principal
                telefone_valido, msg_tel = ValidadorTelefone.validar(telefone_principal)
                if not telefone_valido:
                    erros.append(f"Telefone principal: {msg_tel}")
                
                # Validar Telefone Secundário (se preenchido)
                if telefone_secundario:
                    telefone_sec_valido, msg_tel_sec = ValidadorTelefone.validar(telefone_secundario)
                    if not telefone_sec_valido:
                        erros.append(f"Telefone secundário: {msg_tel_sec}")
                
                # Validar CEP
                cep_valido, msg_cep = ValidadorCEP.validar(cep)
                if not cep_valido:
                    erros.append(f"CEP: {msg_cep}")
                
                # Validar campos de endereço
                logradouro = request.POST.get("logradouro")
                numero = request.POST.get("numero")
                bairro = request.POST.get("bairro")
                cidade = request.POST.get("cidade")
                estado = request.POST.get("estado")
                
                if not logradouro or not logradouro.strip():
                    erros.append("Logradouro é obrigatório")
                if not numero or not numero.strip():
                    erros.append("Número é obrigatório")
                if not bairro or not bairro.strip():
                    erros.append("Bairro é obrigatório")
                if not cidade or not cidade.strip():
                    erros.append("Cidade é obrigatória")
                if not estado or len(estado.strip()) != 2:
                    erros.append("Estado deve conter 2 caracteres")
                
                # Se houver erros, retornar com mensagens
                if erros:
                    for erro in erros:
                        messages.error(request, erro)
                    # Retornar com dados preenchidos
                    return render(request, "index.html", {
                        'tipo_selecionado': 'pf',
                        'form_data': request.POST
                    })
                
                # Verificar se o email já existe
                if Cliente.objects.filter(email=email).exists():
                    messages.error(request, "Este email já está cadastrado no sistema.")
                    return render(request, "index.html", {'tipo_selecionado': 'pf', 'form_data': request.POST})

                # Verificar se o CPF já existe
                if PessoaFisica.objects.filter(cpf=cpf).exists():
                    messages.error(request, "Este CPF já está cadastrado no sistema.")
                    return render(request, "index.html", {'tipo_selecionado': 'pf', 'form_data': request.POST})

                # Criar usuário base (Cliente)
                cliente = Cliente.objects.create(
                    username=email,
                    email=email,
                    tipo_cliente="pf",
                    password=make_password("123456")
                )

                PessoaFisica.objects.create(
                    cliente=cliente,
                    nome=nome,
                    cpf=cpf,
                    data_nascimento=data_nascimento,
                    rg=request.POST.get("rg", ""),
                    email=email,
                    telefone_principal=telefone_principal,
                    telefone_secundario=telefone_secundario,
                    cep=cep,
                    logradouro=logradouro,
                    numero=numero,
                    complemento=request.POST.get("complemento", ""),
                    bairro=bairro,
                    cidade=cidade,
                    estado=estado,
                    pais=request.POST.get("pais", "Brasil"),
                )

                messages.success(request, "Cadastro realizado com sucesso!")
                return redirect("catalogo_produtos")

            # ==================== VALIDAÇÕES PESSOA JURÍDICA ====================
            else:
                cnpj = request.POST.get("cnpj")
                razao_social = request.POST.get("razao_social")
                data_abertura = request.POST.get("data_abertura")
                telefone_principal = request.POST.get("telefone_principal")
                telefone_secundario = request.POST.get("telefone_secundario", "")
                cep = request.POST.get("cep")
                
                # Validar CNPJ
                cnpj_valido, msg_cnpj = ValidadorCNPJ.validar(cnpj)
                if not cnpj_valido:
                    erros.append(f"CNPJ: {msg_cnpj}")
                
                # Validar Razão Social
                if not razao_social or len(razao_social.strip()) < 3:
                    erros.append("Razão social deve ter pelo menos 3 caracteres")
                
                # Validar Data de Abertura
                if data_abertura:
                    data_valida, msg_data = ValidadorData.validar(data_abertura, "Data de abertura")
                    if not data_valida:
                        erros.append(f"Data de abertura: {msg_data}")
                else:
                    erros.append("Data de abertura é obrigatória")
                
                # Validar Email
                email_valido, msg_email = ValidadorEmail.validar(email)
                if not email_valido:
                    erros.append(f"Email: {msg_email}")
                
                # Validar Telefone Principal
                telefone_valido, msg_tel = ValidadorTelefone.validar(telefone_principal)
                if not telefone_valido:
                    erros.append(f"Telefone principal: {msg_tel}")
                
                # Validar Telefone Secundário (se preenchido)
                if telefone_secundario:
                    telefone_sec_valido, msg_tel_sec = ValidadorTelefone.validar(telefone_secundario)
                    if not telefone_sec_valido:
                        erros.append(f"Telefone secundário: {msg_tel_sec}")
                
                # Validar CEP
                cep_valido, msg_cep = ValidadorCEP.validar(cep)
                if not cep_valido:
                    erros.append(f"CEP: {msg_cep}")
                
                # Validar campos de endereço
                logradouro = request.POST.get("logradouro")
                numero = request.POST.get("numero")
                bairro = request.POST.get("bairro")
                cidade = request.POST.get("cidade")
                estado = request.POST.get("estado")
                
                if not logradouro or not logradouro.strip():
                    erros.append("Logradouro é obrigatório")
                if not numero or not numero.strip():
                    erros.append("Número é obrigatório")
                if not bairro or not bairro.strip():
                    erros.append("Bairro é obrigatório")
                if not cidade or not cidade.strip():
                    erros.append("Cidade é obrigatória")
                if not estado or len(estado.strip()) != 2:
                    erros.append("Estado deve conter 2 caracteres")
                
                # Se houver erros, retornar com mensagens
                if erros:
                    for erro in erros:
                        messages.error(request, erro)
                    # Retornar com dados preenchidos
                    return render(request, "index.html", {
                        'tipo_selecionado': 'pj',
                        'form_data': request.POST
                    })
                
                # Verificar se o email já existe
                if Cliente.objects.filter(email=email).exists():
                    messages.error(request, "Este email já está cadastrado no sistema.")
                    return render(request, "index.html", {'tipo_selecionado': 'pj', 'form_data': request.POST})

                # Verificar se o CNPJ já existe
                if PessoaJuridica.objects.filter(cnpj=cnpj).exists():
                    messages.error(request, "Este CNPJ já está cadastrado no sistema.")
                    return render(request, "index.html", {'tipo_selecionado': 'pj', 'form_data': request.POST})

                # Criar usuário base (Cliente)
                cliente = Cliente.objects.create(
                    username=email,
                    email=email,
                    tipo_cliente="pj",
                    password=make_password("123456")
                )

                PessoaJuridica.objects.create(
                    cliente=cliente,
                    cnpj=cnpj,
                    razao_social=razao_social,
                    nome_fantasia=request.POST.get("nome_fantasia", ""),
                    data_abertura=data_abertura,
                    inscricao_estadual=request.POST.get("inscricao_estadual", ""),
                    email=email,
                    telefone_principal=telefone_principal,
                    telefone_secundario=telefone_secundario,
                    site=request.POST.get("site", ""),
                    cep=cep,
                    logradouro=logradouro,
                    numero=numero,
                    complemento=request.POST.get("complemento", ""),
                    bairro=bairro,
                    cidade=cidade,
                    estado=estado,
                    pais=request.POST.get("pais", "Brasil"),
                )

                messages.success(request, "Cadastro realizado com sucesso!")
                return redirect("catalogo_produtos")

        except IntegrityError:
            messages.error(request, "Erro ao realizar cadastro. Verifique os dados informados.")
            return render(request, "index.html")
        
        except Exception as e:
            messages.error(request, f"Erro inesperado: {str(e)}")
            return render(request, "index.html")

    return render(request, "index.html")


def lista_usuarios(request):
    """View protegida para listar usuários (apenas para admin)"""
    if not request.user.is_staff:
        messages.error(request, "Você não tem permissão para acessar esta página.")
        return redirect("catalogo_produtos")
    
    tipo_filtro = request.GET.get("tipo", "todos")
    
    usuarios_pf = []
    usuarios_pj = []
    
    if tipo_filtro in ["pf", "todos"]:
        usuarios_pf = list(PessoaFisica.objects.all())
    
    if tipo_filtro in ["pj", "todos"]:
        usuarios_pj = list(PessoaJuridica.objects.all())
    
    return render(request, "list_usuarios.html", {
        "usuarios_pf": usuarios_pf,
        "usuarios_pj": usuarios_pj,
        "tipo_filtro": tipo_filtro
    })


# ==========================
# VIEWS DE PRODUTOS
# ==========================

@login_required(login_url='login_usuario')
def catalogo_produtos(request):
    # Pegar categoria selecionada (se houver)
    categoria_id = request.GET.get('categoria')
    busca = request.GET.get('busca', '').strip()
    
    # Buscar todas as categorias ativas
    categorias = Categoria.objects.filter(ativa=True).prefetch_related('produtos')
    
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
    
    # Enriquecer categorias com contagem de produtos ativos e em estoque
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