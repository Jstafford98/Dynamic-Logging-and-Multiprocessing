from __future__ import annotations

import multiprocessing
from concurrent.futures import wait
from abc import ABC, abstractmethod
from typing import Any, NamedTuple, Self
from pebble import ProcessPool, ProcessFuture
from concurrent.futures._base import DoneAndNotDoneFutures

from .future import _ProcessFutureManager

__all__ = [
    'SubprocessBuilder', 'DispatchableArgumentSet', 'DispatchableJobs',
    'SubprocessDispatcher', '_ProcessFutureManager'
]

class SubprocessBuilder(ABC):
    
    @classmethod
    @abstractmethod
    def build_in_subprocess(cls : SubprocessBuilder, *args, **kwargs) -> None :
        '''
            This function should be used to initialize the class in a child
            process
        '''
        raise NotImplementedError()
    
    @classmethod
    @abstractmethod
    def run_in_subprocess(cls : SubprocessBuilder, *args, **kwargs) -> Any :
        raise NotImplementedError()

class DispatchableArgumentSet(NamedTuple):
    
    args : list = []
    kwargs : dict = dict()
    timeout : float | None = None

class DispatchableJobs(NamedTuple):
    
    jobs : list[DispatchableArgumentSet] = []
    
    @staticmethod
    def spawn_dummies(n_dummies : int) -> DispatchableJobs :
        arg_sets = [DispatchableArgumentSet() for _ in range(n_dummies)]
        return DispatchableJobs(jobs=arg_sets)
        
class SubprocessDispatcher(ProcessPool):
    
    def __init__(
        self, 
        builder : SubprocessBuilder, 
        init_args : tuple[Any] = None,
        n_jobs : int = multiprocessing.cpu_count(),
        **pool_kwargs
    ) -> None :
        
        self.builder = builder
        self.future_manager = _ProcessFutureManager()
        
        super().__init__(
            max_workers=n_jobs, 
            initargs=init_args,
            initializer=builder.build_in_subprocess, 
            **pool_kwargs
        )
    
    def dispatch(self, job : DispatchableArgumentSet) -> None :
        
        future = self.schedule(
            function = self.builder.run_in_subprocess,
            args = job.args,
            kwargs = job.kwargs,
            timeout = job.timeout
        )
        
        self.future_manager.add_future(future)
        
    def dispatch_many(self, jobs : DispatchableJobs) -> None :
        for job in jobs.jobs:
            self.dispatch(job=job)

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
        self.future_manager.wait(timeout=timeout, return_when=return_when)
    
    @property
    def completed(self) -> list[ProcessFuture] :
        ''' Get all completed futures '''
        return self.future_manager.completed    
    
    @property
    def incomplete(self) -> list[ProcessFuture] :
        ''' Get all incomplete futures '''
        return self.future_manager.incomplete
    
    @property
    def results(self) -> list[Any] :
        ''' Get the results of all completed futures'''
        return self.future_manager.results
       
    def __exit__(self, *args) -> None :
        self.future_manager.clear()
        
        ''' 
            I've found the __enter__/__exit__ code for the ProcessPool and can 
            verify all this does is call self.close() and self.join(), so this
            implementation should be no issue.
            
            https://github.com/noxdafox/pebble/blob/master/pebble/pool/base_pool.py
            
        '''
        super().__exit__(*args)
        
        