from urllib.parse import parse_qs
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token
from django.db import close_old_connections
from channels.db import database_sync_to_async

from channels.middleware import BaseMiddleware

class TokenAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope["query_string"].decode()
        query_params = parse_qs(query_string)
        token_key = query_params.get("token")
        scope["user"] = AnonymousUser()

        if token_key:
            try:
                user = await self.get_user_from_db(token_key[0])
                scope["user"] = user
            except Token.DoesNotExist:
                pass

        close_old_connections()

        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user_from_db(self, token_key):
        token = Token.objects.select_related('user').get(key=token_key)
        return token.user
