from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Categoria, Produto, PessoaFisica

User = get_user_model()


class AuthenticationTests(TestCase):
    """Testes de autenticação e login"""

    def setUp(self):
        """Configuração inicial para testes"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123',
            tipo_cliente='pf'
        )

    def test_login_page_accessible(self):
        """Verifica se a página de login é acessível"""
        response = self.client.get(reverse('login_usuario'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_login_with_valid_credentials(self):
        """Testa login com credenciais válidas"""
        response = self.client.post(reverse('login_usuario'), {
            'email': 'test@example.com',
            'senha': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)  # Redirecionamento
        self.assertRedirects(response, reverse('catalogo_produtos'))

    def test_login_with_invalid_credentials(self):
        """Testa login com credenciais inválidas"""
        response = self.client.post(reverse('login_usuario'), {
            'email': 'test@example.com',
            'senha': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Email ou senha incorretos')

    def test_logout(self):
        """Testa logout"""
        self.client.login(username='test@example.com', password='testpass123')
        response = self.client.post(reverse('logout_usuario'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login_usuario'))


class CatalogoTests(TestCase):
    """Testes do catálogo de produtos"""

    def setUp(self):
        """Configuração inicial para testes"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123',
            tipo_cliente='pf'
        )
        self.categoria = Categoria.objects.create(
            nome='Eletrônicos',
            descricao='Produtos eletrônicos',
            ativa=True
        )
        self.produto = Produto.objects.create(
            categoria=self.categoria,
            nome='Produto Teste',
            descricao='Descrição do produto',
            preco=100.00,
            estoque=10,
            ativo=True
        )

    def test_catalogo_requires_authentication(self):
        """Verifica se catálogo requer autenticação"""
        response = self.client.get(reverse('catalogo_produtos'))
        self.assertEqual(response.status_code, 302)  # Redirecionamento para login

    def test_catalogo_accessible_authenticated(self):
        """Verifica se catálogo é acessível para usuário autenticado"""
        self.client.login(username='test@example.com', password='testpass123')
        response = self.client.get(reverse('catalogo_produtos'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalogo_produtos.html')

    def test_catalogo_filter_by_category(self):
        """Testa filtro de catálogo por categoria"""
        self.client.login(username='test@example.com', password='testpass123')
        response = self.client.get(reverse('catalogo_produtos'), {'categoria': self.categoria.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.produto.nome)

    def test_catalogo_search(self):
        """Testa busca no catálogo"""
        self.client.login(username='test@example.com', password='testpass123')
        response = self.client.get(reverse('catalogo_produtos'), {'busca': 'Produto'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.produto.nome)


class ModelTests(TestCase):
    """Testes dos modelos"""

    def test_categoria_creation(self):
        """Testa criação de categoria"""
        categoria = Categoria.objects.create(
            nome='Testes',
            descricao='Categoria de teste',
            ativa=True
        )
        self.assertEqual(str(categoria), 'Testes')
        self.assertTrue(categoria.ativa)

    def test_produto_creation(self):
        """Testa criação de produto"""
        categoria = Categoria.objects.create(
            nome='Testes',
            ativa=True
        )
        produto = Produto.objects.create(
            categoria=categoria,
            nome='Produto Teste',
            descricao='Teste',
            preco=50.00,
            estoque=5,
            ativo=True
        )
        self.assertEqual(str(produto), f'Produto Teste - {categoria.nome}')
        self.assertTrue(produto.tem_estoque())

    def test_produto_price_calculation(self):
        """Testa cálculo de preço com promoção"""
        categoria = Categoria.objects.create(nome='Teste', ativa=True)
        produto = Produto.objects.create(
            categoria=categoria,
            nome='Teste',
            descricao='Teste',
            preco=100.00,
            preco_promocional=80.00,
            estoque=1,
            ativo=True
        )
        self.assertEqual(produto.preco_final(), 80.00)
        self.assertEqual(produto.porcentagem_desconto(), 20)

    def test_user_creation(self):
        """Testa criação de usuário"""
        user = User.objects.create_user(
            username='test@test.com',
            email='test@test.com',
            password='password123',
            tipo_cliente='pf'
        )
        self.assertEqual(user.email, 'test@test.com')
        self.assertEqual(user.tipo_cliente, 'pf')
        self.assertTrue(user.check_password('password123'))
