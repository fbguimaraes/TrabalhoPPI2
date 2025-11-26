import re
from datetime import datetime

class ValidadorCPF:
    @staticmethod
    def validar(cpf):
        """Valida CPF retornando (válido: bool, mensagem: str)"""
        cpf_numeros = cpf.replace('.', '').replace('-', '')
        
        if len(cpf_numeros) != 11:
            return False, "CPF deve conter 11 dígitos"
        
        if not cpf_numeros.isdigit():
            return False, "CPF deve conter apenas números"
        
        if cpf_numeros == cpf_numeros[0] * 11:
            return False, "CPF inválido (todos os dígitos iguais)"
        
        # Validar primeiro dígito verificador
        soma = sum(int(cpf_numeros[i]) * (10 - i) for i in range(9))
        resto = soma % 11
        dv1 = 0 if resto < 2 else 11 - resto
        
        if int(cpf_numeros[9]) != dv1:
            return False, "CPF inválido (dígito verificador incorreto)"
        
        # Validar segundo dígito verificador
        soma = sum(int(cpf_numeros[i]) * (11 - i) for i in range(10))
        resto = soma % 11
        dv2 = 0 if resto < 2 else 11 - resto
        
        if int(cpf_numeros[10]) != dv2:
            return False, "CPF inválido (dígito verificador incorreto)"
        
        return True, "CPF válido"


class ValidadorCNPJ:
    @staticmethod
    def validar(cnpj):
        """Valida CNPJ retornando (válido: bool, mensagem: str)"""
        cnpj_numeros = cnpj.replace('.', '').replace('/', '').replace('-', '')
        
        if len(cnpj_numeros) != 14:
            return False, "CNPJ deve conter 14 dígitos"
        
        if not cnpj_numeros.isdigit():
            return False, "CNPJ deve conter apenas números"
        
        if cnpj_numeros == cnpj_numeros[0] * 14:
            return False, "CNPJ inválido (todos os dígitos iguais)"
        
        # Validar primeiro dígito verificador
        tamanho = 12
        numeros = cnpj_numeros[:tamanho]
        digitos = cnpj_numeros[tamanho:]
        soma = 0
        pos = 0
        
        for i in range(tamanho - 1, -1, -1):
            pos += 1
            soma += int(numeros[tamanho - pos]) * (pos % 8 + 2)
        
        resultado = 0 if soma % 11 < 2 else 11 - soma % 11
        if resultado != int(digitos[0]):
            return False, "CNPJ inválido (dígito verificador incorreto)"
        
        # Validar segundo dígito verificador
        tamanho = 13
        numeros = cnpj_numeros[:tamanho]
        soma = 0
        pos = 0
        
        for i in range(tamanho - 1, -1, -1):
            pos += 1
            soma += int(numeros[tamanho - pos]) * (pos % 8 + 2)
        
        resultado = 0 if soma % 11 < 2 else 11 - soma % 11
        if resultado != int(digitos[1]):
            return False, "CNPJ inválido (dígito verificador incorreto)"
        
        return True, "CNPJ válido"


class ValidadorEmail:
    @staticmethod
    def validar(email):
        """Valida email retornando (válido: bool, mensagem: str)"""
        padrão = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(padrão, email):
            return False, "Email inválido"
        return True, "Email válido"


class ValidadorTelefone:
    @staticmethod
    def validar(telefone):
        """Valida telefone retornando (válido: bool, mensagem: str)"""
        telefone_numeros = telefone.replace('(', '').replace(')', '').replace('-', '').replace(' ', '')
        
        if not telefone_numeros.isdigit():
            return False, "Telefone deve conter apenas números"
        
        if len(telefone_numeros) < 10 or len(telefone_numeros) > 11:
            return False, "Telefone deve ter 10 ou 11 dígitos"
        
        return True, "Telefone válido"


class ValidadorCEP:
    @staticmethod
    def validar(cep):
        """Valida CEP retornando (válido: bool, mensagem: str)"""
        cep_numeros = cep.replace('-', '')
        
        if not cep_numeros.isdigit():
            return False, "CEP deve conter apenas números"
        
        if len(cep_numeros) != 8:
            return False, "CEP deve conter 8 dígitos"
        
        return True, "CEP válido"


class ValidadorData:
    @staticmethod
    def validar(data_str, campo="Data"):
        """Valida data retornando (válido: bool, mensagem: str)"""
        try:
            data = datetime.strptime(data_str, '%Y-%m-%d').date()
            hoje = datetime.now().date()
            
            if data >= hoje:
                return False, f"{campo} não pode ser futura"
            
            return True, f"{campo} válida"
        except ValueError:
            return False, f"{campo} inválida"
