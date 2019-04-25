# Magic Reverse Proxy

An nginx docker container with automatic letsencrypt certificate generation and authentication for all services behind the reverse proxy. HTTP traffic is redirected to HTTPS, and the authentication cookie (if using the example auth server) will apply to all of the subdomains, meaning you only need to authenticate once to get access to all of your websites.

*Note:* your docker container *must* be accessible on port 80 and port 443 for this to work.

*Note:* an authentication server is required, see my [magicauthserver3](https://github.com/sillyfrog/magicauthserver3/) for an example.

## Build Docker Image

To run, firstly build the docker image:
```docker build . -t reverseproxy```

## Setup Your Server

Then update your `servers.ini` file, note the following:
 - The `general` section is required, and must have an `email` and `authserver` set
 - `email` is a contact email address for you that's used by certbot on the certificates
 - `autheserver` is a web service that provides authentication services for the nginx reverse proxy. See my [magicauthserver3](https://github.com/sillyfrog/magicauthserve3r/) for a simple sample implementation.
 - All other sections are the domain name of the web site, this is what will be used by certbot to get an SSL certificate, this MUST be accessible on both port 80 and 443 to work.
 - All sections must have a `destination` set, or the first domain section may have `index = true`, this will not forward internally, rather it will give a simple index to all of the sites that are configured (a simple landing page).
 - `destination` must be a URL that is accessible by the docker container (either HTTP or HTTPS), and this is where all traffic will be forwarded that hits the HTTPS web site for the domain, once the user is authenticated.
 - An optional `options` section maybe included, and this will be added to the relevant *location* section for the nginx config for the site.
 - An optional `serveroptions` section maybe included, and this will be added to the relevant *server* section for the nginx config for the site.
 - An optional `noauthip` section will allow specified IP ranges to be excluded from auth for that host. Multiple values are space separated.

Look at the `servers.ini.example` for an example of how this ini file should look.

## Run Your Server

Once all of that is done, start the docker file, with something such as this:
```docker run --name reverseproxy -d -p 80:80 -p 443:443 -v /etc/localtime:/etc/localtime:ro -v /path/to/servers.ini:/etc/servers.ini:ro -v /secure/path/to/certs:/etc/letsencrypt reverseproxy```

Upon the first run, it will generate certificates, and then start nginx. It will automatically renew certificates as required, checking every day.

## Check the Logs

Always look at the logs, as if something went wrong, it will be there. I have included a 2 minute wait should something go wrong so the letsencrypt servers are not smashed. To view the logs in docker:
```docker logs reverseproxy```

