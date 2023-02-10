# Copyright (c) 2023-present staciax
# Copyright (c) 2015-present Rapptz
# Licensed under the MIT license. Refer to the LICENSE file in the project root for more information.

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple, Union

if TYPE_CHECKING:
    from aiohttp import ClientResponse

__all__: Tuple[str, ...] = (
    'RiotAPIError',
    'HTTPException',
    'BadRequest',
    'Unauthorized',
    'Forbidden',
    'NotFound',
    'MethodNotAllowed',
    'UnsupportedMediaType',
    'RateLimited',
    'InternalServerError',
    # 'BadGateway',
    # 'ServiceUnavailable',
    # 'GatewayTimeout',
)


class RiotAPIError(Exception):
    """Base exception class for all errors raised by RiotAPI."""

    pass


class HTTPException(RiotAPIError):
    """Exception that is thrown for HTTP errors."""

    def __init__(self, response: ClientResponse, message: Optional[Union[Dict[str, Any], str]]) -> None:
        self.response: ClientResponse = response
        self.code: int
        self.text: str
        if isinstance(message, dict):
            self.code = message.get('code', 0)
            base = message.get('message', '')
            self.text = base
        else:
            self.text = message or ''
            self.code = 0

        fmt = '{0.status} {0.reason} (error code: {1})'
        if len(self.text):
            fmt += ': {2}'

        super().__init__(fmt.format(self.response, self.code, self.text))


class BadRequest(HTTPException):
    """Exception raised for 400 HTTP errors."""

    pass


class Unauthorized(HTTPException):
    """Exception raised for 401 HTTP errors."""

    pass


class Forbidden(HTTPException):
    """Exception raised for 403 HTTP errors."""

    pass


class NotFound(HTTPException):
    """Exception raised for 404 HTTP errors."""

    pass


class MethodNotAllowed(HTTPException):
    """Exception raised for 405 HTTP errors."""

    pass


class UnsupportedMediaType(HTTPException):
    """Exception raised for 415 HTTP errors."""

    pass


class RateLimited(HTTPException):
    """Exception raised for 429 HTTP errors."""

    def __init__(self, response: ClientResponse, message: Optional[Union[Dict[str, Any], str]]) -> None:
        super().__init__(response, message)
        self.retry_after: float = float(response.headers.get('Retry-After', 0))


class InternalServerError(HTTPException):
    """Exception raised for 500 HTTP errors."""

    pass


# class BadGateway(HTTPException):
#     """Exception raised for 502 HTTP errors."""
#     pass

# class ServiceUnavailable(HTTPException):
#     """Exception raised for 503 HTTP errors."""
#     pass

# class GatewayTimeout(HTTPException):
#     """Exception raised for 504 HTTP errors."""
#     pass
