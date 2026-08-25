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
    defualt_error_message = "Business rule violation"

    def __init__ (self, detail = None):
        self.detail = detail or self.defualt_error_message

#400
class CityNotAllowedError(BusinessError):
    status_code = 400
    defualt_error_message = "The employee's city is not enabled for this contest"
#403
class PositionNotAllowedError(BusinessError):
    status_code = 403
    defualt_error_message = "Only employees with position Asesor can register"
#404
class EmployeeNotFoundError(BusinessError):
    status_code = 404
    defualt_error_message = "The specified employee does not exist"
class CategoryNotFoundError(BusinessError):
    status_code = 404
    defualt_error_message = "The specified category does not exist"
#409
class RegistrationsClosedError(BusinessError):
    status_code = 409
    defualt_error_message = "Registrations are alredy closed for this event"
class DuplicateRegistrationError(BusinessError):
    status_code = 409
    default_detail = 'This employee is already registered in this category.'
class CapacityExceededError(BusinessError):
    status_code = 409
    default_detail = 'No capacity available in this category.'

def business_exception_handler(exc, context):
    if isinstance(exc, BusinessError):
        return Response({'error': exc.detail}, status=exc.status_code)
    return exception_handler(exc, context)