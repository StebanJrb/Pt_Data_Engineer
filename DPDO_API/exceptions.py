from rest_framework.views import exception_handler
from rest_framework.response import Response

class BusinessError(Exception):
    """ All Business errors belongs to 400 status code,
    but each error has different status error, this is the base class for those
    exeptions

    Args:
        Exception (_type_): _description_
    """
    status_code = 400
    defualt_error_message = 'Business rule violation'

    def __init__ (self, detail = None):
        self.detail = detail or self.defualt_error_message

""" 
HTTP REsponeses Maped:
400: Bad Request: For bad sintaxis or invalid data
403: Forbiden: for users without permissions
404: Not Found: Not founded
409: Conflict: Try to create user alredy registrated
"""
