# Copyright (c) 2023-present staciax
# Licensed under the MIT license. Refer to the LICENSE file in the project root for more information.

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .token import Token

if TYPE_CHECKING:
    from .client import Client
    from .http import AccountResponse as AccountPayload


class Account:
    if TYPE_CHECKING:
        puuid: str
        game_name: str
        tag_line: str
        _token: Token

    def __init__(self, client: Client, data: AccountPayload) -> None:
        self._client = client
        self._update(data)

    def __repr__(self) -> str:
        return '<Account puuid={0.puuid!r} game_name={0.game_name!r} tag_line={0.tag_line!r}>'

    def __str__(self) -> str:
        return self.display_name

    def _update(self, data: AccountPayload) -> None:
        self.puuid = data['puuid']
        self.game_name = data['gameName']
        self.tag_line = data['tagLine']

    def set_token(self, token: Token) -> None:
        self._token = token

    @property
    def display_name(self) -> str:
        return f'{self.game_name}#{self.tag_line}'
