import requests

base = 'http://127.0.0.1:8000'
paths = ['/v1/health', '/', '/v1/localize']

for path in paths:
    try:
        if path == '/v1/localize':
            r = requests.post(base + path, json={
                'text': 'Hello world',
                'target_language': 'es',
                'tone': 'neutral',
            })
        else:
            r = requests.get(base + path)

        ct = r.headers.get('content-type', '')
        body = r.text if 'text' in ct else r.json()
        print(path, '->', r.status_code, body)
    except Exception as e:
        print(path, 'ERROR', e)
