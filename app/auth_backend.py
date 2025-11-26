import logging
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

logger = logging.getLogger(__name__)

User = get_user_model()


class EmailAuthenticationBackend(ModelBackend):
    """
    Autenticação customizada usando email ao invés de username.
    Permite login com email e senha.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Autentica usando email como username.
        """
        try:
            # Buscar usuário por email ou username
            user = User.objects.get(
                Q(email=username) | Q(username=username)
            )
        except User.DoesNotExist:
            logger.warning(f"Tentativa de login com email/usuário inválido: {username}")
            return None
        except User.MultipleObjectsReturned:
            logger.error(f"Múltiplos usuários encontrados para: {username}")
            return None

        # Verificar senha
        if user.check_password(password) and self.user_can_authenticate(user):
            logger.info(f"Login bem-sucedido para usuário: {user.email}")
            return user
        else:
            logger.warning(f"Falha de autenticação para: {username}")
            return None

    def get_user(self, user_id):
        """Recuperar usuário pelo ID"""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
