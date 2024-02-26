from __future__ import annotations

import loguru
from typing import TypeAlias
from abc import ABC, abstractmethod


__all__ = ['_HandlerFactory', '_HandlerId', '_HandlerSink']

_HandlerId : TypeAlias = int
_HandlerSink : TypeAlias = str

class _HandlerFactory(ABC):
    
    @abstractmethod
    def new(self, logger : loguru.Logger) -> tuple[_HandlerSink, _HandlerId] :
        raise NotImplementedError()