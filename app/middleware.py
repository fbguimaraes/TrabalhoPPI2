import logging
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(MiddlewareMixin):
    """
    Middleware para tratamento global de erros e exceções.
    Registra erros e retorna páginas de erro apropriadas.
    """

    def process_exception(self, request, exception):
        """Processa exceções não capturadas"""
        
        # Log do erro
        logger.error(
            f"Erro não capturado em {request.path}",
            extra={
                'request_method': request.method,
                'user': request.user,
                'exception': str(exception),
            },
            exc_info=True
        )

        # Retornar página de erro apropriada
        if request.path.startswith('/api/'):
            # Para APIs, retornar JSON
            return JsonResponse({
                'error': 'Erro interno do servidor',
                'status': 500
            }, status=500)
        else:
            # Para HTML, retornar template
            return render(
                request,
                '500.html',
                {'error': str(exception)},
                status=500
            )


class SessionTimeoutMiddleware(MiddlewareMixin):
    """
    Middleware para timeout de sessão.
    Fecha a sessão após período de inatividade.
    """
    SESSION_TIMEOUT = 3600  # 1 hora em segundos

    def process_request(self, request):
        if request.user.is_authenticated:
            last_activity = request.session.get('last_activity')
            current_time = __import__('time').time()

            if last_activity:
                elapsed = current_time - last_activity
                if elapsed > self.SESSION_TIMEOUT:
                    # Sessão expirada
                    from django.contrib.auth import logout
                    logout(request)
                    logger.warning(
                        f"Sessão expirada para usuário {request.user}",
                        extra={'user': request.user}
                    )

            # Atualizar último acesso
            request.session['last_activity'] = current_time


class LoggingMiddleware(MiddlewareMixin):
    """
    Middleware para registrar requisições HTTP importantes.
    """

    def process_request(self, request):
        """Log de requisições POST (críticas)"""
        if request.method == 'POST':
            logger.info(
                f"POST request a {request.path}",
                extra={
                    'user': request.user,
                    'method': request.method,
                    'path': request.path,
                }
            )

    def process_response(self, request, response):
        """Log de respostas com erro"""
        if response.status_code >= 400:
            logger.warning(
                f"Resposta {response.status_code} em {request.path}",
                extra={
                    'status_code': response.status_code,
                    'path': request.path,
                    'user': request.user,
                }
            )
        return response
