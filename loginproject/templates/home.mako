# -*- coding: utf-8 -*-
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" xmlns:tal="http://xml.zope.org/namespaces/tal">
<head>
  <title>My HTML Title</title>
  <meta http-equiv="Content-Type" content="text/html;charset=UTF-8"/>
  <meta name="keywords" content="python web application" />
  <meta name="description" content="pyramid web application" />
</head>
<body>
  <div id="header">
   % if logged_in == None:
   <a href="${request.application_url}/login/google"><img src="${request.static_url('loginproject:static/provider_google.png')}"
    alt="Login with Google" title="Login with Google"></a><br>
    <a href="${request.application_url}/login/facebook"><img src="${request.static_url('loginproject:static/provider_facebook.png')}"
    alt="Login with Facebook" title="Login with Facebook"></a><br>
    <a href="${request.application_url}/login/twitter"><img src="${request.static_url('loginproject:static/provider_twitter.png')}"
    alt="Login with Twitter" title="Login with Twitter"></a><br>
    % else:
    Logged in as ${user.profile.displayname} |
    <a href="${request.application_url}/logout">Logout</a>
    My user: ${user.profile.displayname}
    % endif
  </div>
  <div id="main-content">
    This is my content
  </div>
  <div id="footer">
    <div class="footer">&copy; Copyright 2008-2012, Agendaless Consulting.</div>
  </div>
</body>
</html>
