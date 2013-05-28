
'''

Define a well-known exception that the user-interface is primed to handle. 

The error-handling strategy in this app is simple:
- Trap and log all predictable exception situation (E.g. FileIOError)
- Trap and log all other Exceptions
- Then re-raise as AppError with a more suitable message
- Bubble AppError up to the view and submit back to the user interface.

NB :
- In this app, all entry point functions in each module will do this exception 
  handling, even if there are no obvious exceptions to catch.

'''

class AppError (Exception):
    pass
