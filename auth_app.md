# Auth app

## OAuth 2.0 
RFC 6749
### Roles

OAuth defines four roles:
##### - `resource owner`
An entity capable of granting access to a protected resource.
When the resource owner is a person, it is referred to as an
end-user.

##### - `resource server`
The server hosting the protected resources, capable of accepting
and responding to protected resource requests using access tokens.

##### - `client`
An application making protected resource requests on behalf of the
resource owner and with its authorization.  The term "client" does
not imply any particular implementation characteristics (e.g.,
whether the application executes on a server, a desktop, or other
devices).

##### - `authorization server`
The server issuing access tokens to the client after successfully
authenticating the resource owner and obtaining authorization.

### Protocol flow
```
     +--------+                               +---------------+
     |        |--(A)- Authorization Request ->|   Resource    |
     |        |                               |     Owner     |
     |        |<-(B)-- Authorization Grant ---|               |
     |        |                               +---------------+
     |        |
     |        |                               +---------------+
     |        |--(C)-- Authorization Grant -->| Authorization |
     | Client |                               |     Server    |
     |        |<-(D)----- Access Token -------|               |
     |        |                               +---------------+
     |        |
     |        |                               +---------------+
     |        |--(E)----- Access Token ------>|    Resource   |
     |        |                               |     Server    |
     |        |<-(F)--- Protected Resource ---|               |
     +--------+                               +---------------+
```
- `A`  The client requests authorization from the resource owner.  The
authorization request can be made directly to the resource owner
(as shown), or preferably indirectly via the authorization
server as an intermediary.

- `B`  The client receives an authorization grant, which is a
credential representing the resource owner's authorization,
expressed using one of four grant types defined in this
specification or using an extension grant type.  The
authorization grant type depends on the method used by the
client to request authorization and the types supported by the
authorization server.

- `C`  The client requests an access token by authenticating with the
authorization server and presenting the authorization grant.

- `D`  The authorization server authenticates the client and validates
the authorization grant, and if valid, issues an access token.

- `E`  The client requests the protected resource from the resource
server and authenticates by presenting the access token.

- `F`  The resource server validates the access token, and if valid,
serves the request.

## Resoureces
- [RFC 6749](https://datatracker.ietf.org/doc/html/rfc6749#section-1.2)
