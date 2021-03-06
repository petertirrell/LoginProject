from pyramid_beaker import session_factory_from_settings
from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    LogSession,
    Base,
    groupfinder
    )

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    LogSession.configure(bind=engine)
    Base.metadata.bind = engine
    authn_policy = AuthTktAuthenticationPolicy(
        'sosecret', callback=groupfinder, hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()
    
    my_session_factory = session_factory_from_settings(settings)
    config = Configurator(settings=settings,
                          root_factory='loginproject.models.RootFactory',
                          #session_factory=my_session_factory
                          )
    config.include('pyramid_beaker')
    config.set_session_factory(my_session_factory)

    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    config.add_request_method(models.get_user, 'user', reify=True)
    
    config.add_static_view('static', 'static', cache_max_age=3600)
    
    config.add_route('home', '/')
    config.add_route('protected', '/protected')

    config.add_route('login', '/login/{provider}')
    config.add_route('logout', '/logout')
    
    config.scan()
    return config.make_wsgi_app()
