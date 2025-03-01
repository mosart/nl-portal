# OpenAIE API | Guide for authenticated requests

## Authentication & limits

The OpenAIRE APIs are free-to-use by any third-party service and can be accessed over HTTPS both by authenticated and unauthenticated requests. The rate limit for the former type of requests is up to 7200 requests per hour, while the latter is up to 60 requests per hour.

To make an authenticated request, you must first register. Then, you can go to the personal access token page in your account, copy your token and use it for up to one hour, find out more.

Our OAuth 2.0 implementation, conforms to the OpenID Connect specification, and is OpenID Certified. OpenID Connect is a simple identity layer on top of the OAuth 2.0 protocol. For more information about OAuth2.0 please visit the OAuth2.0 official site. For more information about OpenID Connect please visit the OpenID Connect official site. Also, check here for more information on our Privacy Policy. 

## Basic service authentication and registration

For the Basic Authentication method the OpenAIRE AAI server generates a pair of Client ID and Client Secret for your service upon its registration. The service uses the client id and client secret to obtain the access token for the OpenAIRE APIs. The OpenAIRE AAI server checks whether the client id and client secret sent is valid.
How to register your service

To register your service you need to:

    Go to your Registered Services page and click the + New Service button.
    Provide the mandatory information for your service.
    Select the Basic Security level.
    Click the Create button.

Once your service is created, the Client ID and Client Secret will appear on your screen. Click "OK" and your new service will be appear in the list of your Registered Services page.

### How to make a request

#### Step 1. Request for an access token

To make an access token request use the Client ID and Client Secret of your service.

curl -u {CLIENT_ID}:{CLIENT_SECRET} \
-X POST 'https://aai.openaire.eu/oidc/token' \
-d 'grant_type=client_credentials'

where {CLIENT_ID} and {CLIENT_SECRET} are the Client ID and Client Secret assigned to your service upon registration.

The response is:

{
    "access_token": ...,
    "token_type": "Bearer",
    "expires_in": ...
}

Store the access token confidentially on the service side.

#### Step 2. Make a request

To access the OpenAIRE APIs send the access token returned in Step 1.

GET https://api.openaire.eu/{resourceServicePath}
Authorization: Bearer {ACCESS_TOKEN}

