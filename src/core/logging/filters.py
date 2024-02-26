from __future__ import annotations

import loguru

__all__ = ['_LoggerFilter']

class _LoggerFilter:
    ''' 
        Callable filter object, compliant with loguru.FilterFunction 
        which will be used to only log messages using loguru which also 
        pass an additional logger_id parameter
    '''
    
    def __init__(self, logger_id : int) -> None :
        '''
            args:
                logger_id : an integer value which a record must contain 
                            for it to be logged to a specific file
        '''
        self.logger_id = logger_id
        
    def __call__(self, record : loguru.Record) -> bool :
        ''' 
            Returns true if the record contains self.logger_id 

            args:
                record : loguru.Record object associated with a log entry
        '''
        
        extra = record['extra']
        
        try:
            return extra['logger_id'] == self.logger_id
        except KeyError as e:
            return False