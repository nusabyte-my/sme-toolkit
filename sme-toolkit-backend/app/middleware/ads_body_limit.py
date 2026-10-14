"""Reject oversized ad payloads before JSON/base64 parsing allocates unbounded memory."""
from starlette.responses import JSONResponse


class AdsBodyLimit:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http' or not scope['path'].startswith('/api/v1/ads/') or scope['method'] not in ('POST', 'PUT', 'PATCH'):
            await self.app(scope, receive, send)
            return
        limit = 42_100_000 if scope['path'] == '/api/v1/ads/assets' else 100_000
        body = bytearray()
        while True:
            message = await receive()
            if message['type'] == 'http.disconnect':
                return
            body.extend(message.get('body', b''))
            if len(body) > limit:
                await JSONResponse({'detail': 'Advertising request exceeds the upload size limit.'}, status_code=413)(scope, receive, send)
                return
            if not message.get('more_body', False):
                break
        delivered = False
        async def replay():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {'type': 'http.request', 'body': bytes(body), 'more_body': False}
            return await receive()
        await self.app(scope, replay, send)
