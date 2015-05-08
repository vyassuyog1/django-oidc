import logging
from urlparse import parse_qs

from django.conf import settings
from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect, render_to_response, resolve_url
from django.http import HttpResponse
from django import forms
from django.template import RequestContext

from djangooidc.oidc import OIDCClients

logger = logging.getLogger(__name__)

CLIENTS = OIDCClients(settings)


# Step 1: provider choice (form). Also - Step 2: redirect to OP. (Step 3 is OP business.)
class DynamicProvider(forms.Form):
    hint = forms.CharField(required=True, label='login', max_length=250)


def openid(request, op_name=None):
    client = None
    request.session["next"] = request.GET["next"] if "next" in request.GET.keys() else "/"
    try:
        dyn = settings.ALLOW_DYNAMIC_OP or False
    except:
        dyn = True

    # Try to find an OP client either from the form or from the op_name URL argument
    if request.method == 'GET' and op_name is not None:
        client = CLIENTS[op_name]
        request.session["op"] = op_name

    if request.method == 'POST' and dyn:
        form = DynamicProvider(request.POST)
        if form.is_valid():
            try:
                client = CLIENTS.dynamic_client(form.cleaned_data["hint"])
                request.session["op"] = client.provider_info["issuer"]
            except Exception, e:
                logger.exception("could not create OOID client")
                return render_to_response("djangooidc/error.html", {"error": e})
    else:
        form = DynamicProvider()

    # If we were able to determine the OP client, just redirect to it with an authentication request
    if client:
        try:
            return client.create_authn_request(request.session)
        except Exception, e:
            return render_to_response("djangooidc/error.html", {"error": e})

    # Otherwise just render the list+form.
    return render_to_response("djangooidc/opchoice.html",
                              {"op_list": [i for i in settings.CLIENTS.keys() if i], 'dynamic': dyn,
                               'form': form}, context_instance=RequestContext(request))


# Step 4: analyze the token returned by the OP
def authz_cb(request):
    client = CLIENTS[request.session["op"]]
    query = None

    try:
        query = parse_qs(request.META['QUERY_STRING'])
        userinfo = client.callback(query, request.session)
        request.session["userinfo"] = userinfo

        return redirect(request.session["next"])
    except Exception, e:
        return render_to_response("djangooidc/error.html", {"error": e, "callback": query})


def logout(request, next_page=None):
    client = CLIENTS[request.session["op"]]

    # User is by default NOT redirected to the app - it stays on an OP page after logout.
    # Here we try to determine if a redirection to the app was asked for and is possible.
    extra_args = {}
    try:
        if next_page is not None:
            # Specific redirection required by user - will only work if registered with the OP
            next_page = resolve_url(next_page)
            urls = [i for i in client.registration_response["post_logout_redirect_uris"] if next_page in i]
            if len(urls) > 0:
                extra_args["post_logout_redirect_uri"] = urls[0]
        else:
            # Just take the first registered URL if no URL is specifically asked for
            extra_args["post_logout_redirect_uri"] = client.registration_response["post_logout_redirect_uris"][0]
    except KeyError:
        # No post_logout_redirect_uris - no redirection to the application is possible anyway
        pass

    # Redirect client to the OP logout page
    try:
        res = client.do_end_session_request(state=request.session["state"],
                                            extra_args=extra_args)
        resp = HttpResponse(content_type=res.headers["content-type"], status=res.status_code, content=res._content)
        for key, val in res.headers.items():
            resp[key] = val
        return resp
    finally:
        # Always remove Django session stuff
        auth_logout(request)
