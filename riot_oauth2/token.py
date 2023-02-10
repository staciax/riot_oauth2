# Copyright (c) 2023-present staciax
# Licensed under the MIT license. Refer to the LICENSE file in the project root for more information.

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from typing_extensions import Self

    from .client import Client
    from .http import TokenResponse as TokenPayload

# fmt: off
__all__: Tuple[str, ...] = (
    'Token',
)
# fmt: on


class Token:
    if TYPE_CHECKING:
        refresh_token: str
        id_token: str
        access_token: str
        # expires_at: datetime.datetime

    def __init__(self, client: Client, data: TokenPayload) -> None:
        self._client = client
        self._update(data)

    def _update(self, data: TokenPayload) -> None:
        self.refresh_token = data['refresh_token']
        self.id_token = data['id_token']
        self.access_token = data['access_token']
        self.expires_at = datetime.datetime.now() + datetime.timedelta(seconds=3600)
        # import jwt
        # decoded = jwt.decode(self.id_token, verify=False)
        # self.expires_at = datetime.datetime.fromtimestamp(decoded['exp'])

    async def refresh(self, force: bool = False) -> Self:
        if self.is_expired() or force:
            data = await self._client._http.refresh_token(self.refresh_token)
            self._update(data)
        return self

    def is_expired(self) -> bool:
        return datetime.datetime.now() > self.expires_at
