from fastapi import Request, status, exceptions as fastapi_exc
from fastapi.responses import JSONResponse
from jsonschema import exceptions as jsonschema_exc
from bson import errors as bson_exc
import logging

from src.watsh.lib import exceptions

def create_error_response(status_code: int, message: str) -> JSONResponse:
    """
    Create a standardized JSON response for error messages.
    """
    return JSONResponse(
        status_code=status_code,
        content=message
    )

async def handler_400(request: Request, exc: Exception) -> JSONResponse:
    logging.warning(str(exc))
    return create_error_response(status.HTTP_400_BAD_REQUEST, str(exc))

async def handler_403(request: Request, exc: Exception) -> JSONResponse:
    return create_error_response(status.HTTP_403_FORBIDDEN, str(exc))

async def handler_404(request: Request, exc: Exception) -> JSONResponse:
    return create_error_response(status.HTTP_404_NOT_FOUND, str(exc))


async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Override the default handler for HTTP 404 Not Found.
    """
    # Optionally include the requested path in the response
    message = f"Endpoint '{request.url.path}' not found."
    return create_error_response(status.HTTP_404_NOT_FOUND, message)

async def validation_exception_handler(request: Request, exc: fastapi_exc.RequestValidationError) -> JSONResponse:
    """
    Override the default handler for HTTP 422 Unprocessable Entity.
    """
    message = exc.errors()[0]['loc'][0] + ': ' + exc.errors()[0]['msg']
    return create_error_response(status.HTTP_422_UNPROCESSABLE_ENTITY, message)

async def http_exception_handler(request: Request, exc: fastapi_exc.HTTPException) -> JSONResponse:
    return create_error_response(exc.status_code, exc.detail)

async def wrong_id_handler(request: Request, exc: bson_exc.InvalidId) -> JSONResponse:
    return create_error_response(status.HTTP_400_BAD_REQUEST, 'Invalid ID.')

async def invalid_json_handler(request: Request, exc: jsonschema_exc.ValidationError) -> JSONResponse:
    return create_error_response(status.HTTP_400_BAD_REQUEST, exc.message)


exception_handlers = {
    
    exceptions.UnauthorizedException: handler_403,
    exceptions.BadRequest: handler_400,

    exceptions.ProjetNotFound: handler_404,
    exceptions.ProjectSlugTaken: handler_400,
    
    exceptions.EnvironmentNotFound: handler_404,
    exceptions.EnvironmentSlugTaken: handler_400,
    
    exceptions.BranchSlugTaken: handler_400,
    exceptions.BranchNotFound: handler_404,

    exceptions.CommitNotFound: handler_404,

    exceptions.MemberAlreadyExist: handler_400,
    exceptions.MemberNotFound: handler_404,

    exceptions.UserNotFound: handler_404,

    exceptions.EmailAlreadyTaken: handler_400,

    exceptions.ItemNotFound: handler_404,

    exceptions.JSONSchemaError: handler_400,

    404: not_found_handler,

    bson_exc.InvalidId: wrong_id_handler,
    jsonschema_exc.ValidationError: invalid_json_handler,

    fastapi_exc.HTTPException: http_exception_handler,
    fastapi_exc.RequestValidationError: validation_exception_handler,
}