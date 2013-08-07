from pyramid.view import (
    view_config,
    forbidden_view_config,
    notfound_view_config
    )

from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    HTTPForbidden,
    HTTPBadRequest,
    HTTPInternalServerError
    )

import transaction
import traceback
import logging

log = logging.getLogger(__name__)

#region Custom HTTP Errors and Exceptions
@view_config(context=HTTPNotFound, renderer='HTTPNotFound.mako')
def notfound(request):
    if not 'favicon' in str(request.url):
        log.error('404 not found: {0}'.format(str(request.url)))
        request.response.status_int = 404
    return {}

@view_config(context=HTTPInternalServerError, renderer='HTTPInternalServerError.mako')
def internalerror(request):
    log.error('HTTPInternalServerError: {0}'.format(str(request.url)))
    request.response.status_int = 500
    return {}

@view_config(context=Exception, renderer="HTTPExceptionCaught.mako")
def error_view(exc, request):
    log.error('HTTPException: {0}'.format(str(request.url)))
    log.error(str(exc.message))
    log.error(traceback.format_exc(exc))

    return {}
#endregion