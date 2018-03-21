from __future__ import absolute_import, print_function
from pprint import pprint
import unittest
import webbrowser

import docusign_esign as docusign
from docusign_esign import AuthenticationApi, TemplatesApi, EnvelopesApi
from docusign_esign.rest import ApiException

user_name      = "namgivu@gmail.com" #this value taken from API Username ref. https://admindemo.docusign.com/api-integrator-key
user_id        = "f3d9588f-4aee-4c2c-8873-d66ea8860ce4" #this value taken from API Username ref. https://admindemo.docusign.com/api-integrator-key
integrator_key = "b9182992-b2b4-411b-9aa4-cdbbc3d0c6d9"
base_url       = "https://demo.docusign.net/restapi"
oauth_base_url = "account-d.docusign.com" # use account.docusign.com for Live/Production
redirect_uri   = "https://www.docusign.com/api" #must register with integrator_key ref. https://support.docusign.com/en/articles/Redirect-URI-not-registered

template_id        = "40cff443-cbd6-4751-a59a-c1e1d9668b93"
template_role_name = 'contract object'

private_key_filename = "/home/namgivu/.ssh/namgivu-docusign" #TODO what is this for?

api_client = docusign.ApiClient(base_url)

# IMPORTANT NOTE:
# the first time you ask for a JWT access token, you should grant access by making the following call
# get DocuSign OAuth authorization url:
oauth_login_url = api_client.get_jwt_uri(integrator_key, redirect_uri, oauth_base_url)
# open DocuSign OAuth authorization url in the browser, login and grant access
# webbrowser.open_new_tab(oauth_login_url)
print('oauth_login_url=%s' % oauth_login_url)

# END OF NOTE

# configure the ApiClient to asynchronously get an access token and store it
api_client.configure_jwt_authorization_flow(private_key_filename, oauth_base_url, integrator_key, user_id, 3600) #TODO we cannot reach this
docusign.configuration.api_client = api_client


##region prepare envelope
# create an envelope to be signed
envelope_definition = docusign.EnvelopeDefinition()
envelope_definition.email_subject = 'Please Sign my Python SDK Envelope'
envelope_definition.email_blurb   = 'Hello, Please sign my Python SDK Envelope.'
# assign template information including ID and role(s)
envelope_definition.template_id = template_id

# create a template role with a valid template_id and role_name and assign signer info
t_role = docusign.TemplateRole()
t_role.role_name = template_role_name
t_role.name ='Pat Developer'
t_role.email = user_name

# create a list of template roles and add our newly created role
# assign template role(s) to the envelope
envelope_definition.template_roles = [t_role]

# send the envelope by setting |status| to "sent". To save as a draft set to "created"
envelope_definition.status = 'sent'

##endregion prepare envelope

auth_api = AuthenticationApi()
envelopes_api = EnvelopesApi()

try:
    login_info = auth_api.login(api_password='true', include_account_id_guid='true')
    import sys; sys.exit() #TODO need fix in $VENV/python3.5/site-packages/docusign_esign/api_client.py ref.
    '''
    full error
    /home/namgivu/NN/code/_NN_/docusign-start/venv3/bin/python /home/namgivu/NN/code/_NN_/docusign-start/run00.py
    oauth_login_url=https://account-d.docusign.com/oauth/auth?response_type=code&client_id=b9182992-b2b4-411b-9aa4-cdbbc3d0c6d9&scope=signature%20impersonation&redirect_uri=https%3A%2F%2Fwww.docusign.com%2Fapi
    Traceback (most recent call last):
      File "/home/namgivu/NN/code/_NN_/docusign-start/run00.py", line 66, in <module>
        login_info = auth_api.login(api_password='true', include_account_id_guid='true')
      File "/home/namgivu/NN/code/_NN_/docusign-start/venv3/lib/python3.5/site-packages/docusign_esign/apis/authentication_api.py", line 388, in login
        (data) = self.login_with_http_info(**kwargs)
      File "/home/namgivu/NN/code/_NN_/docusign-start/venv3/lib/python3.5/site-packages/docusign_esign/apis/authentication_api.py", line 472, in login_with_http_info
        collection_formats=collection_formats)
      File "/home/namgivu/NN/code/_NN_/docusign-start/venv3/lib/python3.5/site-packages/docusign_esign/api_client.py", line 373, in call_api
        _return_http_data_only, collection_formats, _preload_content, _request_timeout)
      File "/home/namgivu/NN/code/_NN_/docusign-start/venv3/lib/python3.5/site-packages/docusign_esign/api_client.py", line 208, in __call_api
        return_data = self.deserialize(response_data, response_type)
      File "/home/namgivu/NN/code/_NN_/docusign-start/venv3/lib/python3.5/site-packages/docusign_esign/api_client.py", line 282, in deserialize
        data = json.loads(response.data)
      File "/usr/lib/python3.5/json/__init__.py", line 312, in loads
        s.__class__.__name__))
    TypeError: the JSON object must be str, not 'bytes'    
    '''
    assert login_info is not None
    assert len(login_info.login_accounts) > 0

    login_accounts = login_info.login_accounts
    assert login_accounts[0].account_id is not None

    base_url, _ = login_accounts[0].base_url.split('/v2')
    api_client.host = base_url
    docusign.configuration.api_client = api_client

    envelope_summary = envelopes_api.create_envelope(login_accounts[0].account_id, envelope_definition=envelope_definition)
    assert envelope_summary is not None
    assert envelope_summary.envelope_id is not None
    assert envelope_summary.status == 'sent'

    print("EnvelopeSummary: ", end="")
    pprint(envelope_summary)

except ApiException as e:
    print("\nException when calling DocuSign API: %s" % e)
    assert e is None # make the test case fail in case of an API exception
