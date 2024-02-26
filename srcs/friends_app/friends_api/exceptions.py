from rest_framework.exceptions import APIException

'''
    This exception is raised in response to a bad API request.

    To customize the message sent to the user, provide the `detail` parameter to the constructor.
    Example:
        raise BadRequest(detail='first_id is required')
    Args:
        detail (str, optional): A detailed message specifying the issue with the API request.
'''
class BadRequest(APIException):
    status_code = 400
    default_detail = 'bad request'
    default_code = 'bad_request'

'''
    This exception is raised in response to an object not found.

    To customize the message sent to the user, provide the `detail` parameter to the constructor.
    Example:
        raise NotFound(detail='object not found with id `333`')
    Args:
        detail (str, optional): A detailed message specifying that the object was not found.
'''
class NotFound(APIException):
    status_code = 404
    default_detail = 'not found'
    default_code = 'not_found'