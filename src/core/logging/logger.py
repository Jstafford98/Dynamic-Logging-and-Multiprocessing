from __future__ import annotations

import loguru
from contextlib import contextmanager
from typing import TYPE_CHECKING, ContextManager

if TYPE_CHECKING:
    from .handlers import _HandlerFactory, _HandlerId
    
__all__ = ['_LoggerManager']

class _LoggerManager:
    ''' 
        Manages a loguru.Logger object by providing various functionalities.
        The main use for this is using the logger in child processes, where 
        we want to dynamically add and remove a new logger Handler for each
        new call in the child process.
        
        The main core of this is designed around the example given in the loguru
        documentation:
        
        https://loguru.readthedocs.io/en/stable/resources/recipes.html#compatibility-with-multiprocessing-using-enqueue-argument
        
    '''
    
    _logger : loguru.Logger = None
    _handler_factory : _HandlerFactory = None
    
    @classmethod
    def set_logger(cls : _LoggerManager, logger : loguru.Logger) -> None :
        ''' 
            Sets the logger to use for all _LoggerManagers in the current process 
        '''
        cls._logger = logger
    
    @classmethod
    def set_handler_factory(cls : _LoggerManager, handler_factory : _HandlerFactory) -> None :
        ''' 
            Sets the handler_factory to use for all _LoggerManagers 
            in the current process.
            
            args:
                handler_factory : The _HandlerFactory object used to spawn new handlers
                                  for the loguru.Logger object. This will be used when
                                  spawning a context logger.
        '''
        cls._handler_factory = handler_factory
        
    @classmethod
    def reset(cls : _LoggerManager) -> None :
        ''' 
            Resets all class variables to None
        '''
        cls._logger = None
        cls._handler_factory = None
    
    @classmethod
    def get_logger(cls : _LoggerManager) -> loguru.Logger :
        return cls._logger
    
    @classmethod
    def ensure_build(cls : _LoggerManager) -> None :
        ''' 
            Ensures that the logger and handler_factory have been set 
            
            raises:
                ValueError if either _logger or _handler_factory are None
        '''
        
        if cls._logger is None:
            raise ValueError(
                "_LoggerManager._logger must be set using _LoggerManager.set_logger"\
                " before using _LoggerManager.context_logger"
            )
        
        if cls._handler_factory is None:
            raise ValueError(
                "_LoggerManager._handler_factory must be set using "\
                "_LoggerManager.set_handler_factory before using _LoggerManager._handler_factory"
            )
    
    @classmethod
    def remove_handler(cls : _LoggerManager, handler_id : _HandlerId) -> None :
        cls._logger.remove(handler_id = handler_id)
        
    @classmethod
    @contextmanager
    def context_logger(cls : _LoggerManager, **kwargs) -> ContextManager[loguru.Logger] : # type: ignore
        '''
            Contextually spawns a new logger handler using the _handler_factory
            which will remain added to the logger while in the context of the 
            function call.
            
            args:
                cls : _LoggerManager class
                **kwargs : keyword args to pass to the handler_factory
                
            returns:
                loguru.Logger instance
                
            raises:
                ValueError if either _logger or _handler_factory are None
        '''
        
        cls.ensure_build() # may raise ValueError
        
        handler_sink, handler_id = cls._handler_factory.new(
            logger = cls.get_logger(), **kwargs
        )
        
        try:
            yield cls.get_logger()
        finally:    
            cls.remove_handler(handler_id=handler_id)