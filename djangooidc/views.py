from urlparse import parse_qs
import urllib

from django.conf import settings

from django.shortcuts import redirect, render_to_response
from django.http import HttpResponse
from jwkest.jws import alg2keytype
from oic.utils.http_util import Redirect

from djangooidc.oidc import OIDCClients


CLIENTS = OIDCClients(settings)

# debug
# JWE.is_jwe = JWEnc.is_jwe

def start_response(status, headers):
    # Empty method
    return


# Step 1: provider choice
def openid(request):
    request.session["next"] = request.GET["next"] if "next" in request.GET.keys() else "/"
    return render_to_response("oidc_django/opchoice.html", {"op_list": [i for i in settings.CLIENTS.keys() if i]})


# Step 2: redirect user to step 3 (the OP)
def rp(request, discovery_str=None, op_name=None):
    if discovery_str is not None:
        client = CLIENTS.dynamic_client(discovery_str)
        request.session["op"] = client.provider_info["issuer"]
    else:
        client = CLIENTS[op_name]
        request.session["op"] = op_name

    try:
        oic_resp = client.create_authn_request(request.session)
    except Exception:
        raise
    else:
        oic_resp(request.environ, start_response)
        resp = HttpResponse(content_type=oic_resp._content_type, status=oic_resp._status)
        for key, val in oic_resp.headers:
            resp[key] = val
        return resp


# Step 4: analyze the token returned by the OP
def authz_cb(request):
    client = CLIENTS[request.session["op"]]

    query = parse_qs(request.META['QUERY_STRING'])
    userinfo = client.callback(query, request.session)
    request.session["userinfo"] = userinfo

    return redirect(request.session["next"])


def logout(request):
    client = CLIENTS[request.session["op"]]

    logout_url = client.endsession_endpoint
    try:
        # Specify to which URL the OP should return the user after
        # log out. That URL must be registered with the OP at client
        # registration.
        logout_url += "?" + urllib.urlencode({
            "post_logout_redirect_uri": client.registration_response["post_logout_redirect_uris"][0]
        })
    except KeyError:
        pass
    else:
        # If there is an ID token send it along as a id_token_hint
        _idtoken = get_id_token(client, request.session)
        if _idtoken:
            logout_url += "&" + urllib.urlencode({
                "id_token_hint": id_token_as_signed_jwt(client, _idtoken, "HS256")
            })

    request.session.clear()
    oic_resp = Redirect(str(logout_url))
    oic_resp(request.environ, start_response)
    resp = HttpResponse(content_type=oic_resp._content_type, status=oic_resp._status)
    for key, val in oic_resp.headers:
        resp[key] = val
    return resp


def get_id_token(client, session):
    return client.grant[session["state"]].get_id_token()


# Produce a JWS, a signed JWT, containing a previously received ID token
def id_token_as_signed_jwt(client, id_token, alg="RS256"):
    ckey = client.keyjar.get_signing_key(alg2keytype(alg), "")
    _signed_jwt = id_token.to_jwt(key=ckey, algorithm=alg)
    return _signed_jwt

