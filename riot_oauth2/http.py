# Copyright (c) 2023-present staciax
# Copyright (c) 2015-present Rapptz
# Licensed under the MIT license. Refer to the LICENSE file in the project root for more information.

from __future__ import annotations

import asyncio
import logging
import re
from typing import TYPE_CHECKING, Any, ClassVar, Coroutine, Dict, Optional, Tuple, TypedDict, TypeVar, Union
from urllib.parse import quote as _uriquote, urlencode

import aiohttp

from . import utils
from .errors import (
    BadRequest,
    Forbidden,
    HTTPException,
    InternalServerError,
    MethodNotAllowed,
    NotFound,
    RateLimited,
    Unauthorized,
    UnsupportedMediaType,
)

if TYPE_CHECKING:
    T = TypeVar('T')
    Response = Coroutine[Any, Any, T]

__all__: Tuple[str, ...] = ('HTTPClient',)

_log = logging.getLogger(__name__)

MISSING = utils.MISSING


class TokenResponse(TypedDict):
    refresh_token: str
    id_token: str
    access_token: str


class AccountResponse(TypedDict):
    puuid: str
    gameName: str
    tagLine: str


# TODO: remove this func and make regex func for redirect_uri
def validate_redirect_url(url: Optional[str]) -> Optional[str]:
    if url is not None:
        if url.startswith('localhost'):
            return 'http://' + url
        match = re.match(r'https?://.+', url)
        if not match:
            raise ValueError(f'{url!r} must be a valid http or https url')
        return url
    return None


# HTTPClient, Route inspired by discord.py
# url: https://github.com/Rapptz/discord.py/blob/master/discord/http.py


class Route:

    """Represents an HTTP route."""

    PROVIDER: ClassVar[str] = 'https://auth.riotgames.com'

    def __init__(
        self,
        method: str,
        path: str,
        verify: bool = False,
        **parameters: Any,
    ) -> None:
        self.method = method
        self.path = path
        self.verify = verify
        self.parameters = parameters

        url = self.PROVIDER + self.path

        if parameters:
            url = url.format_map({k: _uriquote(v) if isinstance(v, str) else v for k, v in parameters.items()})

        self.url: str = url


class HTTPClient:

    """Represents an HTTP client for interacting with the Riot Auth API."""

    def __init__(self, loop: asyncio.AbstractEventLoop, client_id: str, client_secret: str, redirect_uri: str) -> None:
        self.loop: asyncio.AbstractEventLoop = loop
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = validate_redirect_url(redirect_uri)
        # self.scopes = scopes
        # self.state = state
        # self.proxy = proxy
        # self.proxy_auth = proxy_auth
        self._session: aiohttp.ClientSession = MISSING

    async def request(self, route: Route, **kwargs: Any) -> Any:
        method = route.method
        url = route.url
        headers = kwargs.pop('headers', {})
        kwargs['verify_ssl'] = route.verify

        response: Optional[aiohttp.ClientResponse] = None
        data: Optional[Union[Dict[str, Any], str]] = None

        for tries in range(5):
            try:
                async with self._session.request(
                    method, url, headers=headers, proxy=self.proxy, proxy_auth=self.proxy_auth, **kwargs
                ) as response:
                    _log.debug('%s %s with %s has returned %s', method, url, kwargs.get('data'), response.status)
                    data = await utils.json_or_text(response)
                    if 300 > response.status >= 200:
                        _log.debug('%s %s has received %s', method, url, data)
                        return data

                    if response.status == 429:
                        if not response.headers.get('Via') or isinstance(data, str):
                            # Banned by Cloudflare more than likely.
                            raise HTTPException(response, data)
                        # We are being rate limited
                        raise RateLimited(response, data)

                    if response.status == 400:
                        raise BadRequest(response, data)
                    elif response.status == 401:
                        raise Unauthorized(response, data)
                    elif response.status == 403:
                        raise Forbidden(response, data)
                    elif response.status == 404:
                        raise NotFound(response, data)
                    elif response.status == 405:
                        raise MethodNotAllowed(response, data)
                    elif response.status == 415:
                        raise UnsupportedMediaType(response, data)
                    elif response.status >= 500:
                        raise InternalServerError(response, data)

            except OSError as e:
                # Connection reset by peer
                if tries < 4 and e.errno in (54, 10054):
                    await asyncio.sleep(1 + tries * 2)
                    continue
                raise

        if response is not None:
            # We've run out of retries, raise.
            if response.status >= 500:
                raise InternalServerError(response, data)

            raise HTTPException(response, data)

        raise RuntimeError('Unreachable code in HTTP handling')

    async def close(self) -> None:
        if self._session is not MISSING:
            await self._session.close()

    async def start(self) -> None:
        self._session = aiohttp.ClientSession()

    def clear(self) -> None:
        if self._session and self._session.closed:
            self._session = MISSING

    def get_oauth_url(self) -> str:
        url = Route.PROVIDER
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'scope': 'openid',  # TODO: scope from config
        }
        return url + '?' + urlencode(params)

    def get_oauth2_token(self, code: str) -> Response[TokenResponse]:
        auth = aiohttp.BasicAuth(
            login=self.client_id,
            password=self.client_secret,
        )
        payload = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri,
        }
        return self.request(Route('POST', '/token'), data=payload, auth=auth)

    def get_account(self, access_token: str) -> Response[AccountResponse]:
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {access_token}'}
        r = Route('GET', '/riot/account/v1/accounts/me')
        return self.request(r, headers=headers)

    # def get_user(self, access_token: str) -> Response[...]:
    #     headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {access_token}'}
    #     return self.request(Route('GET', 'userinfo'), headers=headers)
