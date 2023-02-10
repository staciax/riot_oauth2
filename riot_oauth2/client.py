# Copyright (c) 2023-present staciax
# Licensed under the MIT license. Refer to the LICENSE file in the project root for more information.

import asyncio
from typing import Any, Optional, Tuple

from .account import Account
from .http import HTTPClient
from .token import Token

# fmt: off
__all__: Tuple[str, ...] = (
    'Client',
)
# fmt: on


# -- from discord.py
# link: https://github.com/Rapptz/discord.py/blob/9ea6ee8887b65f21ccc0bcf013786f4ea61ba608/discord/client.py#L111
class _LoopSentinel:
    __slots__ = ()

    def __getattr__(self, attr: str) -> None:
        msg = (
            'loop attribute cannot be accessed in non-async contexts. '
            'Consider using either an asynchronous main function and passing it to asyncio.run or '
        )
        raise AttributeError(msg)


_loop: Any = _LoopSentinel()

# --


class Client:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str) -> None:
        self.client_id = client_id
        self._client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.loop: asyncio.AbstractEventLoop = _loop
        self._http: HTTPClient = HTTPClient(self)

    @property
    def application_id(self) -> str:
        return self.client_id

    def get_oauth_url(self) -> str:
        return self._http.get_oauth_url()

    async def authorization(self, code: str) -> Token:
        data = await self._http.get_oauth2_token(code)
        return Token(client=self, data=data)

    async def fetch_account(self, token: Token) -> Optional[Account]:
        if token.is_expired():
            await token.refresh()

        data = await self._http.get_account(token.access_token)
        if data is not None:
            acc = Account(self, data)
            acc.set_token(token)
            return acc
        return None
