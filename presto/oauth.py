import urllib
from oauthlib.oauth1.rfc5849 import SIGNATURE_TYPE_QUERY, Client
import httplib2
import urlparse


def get_request_token(public_key, secret_key, url, method=u'POST'):
    '''
    
    :param public_key:
    :param secret_key:
    :param url:
    :param method:
    '''
    c = Client(
            unicode(public_key),
            unicode(secret_key), 
            signature_type=SIGNATURE_TYPE_QUERY
    )
    uri, headers, body = c.sign(
            uri=url, 
            http_method=method)
    http = httplib2.Http()

    response, content = httplib2.Http.request(http, uri, 
            method=method, 
            body=body,
            headers=headers
    )

    if response.get('status') != '200':
        raise Exception("Invalid request token response: %s." % content)

    tokens = dict(urlparse.parse_qsl(content))
    token = tokens.get('oauth_token')
    token_secret = tokens.get('oauth_token_secret')
    return unicode(token), unicode(token_secret)


def build_authorize_url(auth_url, oauth_token, callback_url=None):
    '''
    Returns authentication URL to be used in a browser

    :param callback_url:
    '''
    params = {'oauth_token': oauth_token}
    if callback_url:
        params['oauth_callback'] = callback_url

    return '%s?%s' % (auth_url, urllib.urlencode(params))


def get_access_token(request_token, request_token_secret, 
                     access_token_url, access_token_method,
                     public_key, secret_key,
                     verifier):
    """
    Returns access token and access token secret
    """
    c = Client(public_key,
        secret_key,
        resource_owner_key=request_token,
        resource_owner_secret=request_token_secret,
        signature_type=SIGNATURE_TYPE_QUERY,
        verifier=verifier
    )

    uri, headers, body =  c.sign(uri=access_token_url, http_method=access_token_method)
    http = httplib2.Http()

    response, content = httplib2.Http.request(http, uri, method=access_token_method, body=body,
        headers=headers)

    if response.get('status') != '200':
        raise Exception("Invalid access token response: %s." % content)

    tokens = dict(urlparse.parse_qsl(content))
    access_token = tokens.get('oauth_token')
    access_token_secret = tokens.get('oauth_token_secret')
    return access_token, access_token_secret
