"""Lee solo opciones públicas de proxy del .env, sin ejecutar su contenido."""
import os
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit


def settings(path):
    values = {'OICA_PROXY_MODE': 'container', 'OICA_PUBLIC_URL': 'https://oica.cris-munoz.me'}
    source = Path(path)
    if source.is_file():
        for line in source.read_text().splitlines():
            match = re.fullmatch(r'\s*(?:export\s+)?(OICA_PROXY_MODE|OICA_PUBLIC_URL)\s*=\s*(.*?)\s*', line)
            if match:
                value = match[2]
                quoted = re.fullmatch(r'''["']([^"']*)["']\s*(?:#.*)?''', value)
                values[match[1]] = quoted[1] if quoted else value.split(' #', 1)[0].strip()
    for key in values:
        if key in os.environ:
            values[key] = os.environ[key]
    if values['OICA_PROXY_MODE'] not in ('container', 'host'):
        raise ValueError('OICA_PROXY_MODE debe ser container o host')
    url = urlsplit(values['OICA_PUBLIC_URL'])
    if (url.scheme not in ('http', 'https') or not url.hostname or url.username or url.password
            or url.path not in ('', '/') or url.query or url.fragment
            or any(c.isspace() for c in values['OICA_PUBLIC_URL'])):
        raise ValueError('OICA_PUBLIC_URL debe ser un origen HTTP(S), sin credenciales ni rutas')
    return values


if __name__ == '__main__':
    try:
        print(settings(sys.argv[1])[sys.argv[2]])
    except (ValueError, KeyError) as error:
        sys.exit(str(error))
