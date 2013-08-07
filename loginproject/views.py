from pyramid.response import Response
#from pyramid.request import Request
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
    unauthenticated_userid
    )

from .security import USERS
#endregion

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    User,
    UserProfile
    )

import logging
import datetime

from authomatic import Authomatic
from authomatic.adapters import WebObAdapter

from config import CONFIG

authomatic = Authomatic(config=CONFIG, secret='some random secret string')


log = logging.getLogger(__name__)

#@view_config(route_name='home', permission='view')
@view_config(route_name='home', renderer='home.mako', permission='view')
def home(request):
    # return Response('''
    #     Login with <a href="login/facebook">Facebook</a>.<br />
    #     Login with <a href="login/twitter">Twitter</a>.<br />
    #     <form action="login/oi">
    #         <input type="text" name="id" value="me.yahoo.com" />
    #         <input type="submit" value="Authenticate With OpenID">
    #     </form>
    # ''')

    return {
        'logged_in': authenticated_userid(request),
        'user': request.user
    }


@view_config(route_name='protected', renderer='protected.mako', permission='edit')
def viewProtected(request):

    return dict(
        one='foo',
        two='bar',
        logged_in = authenticated_userid(request)
        )

#@view_config(route_name='login', renderer='login.mako')
#@forbidden_view_config(renderer='login.mako')
@view_config(route_name='login')
def login(request):
    response = Response()
    # get provider
    provider = request.matchdict.get('provider')

    result = authomatic.login(WebObAdapter(request, response),provider)

    # Do not write anything to the response if there is no result!
    if result:
        # If there is result, the login procedure is over and we can write to response.
        #response.write('<a href="..">Home</a>')
        
        if result.error:
            log.error(result.error.message)
            # Login procedure finished with an error.
            response.write('<h2>Damn that error: {}</h2>'.format(result.error.message))
            #print result.error.message
        
        elif result.user:
            # Hooray, we have the user!
            
            # OAuth 2.0 and OAuth 1.0a provide only limited user data on login,
            # We need to update the user to get more info.
            if not (result.user.name and result.user.id):
                result.user.update()

            # check is user already exists, if not, then add
            thisuser = None
            try:
                thisuser = DBSession.query(User).filter(User.providerid == result.user.id)\
                    .filter(User.provider == provider).first()
                if not thisuser:
                    NewUser = User(result.user.id, provider, result.user.credentials.serialize())
                    
                    DBSession.add(NewUser)
                    DBSession.flush()
                    # default profile name is whatever the provider display name is
                    NewProfile = UserProfile(NewUser.id)
                    NewProfile.displayname = result.user.name
                    NewProfile.last_login = datetime.datetime.utcnow()
                    DBSession.add(NewProfile)
                    DBSession.flush()

                    thisuser = DBSession.query(User).filter(User.providerid == result.user.id)\
                        .filter(User.provider == provider).first()

                    # redirect to fill out userprofile?  
                else:
                    thisuser.last_login = datetime.datetime.utcnow()
                    DBSession.add(thisuser)
                    DBSession.flush()          
            except DBAPIError as e:
                log.error(e.message)


            login_url = request.route_url('login', provider=provider)
            referrer = request.url
            if referrer == login_url:
                referrer = request.route_url('home') # never use the login form itself as came_from
            came_from = request.params.get('came_from', referrer)
            headers = remember(request, thisuser.id)
            
            return HTTPFound(location = request.route_url('home'), headers = headers)
            
            # Welcome the user.
            response.write('<h1>Hi {}</h1>'.format(result.user.name))
            response.write('<h2>Your id is: {}</h2>'.format(result.user.id))
            response.write('<h2>Your email is: {}</h2>'.format(result.user.email))
            
            # Seems like we're done, but there's more we can do...


            
            # If there are credentials (only by AuthorizationProvider),
            # we can _access user's protected resources.
            if result.user.credentials:
                
                # Each provider has it's specific API.
                if result.provider.name == 'fb':
                    response.write('Your are logged in with Facebook.<br />')
                    
                    # We will access the user's 5 most recent statuses.
                    url = 'https://graph.facebook.com/{}?fields=feed.limit(5)'
                    url = url.format(result.user.id)
                    
                    # Access user's protected resource.
                    access_response = result.provider.access(url)
                    
                    if access_response.status == 200:
                        # Parse response.
                        statuses = access_response.data.get('feed').get('data')
                        error = access_response.data.get('error')
                        
                        if error:
                            response.write('Damn that error: {}!'.format(error))
                        elif statuses:
                            response.write('Your 5 most recent statuses:<br />')
                            for message in statuses:
                                
                                text = message.get('message')
                                date = message.get('created_time')
                                
                                response.write('<h3>{}</h3>'.format(text))
                                response.write('Posted on: {}'.format(date))
                    else:
                        response.write('Damn that unknown error!<br />')
                        response.write('Status: {}'.format(response.status))
                    
                if result.provider.name == 'tw':
                    response.write('Your are logged in with Twitter.<br />')
                    
                    # We will get the user's 5 most recent tweets.
                    url = 'https://api.twitter.com/1.1/statuses/user_timeline.json'
                    
                    # You can pass a dictionary of querystring parameters.
                    access_response = result.provider.access(url, {'count': 5})
                                            
                    # Parse response.
                    if access_response.status == 200:
                        if type(access_response.data) is list:
                            # Twitter returns the tweets as a JSON list.
                            response.write('Your 5 most recent tweets:')
                            for tweet in access_response.data:
                                text = tweet.get('text')
                                date = tweet.get('created_at')
                                
                                response.write('<h3>{}</h3>'.format(text.replace(u'\u2026', '...')))
                                response.write('Tweeted on: {}'.format(date))
                                
                        elif access_response.data.get('errors'):
                            response.write('Damn that error: {}!'.\
                                                format(response.data.get('errors')))
                    else:
                        response.write('Damn that unknown error!<br />')
                        response.write('Status: {}'.format(response.status))

    return response

@view_config(route_name='logout')
def logout(request):
    headers = forget(request)    
    return HTTPFound(location = request.route_url('home'),
                     headers = headers)

