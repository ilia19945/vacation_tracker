# Create your tasks here

from __future__ import absolute_import, unicode_literals

from taskapp.celery import app

@app.task
def send_email_when_approved(to_email, first_name=None, ):
    message = f"Hey {first_name}, your vacation request was *Approved*. " \
              f"Don't forget to write down vacation memo for your colleagues, set up autoreply for your emails and set up your vacation on the calendar. " \
              f"Wishing you a good vacation! :) "
    #  както отправить сообщение нужно в слаке или имейлом
    print(f'The notification was sent to {to_email}')
    return "success"

