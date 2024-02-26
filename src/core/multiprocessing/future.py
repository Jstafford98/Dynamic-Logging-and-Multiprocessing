from typing import Any, Self
from pebble import ProcessFuture
from concurrent.futures import wait
from concurrent.futures._base import DoneAndNotDoneFutures

__all__ = ['_ProcessFutureManager']

class _ProcessFutureManager:
    ''' 
        Manages futures created when using a ProcessPool and abstracts it away
        to clean up the code and make it a little easier to read.
    '''
    
    def __init__(self) -> None :
        self.futures = []
        self.done_not_done : DoneAndNotDoneFutures = None
        
    def add_future(self, future : ProcessFuture) -> None :
        self.futures.append(future)
    
    def clear(self) -> None :
        ''' 
            Clears all futures managed by the class instance and all data 
            associated with them 
        '''
        self.futures.clear()
        self.done_not_done = None
        
    def wait(
        self, 
        timeout : float | None = None, 
        return_when : str = 'ALL_COMPLETED'
    ) -> None :
        ''' 
            Wait for all futures added with "add_future" to complete 
            args:
                timeout : Maximum number of seconds to wait for futures to complete
                return_when : indicates when the function should return.
        '''
        
        self.done_not_done = wait(
            fs=self.futures, timeout=timeout, return_when=return_when
        )
    
    @property
    def completed(self) -> list[ProcessFuture] :
        ''' Get all completed futures '''
        return self.done_not_done.done
    
    @property
    def incomplete(self) -> list[ProcessFuture] :
        ''' Get all incomplete futures '''
        return self.done_not_done.not_done
    
    @property
    def results(self) -> list[Any] :
        ''' Get the results of all completed futures'''
        return [future.result() for future in self.completed]
    
    def __enter__(self) -> Self :
        return self
    
    def __exit__(self, *args) -> None :
        self.clear()