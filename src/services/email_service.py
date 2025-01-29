import logging
from typing import Any, List

import httpx
from django.template.loader import render_to_string

from backend.settings.base import (
    APP_MODE,
    BRAND_NAME,
    DEFAULT_EMAIL_SENDER,
    SMTP_API_KEY,
    SMTP_API_URL,
    DjangoSettings,
)
from backend.settings.logging import LoggerContext

log = logging.getLogger(__name__)

def send_email(to: List[str],
               subject: str,
               email_template: str,
               template_context: dict,
               cc: List[str] = [],
               bcc: List[str] = [],
               attachments: List[Any] | None = None,
               override_sender_email: str | None = None) -> None:
    """
        @param to: A list of email recipients as string
        @param subject: The string subject of the email
        @param email_template: The string path of the email template to be used
        @param template_context: The dict context to be used for the email template
        @param cc: The list of email recipients as string to be cc'ed
        @param bcc: The list of email recipients as string to be bcc'ed
        @param attachments: The list of attachments to be sent
        @param override_sender_email: The optional string email to be used as the sender of the 
           email. If not provided, default email sender is used
    """
    if APP_MODE == DjangoSettings.TEST:
        return

    # Default email sender
    sender: str = DEFAULT_EMAIL_SENDER

    # Assign brand name
    template_context['brand_name'] = BRAND_NAME

    try:
        data = {
            'to': to,
            'sender': sender,
            'subject': subject,
            'html_body': render_to_string(email_template, template_context),
            'api_key': SMTP_API_KEY,
        }

        if cc:
            data['cc'] = cc

        if bcc:
            data['bcc'] = bcc

        if attachments:
            data['attachments'] = attachments

        if override_sender_email:
            data['sender'] = override_sender_email

        response = httpx.post(
            SMTP_API_URL, 
            json=data, 
            headers={'Content-type': 'application/json'},
            timeout=10
        )

        response_data = response.json()

        context = {
            'subject': subject,
            'to': to,
            'cc': cc,
            'bcc': bcc
        }

        if response.status_code != 200:
            context['error'] = str(response_data.get('data'))
            log_ctx = LoggerContext(
                type='EMAIL_ERROR',
                context=context
            )
            log.error(f'Error encountered with email api: {log_ctx.__dict__}')
        else:
            context['response'] = str(response_data.get('data'))
            log_ctx = LoggerContext(
                type='EMAIL_SUCCESS',
                context=context
            )
            log.info(f'Email api successful with response: {log_ctx.__dict__}')
    except Exception as e:
        context['exception'] = str(e)
        log_ctx = LoggerContext(
            type='EMAIL_ERROR',
            context=context
        )
        log.error(f'Email error encountered: {log_ctx.__dict__}')
