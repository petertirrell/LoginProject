from pyramid.response import Response
from pyramid.request import Request
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    )
#region login stuff
from pyramid.view import (
    view_config,
    forbidden_view_config,
    )

from pyramid.security import (
    remember,
    forget,
    authenticated_userid,
    )

from .security import USERS
#endregion

from sqlalchemy.exc import DBAPIError

from authomatic import Authomatic

from config import CONFIG

from .models import (
    DBSession,
    MyModel,
    )


from authomatic import Authomatic
from authomatic.adapters import PyramidAdapter

from config import CONFIG

authomatic = Authomatic(config=CONFIG, secret='my new secret string')

@view_config(route_name='home', renderer='home.mako', permission='view')
def my_view(request):
    #try:
    #    one = DBSession.query(MyModel).filter(MyModel.name == 'one').first()
    #except DBAPIError:
    #    return Response(conn_err_msg, content_type='text/plain', status_int=500)
    #return {'one': one, 'project': 'LoginProject'}
    return dict(
        one='foo',
        two='bar',
        logged_in = authenticated_userid(request)
        )


@view_config(route_name='protected', renderer='protected.mako', permission='edit')
def viewProtected(request):

    return dict(
        one='foo',
        two='bar',
        logged_in = authenticated_userid(request)
        )

@view_config(route_name='login', renderer='login.mako')
@forbidden_view_config(renderer='login.mako')
def login(request):
    # get provider
    provider = request.matchdict.get('provider')
    print provider

    login_url = request.route_url('login', provider=provider)
    referrer = request.url
    if referrer == login_url:
        referrer = '/' # never use the login form itself as came_from
    came_from = request.params.get('came_from', referrer)

    if 'token_secret' in request.session:
        print 'secret: ' + request.session['token_secret']
    
    result = authomatic.login(PyramidAdapter(request),provider)

    if result:
            print 'We have a result!'
            print result
            if result.error:
                print 'Error! ' + result.error.message
            elif result.user:
                if not (result.user.name and result.user.id):
                    print 'trying to update user'
                    result.user.update()
                print result
                print result.user.name
    
                headers = remember(request, result)
                return HTTPFound(location = came_from,
                                         headers = headers)

    print 'something went wrong, bailing and just pulling the login page'
    
    '''if 'form.submitted' in request.params:
        login = request.params['login']
        password = request.params['password']
        if USERS.get(login) == password:
            headers = remember(request, login)
            return HTTPFound(location = came_from,
                             headers = headers)
        message = 'Failed login'
        '''

    return dict(
        message = 'foo',
        url = request.application_url + '/login/twitter',
        came_from = came_from        
        )

@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(location = request.route_url('home'),
                     headers = headers)

