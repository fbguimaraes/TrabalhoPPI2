"""
Utilitários para geração de Boleto e PIX
"""

import qrcode
from io import BytesIO
import base64
from datetime import datetime, timedelta
from decimal import Decimal
import random
import string


class PixGenerator:
    """Gerador de QR Code e dados PIX"""
    
    @staticmethod
    def gerar_qr_code(chave_pix: str, valor: Decimal, descricao: str = "") -> tuple:
        """
        Gera QR Code PIX dinâmico
        
        Returns:
            Tuple (qr_code_string, qr_code_base64)
        """
        # Criar dados EMV para PIX
        # Formato simplificado: chave_pix|valor|descricao
        qr_data = f"00020126580014br.gov.bcb.pix0136{chave_pix}520400005303986540510{format(valor, '.2f')}5802BR5913Loja%20Test5914Sao%20Paulo62410503***63041D3D"
        
        # Gerar QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Converter para imagem
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Converter para Base64 para exibição em HTML
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return qr_data, qr_base64
    
    @staticmethod
    def gerar_chave_aleatoria() -> str:
        """Gera uma chave PIX aleatória (UUID)"""
        # Formato: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
        def random_hex(length):
            return ''.join(random.choices(string.hexdigits[:16], k=length))
        
        return f"{random_hex(8)}-{random_hex(4)}-{random_hex(4)}-{random_hex(4)}-{random_hex(12)}"
    
    @staticmethod
    def get_expiracao_pix(minutos=15) -> datetime:
        """Retorna data de expiração do PIX (padrão 15 minutos)"""
        return datetime.now() + timedelta(minutes=minutos)


class BoletoGenerator:
    """Gerador de dados de Boleto Bancário"""
    
    # Banco do Brasil
    BANCO_CODIGO = "001"
    AGENCIA = "0001"
    CONTA = "00123456789"
    
    @staticmethod
    def gerar_codigo_barras(numero_sequencial: int) -> tuple:
        """
        Gera código de barras e linha digitável do boleto
        
        Retorna:
            Tuple (codigo_barras, linha_digitavel, numero_boleto)
        """
        # Número sequencial do boleto (XXXXXXXX)
        numero = str(numero_sequencial).zfill(8)
        
        # Dígito verificador do boleto
        def calc_dv_boleto(campos):
            sequencia = "0123456789"
            resto = sum(int(c) * (i + 2) for i, c in enumerate(campos[::-1])) % 11
            return "0" if resto == 0 else "1" if resto == 1 else str(11 - resto)
        
        # Estrutura: Banco(3) + DV(1) + Data(4) + Agencia(4) + Conta(8) + Numero(8)
        dv = calc_dv_boleto(f"{BoletoGenerator.BANCO_CODIGO}{BoletoGenerator.AGENCIA}{BoletoGenerator.CONTA}{numero}")
        
        codigo_barras = f"{BoletoGenerator.BANCO_CODIGO}{dv}00000{BoletoGenerator.AGENCIA}{BoletoGenerator.CONTA}{numero}"
        
        # Linha Digitável
        # Formato: BANCO.CAMPO1 CAMPO2.CAMPO3 CAMPO4.CAMPO5 DV DATA VALOR
        campo1 = f"{BoletoGenerator.BANCO_CODIGO}.{BoletoGenerator.AGENCIA}{BoletoGenerator.CONTA[0:2]}"
        campo2 = f"{BoletoGenerator.CONTA[2:7]}.{numero[0:4]}"
        campo3 = f"{numero[4:8]}.{BoletoGenerator.BANCO_CODIGO}"
        
        linha_digitavel = f"{campo1} {campo2} {campo3}"
        
        numero_boleto = f"{BoletoGenerator.BANCO_CODIGO}.{numero}.{BoletoGenerator.AGENCIA}"
        
        return codigo_barras, linha_digitavel, numero_boleto
    
    @staticmethod
    def gerar_vencimento(dias=7) -> datetime:
        """Gera data de vencimento do boleto"""
        return datetime.now() + timedelta(days=dias)
    
    @staticmethod
    def formatar_codigo_barras(codigo: str) -> str:
        """Formata código de barras para exibição"""
        return f"{codigo[:5]}.{codigo[5:10]} {codigo[10:15]}.{codigo[15:20]} {codigo[20:25]}.{codigo[25:30]} {codigo[30:35]}.{codigo[35:40]} {codigo[40:47]}"
    
    @staticmethod
    def formatar_linha_digitavel(linha: str) -> str:
        """Formata linha digitável para exibição"""
        # Remove pontos e espaços, depois formata
        limpo = linha.replace(".", "").replace(" ", "")
        return f"{limpo[:5]}.{limpo[5:10]} {limpo[10:15]}.{limpo[15:20]} {limpo[20:25]}.{limpo[25:30]} {limpo[30:35]}.{limpo[35:42]}.{limpo[42:47]}"


class PagamentoUtils:
    """Utilitários gerais de pagamento"""
    
    @staticmethod
    def formatar_valor(valor: Decimal) -> str:
        """Formata valor monetário"""
        return f"R$ {valor:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')
    
    @staticmethod
    def gerar_numero_transacao() -> str:
        """Gera número único de transação"""
        from django.utils import timezone
        import hashlib
        
        timestamp = timezone.now().isoformat()
        random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        return hashlib.md5(f"{timestamp}{random_str}".encode()).hexdigest()[:20].upper()
