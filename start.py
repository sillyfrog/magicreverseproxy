#!/usr/bin/env python

import ConfigParser
import collections
import subprocess
import sys
import time

EMAIL = 1
DOMAINS = 2
CMD = [
    'certbot',
    'certonly',
    # '--test-cert',
    '--standalone',
    '-n',
    '--agree-tos',
    '--email',
    EMAIL,
    '--expand',
    '--domains',
    DOMAINS,
]


def getconfigs():
    config = ConfigParser.ConfigParser()
    config.read('/etc/servers.ini')

    general = {}
    domains = collections.OrderedDict()
    for section in config.sections():
        values = collections.OrderedDict(config.items(section))
        if section == 'general':
            general = values
        else:
            domains[section] = values

    return general, domains


def execute(cmd):
    P = subprocess.Popen(cmd)
    if P.wait() != 0:
        sys.stderr.write("Something went wrong, review the logs!\n")
        time.sleep(120) # Sleep before dying to prevent hammering letsencrypt
        sys.exit(1)


def applytemplate(template, destfn, values):
    f = open(destfn, 'w')
    f.write(template % values)
    f.close()


def main():
    general, configs = getconfigs()
    domains = configs.keys()

    # Check and generate all certs
    doms = ','.join(domains)
    cmd = list(CMD)
    cmd[cmd.index(EMAIL)] = general['email']
    cmd[cmd.index(DOMAINS)] = doms
    execute(cmd)

    # Put the default template in place
    applytemplate(
        open('/conftemplates/default.conf').read(), '/etc/nginx/conf.d/default.conf', {}
    )

    values = {
        'certificatepath': '/etc/letsencrypt/live/{}/fullchain.pem'.format(domains[0]),
        'keypath': '/etc/letsencrypt/live/{}/privkey.pem'.format(domains[0]),
        'authserver': general['authserver'],
    }

    # Check if the first entry is an index listing
    firstdom, firstconfig = configs.items()[0]
    if firstconfig.get('index', 'false').lower() == 'true':
        conftemplate = open('/conftemplates/index.conf').read()
        template = open('/conftemplates/index.html').read()
        configs.pop(firstdom)  # Remove this config item as it's not a proxy
        htmlblock = ''
        for domain in configs.keys():
            htmlblock += '<li><a href="https://{0}/">{0}</a></li>\n'.format(domain)
        applytemplate(
            template, '/usr/share/nginx/html/index.html', {'domains': htmlblock}
        )
        values['domain'] = firstdom
        applytemplate(conftemplate, '/etc/nginx/conf.d/0000_index.conf', values)

    # Generate the template for the domanis
    template = open('/conftemplates/domains.conf').read()

    i = 1
    for domain, config in configs.iteritems():
        values['domain'] = domain
        values['proxydest'] = config['destination']
        values['options'] = config.get('options', '')
        fn = '/etc/nginx/conf.d/{:04d}_{}.conf'.format(i, domain)
        applytemplate(template, fn, values)
        i += 1

    # Start nginx
    execute(["nginx", "-g", "daemon on;"])
    print("Started nginx without errors")

    # Renew certs daily...
    execute(
        [
            'tinycron',
            '@daily',
            "/certbotrenew.sh",
        ]
    )


if __name__ == '__main__':
    main()
