from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from .models import Cliente, PessoaFisica, PessoaJuridica
from .validators import ValidadorCPF, ValidadorCNPJ, ValidadorEmail, ValidadorTelefone, ValidadorCEP, ValidadorData


class LoginForm(forms.Form):
    """Formulário customizado de login com email e senha"""
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'seu@email.com',
            'autofocus': True,
        })
    )
    senha = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Sua senha',
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        senha = cleaned_data.get('senha')

        if email and senha:
            # Tenta autenticar o usuário
            usuario = authenticate(username=email, password=senha)
            if usuario is None:
                raise forms.ValidationError(
                    'Email ou senha incorretos. Verifique seus dados e tente novamente.'
                )
            cleaned_data['usuario'] = usuario
        
        return cleaned_data


class PessoaFisicaForm(forms.ModelForm):
    """Formulário para Pessoa Física"""
    senha = forms.CharField(
        label='Senha',
        min_length=6,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mínimo 6 caracteres',
        })
    )
    confirmar_senha = forms.CharField(
        label='Confirmar Senha',
        min_length=6,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme sua senha',
        })
    )
    
    class Meta:
        model = PessoaFisica
        fields = ['nome', 'cpf', 'data_nascimento', 'rg', 'email', 
                  'telefone_principal', 'telefone_secundario']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome completo'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00', 'maxlength': '14'}),
            'data_nascimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'rg': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'RG (opcional)'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'seuemail@exemplo.com'}),
            'telefone_principal': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000', 'maxlength': '15'}),
            'telefone_secundario': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000 (opcional)', 'maxlength': '15'}),
        }

    def clean_cpf(self):
        cpf = self.cleaned_data['cpf']
        # Validar CPF
        valido, msg = ValidadorCPF.validar(cpf)
        if not valido:
            raise forms.ValidationError(f'CPF inválido: {msg}')
        
        # Verificar duplicação
        if PessoaFisica.objects.filter(cpf=cpf).exists():
            raise forms.ValidationError('Este CPF já está cadastrado no sistema.')
        
        return cpf

    def clean_email(self):
        email = self.cleaned_data['email']
        # Validar email
        valido, msg = ValidadorEmail.validar(email)
        if not valido:
            raise forms.ValidationError(f'Email inválido: {msg}')
        
        # Verificar duplicação
        if Cliente.objects.filter(email=email).exists():
            raise forms.ValidationError('Este email já está cadastrado no sistema.')
        
        return email

    def clean_data_nascimento(self):
        data = self.cleaned_data['data_nascimento']
        valido, msg = ValidadorData.validar(str(data), 'Data de nascimento')
        if not valido:
            raise forms.ValidationError(f'Data inválida: {msg}')
        return data

    def clean_telefone_principal(self):
        telefone = self.cleaned_data['telefone_principal']
        valido, msg = ValidadorTelefone.validar(telefone)
        if not valido:
            raise forms.ValidationError(f'Telefone inválido: {msg}')
        return telefone

    def clean_telefone_secundario(self):
        telefone = self.cleaned_data.get('telefone_secundario', '')
        if telefone:
            valido, msg = ValidadorTelefone.validar(telefone)
            if not valido:
                raise forms.ValidationError(f'Telefone secundário inválido: {msg}')
        return telefone

    def clean(self):
        cleaned_data = super().clean()
        senha = cleaned_data.get('senha')
        confirmar_senha = cleaned_data.get('confirmar_senha')

        if senha and confirmar_senha:
            if senha != confirmar_senha:
                raise forms.ValidationError('As senhas não conferem.')

        return cleaned_data


class EnderecoForm(forms.Form):
    """Formulário reutilizável para endereço"""
    cep = forms.CharField(
        label='CEP',
        max_length=9,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '00000-000',
            'maxlength': '9',
        })
    )
    logradouro = forms.CharField(
        label='Logradouro',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rua, Avenida, etc.',
        })
    )
    numero = forms.CharField(
        label='Número',
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número',
        })
    )
    complemento = forms.CharField(
        label='Complemento (opcional)',
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apto, Sala, etc.',
        })
    )
    bairro = forms.CharField(
        label='Bairro',
        max_length=80,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Bairro',
        })
    )
    cidade = forms.CharField(
        label='Cidade',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Cidade',
        })
    )
    estado = forms.CharField(
        label='Estado',
        max_length=2,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'UF',
            'maxlength': '2',
        })
    )
    pais = forms.CharField(
        label='País',
        max_length=50,
        initial='Brasil',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'País',
        })
    )

    def clean_cep(self):
        cep = self.cleaned_data['cep']
        valido, msg = ValidadorCEP.validar(cep)
        if not valido:
            raise forms.ValidationError(f'CEP inválido: {msg}')
        return cep

    def clean_estado(self):
        estado = self.cleaned_data['estado']
        if len(estado) != 2:
            raise forms.ValidationError('Estado deve conter 2 caracteres.')
        return estado.upper()


class PessoaJuridicaForm(forms.ModelForm):
    """Formulário para Pessoa Jurídica"""
    senha = forms.CharField(
        label='Senha',
        min_length=6,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mínimo 6 caracteres',
        })
    )
    confirmar_senha = forms.CharField(
        label='Confirmar Senha',
        min_length=6,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme sua senha',
        })
    )

    class Meta:
        model = PessoaJuridica
        fields = ['cnpj', 'razao_social', 'nome_fantasia', 'data_abertura',
                  'inscricao_estadual', 'email', 'telefone_principal', 
                  'telefone_secundario', 'site']
        widgets = {
            'cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00.000.000/0000-00', 'maxlength': '18'}),
            'razao_social': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Razão Social'}),
            'nome_fantasia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome Fantasia (opcional)'}),
            'data_abertura': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'inscricao_estadual': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'IE (opcional)'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'contato@empresa.com'}),
            'telefone_principal': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000', 'maxlength': '15'}),
            'telefone_secundario': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000 (opcional)', 'maxlength': '15'}),
            'site': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.exemplo.com (opcional)'}),
        }

    def clean_cnpj(self):
        cnpj = self.cleaned_data['cnpj']
        valido, msg = ValidadorCNPJ.validar(cnpj)
        if not valido:
            raise forms.ValidationError(f'CNPJ inválido: {msg}')
        
        if PessoaJuridica.objects.filter(cnpj=cnpj).exists():
            raise forms.ValidationError('Este CNPJ já está cadastrado no sistema.')
        
        return cnpj

    def clean_email(self):
        email = self.cleaned_data['email']
        valido, msg = ValidadorEmail.validar(email)
        if not valido:
            raise forms.ValidationError(f'Email inválido: {msg}')
        
        if Cliente.objects.filter(email=email).exists():
            raise forms.ValidationError('Este email já está cadastrado no sistema.')
        
        return email

    def clean_telefone_principal(self):
        telefone = self.cleaned_data['telefone_principal']
        valido, msg = ValidadorTelefone.validar(telefone)
        if not valido:
            raise forms.ValidationError(f'Telefone inválido: {msg}')
        return telefone

    def clean_telefone_secundario(self):
        telefone = self.cleaned_data.get('telefone_secundario', '')
        if telefone:
            valido, msg = ValidadorTelefone.validar(telefone)
            if not valido:
                raise forms.ValidationError(f'Telefone secundário inválido: {msg}')
        return telefone

    def clean(self):
        cleaned_data = super().clean()
        senha = cleaned_data.get('senha')
        confirmar_senha = cleaned_data.get('confirmar_senha')

        if senha and confirmar_senha:
            if senha != confirmar_senha:
                raise forms.ValidationError('As senhas não conferem.')

        return cleaned_data
