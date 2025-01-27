import json

import httpx

from backend.settings.base import (
    CLOUDFLARE_TURNSTILE_SECRET_KEY,
    CLOUDFLARE_TURNSTILE_VERIFY_URL,
)
from django_admin.utils import get_client_ip


def verify_token(request, token: str) -> bool:
    payload = json.dumps({
        'secret': CLOUDFLARE_TURNSTILE_SECRET_KEY,
        'response': token,
        'remoteip': get_client_ip(request)
    })

    response = httpx.post(
        CLOUDFLARE_TURNSTILE_VERIFY_URL, 
        data=payload, 
        headers={'Content-Type': 'application/json'}
    ).json()

    return response.get('success')
