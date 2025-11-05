from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from .models import Cliente, PessoaFisica, PessoaJuridica


def cadastrar_usuario(request):
    if request.method == "POST":
        tipo = request.POST.get("tipo_cliente")

        # Criar usuário base (Cliente)
        cliente = Cliente.objects.create(
            username=request.POST.get("email"),  # usando email como login
            email=request.POST.get("email"),
            tipo_cliente=tipo,
            password=make_password("123456") # senha padrão temporária
        )

        # Pessoa Física
        if tipo == "PF" or tipo.lower() == "pf":
            PessoaFisica.objects.create(
                cliente=cliente,
                nome=request.POST.get("nome"),
                cpf=request.POST.get("cpf"),
                data_nascimento=request.POST.get("data_nascimento"),
                rg=request.POST.get("rg"),
                email=request.POST.get("email"),
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
            PessoaJuridica.objects.create(
                cliente=cliente,
                cnpj=request.POST.get("cnpj"),
                razao_social=request.POST.get("razao_social"),
                nome_fantasia=request.POST.get("nome_fantasia"),
                data_abertura=request.POST.get("data_abertura"),
                inscricao_estadual=request.POST.get("inscricao_estadual"),
                email=request.POST.get("email"),
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

        return redirect("lista_usuarios")

    return render(request, "index.html")  # tela de cadastro


def lista_usuarios(request):
    usuarios = []
    for cliente in Cliente.objects.all():
        if cliente.tipo_cliente == "pf" or cliente.tipo_cliente == "PF":
            if hasattr(cliente, 'pf'):
                usuarios.append(cliente.pf)
        else:
            if hasattr(cliente, 'pj'):
                usuarios.append(cliente.pj)

    return render(request, "list_usuarios.html", {"usuarios": usuarios})
