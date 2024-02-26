''' 
    This is a demonstration of dynamically creating loggers in child processes,
    where each function call scheduled using a pebble.ProcessPool has it's own
    logger and the log file naming follows a standard convention.
    
    In this case, we're simply having Python calculate a value, x, raised to 
    the second power. While this is something you'd almost never use concurrency
    for, I wanted to keep it simple so the focus could be on the dynamic logging.
'''

from pathlib import Path
from loguru import logger

from .logger_test import Exponential
from .core.multiprocessing import (
    SubprocessDispatcher, DispatchableJobs, DispatchableArgumentSet
)

def run(n : int) -> None :
    
    logger.remove()
    
    sink_directory = Path('../logs') # this is where all log files will be written
    sink_directory.mkdir(exist_ok=True)

    jobs = []
    
    for value in range(n):
        jobs.append(
            DispatchableArgumentSet(kwargs = {'value' : value})
        )
    
    jobs = DispatchableJobs(jobs=jobs)
    
    dispatcher = SubprocessDispatcher(
        builder = Exponential,
        init_args = (
            logger,
            sink_directory,
            3
        )
    )
    
    with dispatcher:
        
        dispatcher.dispatch_many(jobs=jobs)
        dispatcher.wait()
        
        for result in dispatcher.results:
            print(result)
        
    
# def run(n : int) -> None :
#     ''' 
#         Calculates the second power (x**2) for each integer x in range(n)
#     '''
    
#     logger.remove() # remove the sys.stdout logger as it breaks the ProcessPool
    
#     ''' 
#         This isn't super important, it's just a small wrapper I like to use 
#         for managing futures returned from the ProcessPool 
#     '''
#     future_manager = _ProcessFutureManager()
    
#     executor = ProcessPool(
#         initializer = Exponential.build_in_child_process, initargs = (logger, LOG_DIR, 3)
#     )
    
#     ''' Again, the use of ExitStack isn't important here. '''
#     with ExitStack() as stack:
        
#         stack.enter_context(executor)
#         stack.enter_context(future_manager)

#         for i in range(n):
#             ''' 
#                 Calculate the power of every integer from 0 to n-1 in child 
#                 processes and log the results 
#             '''
#             future = executor.schedule(function=Exponential.run_in_subprocess, args=(i,))
#             future_manager.add_future(future)
        
#         future_manager.wait()
        
if __name__ == '__main__':
    run(n = 10)