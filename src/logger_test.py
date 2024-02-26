'''
    Concrete usage of the logging functionality defined in this repository 
    to enable dynamic logging for our simple power function
'''

from __future__ import annotations

import os
import loguru
from pathlib import Path

from .core.multiprocessing import SubprocessBuilder

from .core.logging import (
    _LoggerManager, _HandlerFactory, _HandlerId, _HandlerSink, _LoggerFilter
)

__all__ = ['Exponential']

class _PowerFilter(_LoggerFilter):
    ''' 
        _LoggerFilter that only logs entries which have an associated logger_id 
        of "POWER"
    '''
    
    def __init__(self) -> None :
        super().__init__(logger_id='POWER')
        
class _PowerHandlerFactory(_HandlerFactory):
    ''' 
        Creates logger handlers which write to files in a single directory dynamically
        based on the provided filename in when the "new" function is called
    '''
    
    def __init__(self, sink_directory : Path) -> None :
        '''
            args:
                sink_directory : directory to write log files to
                
            raises:
                ValueError if sink_directory is not an existing directory
        '''
        self.sink_directory = sink_directory
        
        if not self.sink_directory.is_dir():
            raise ValueError(
                f"provided sink directory {sink_directory} either does not "\
                f"exist or isn't a directory."
            )
        
    def new_sink(self, filename : Path | str) -> Path :
        ''' 
            Creates a new log sink in the sink_directory
            
            args:
                filename : name to give the log file
        '''
        return self.sink_directory / filename
          
    def new(self, logger : loguru.Logger, filename : str | Path) -> tuple[_HandlerSink, _HandlerId] :
        ''' 
            Spawns a new logger handler which writes to a file named
            filename in the sink_directory. Only records who have a 
            logger_id of "POWER" will be written to that file.
            
            args:
                filename : name to give the log file in sink_directory
                
        '''
        
        sink = self.new_sink(filename=filename)
        
        handler_id = logger.add(
            sink = sink,
            mode='w',
            enqueue = True, # neccessary so logging can be done in parallel
            filter = _PowerFilter()
        ) 
        
        return sink, handler_id

class Exponential(SubprocessBuilder):
    
    _power = 2
    
    @classmethod
    def set_power(cls : Exponential, power : int) -> None :
        
        if not isinstance(power, int):
            raise ValueError("power must be an integer.")
        
        cls._power = power
    
    @classmethod
    def get_power(cls : Exponential) -> int :
        return cls._power
    
    @classmethod
    def build_in_subprocess(
        cls : Exponential,
        logger : loguru.Logger, 
        sink_directory : Path,
        power : int = None
    ) -> None :
        '''
            Configures the _PowerHandlerFactory and _LoggerManager in each child
            process for their use in "power"
        '''
        
        handler_factory = _PowerHandlerFactory(sink_directory=sink_directory)
        
        _LoggerManager.set_logger(logger)
        _LoggerManager.set_handler_factory(handler_factory)
        
        if power is not None:
            cls.set_power(power)
    
    @classmethod
    def run_in_subprocess(cls : Exponential, value : int) -> int :
        return cls.calculate(value)
    
    @classmethod
    def calculate(cls : Exponential, value : int) -> int :
        
        with _LoggerManager.context_logger(filename = f'{value}.log') as logger:
            
            with logger.contextualize(logger_id='POWER'):
                
                logger.info(f"SOF in process {os.getpid()}")
                
                ans = value**cls.get_power()
            
                logger.info(f"{value}**{cls.get_power()} = {ans}")
                
                logger.info("EOF")
            
                return f"{value}**{cls.get_power()} = {ans}"