import datetime

import os
import requests
import vk_api

from .constants import FILE_NAME
from .message import Message


class SessionVk(object):
    def __init__(self, vk_session=None, other_id=-1):
        self.vk_session = vk_session
        self.other_id = other_id
        if vk_session:
            self.tools = vk_api.VkTools(vk_session)
            self.upload = vk_api.VkUpload(vk_session)
            self.my_id = get_vk_my_id(self)

    def __str__(self):
        return 'VK session of {}'.format(self.my_id)


def create_vk_session(login, password):
    vk_session = vk_api.VkApi(login, password)
    try:
        vk_session.authorization()
    except (vk_api.AuthorizationError, vk_api.ApiError) as error_msg:
        print(error_msg)
        return 'TryAgain'

    return SessionVk(vk_session=vk_session)


def get_vk_my_id(session):
    try:
        return int(session.tools.vk.token['user_id'])
    except KeyError:
        return -1


def get_vk_id_by_url(session, url):
    try:
        user_id_or_alias = url.split('/')[-1]
        user = session.tools.get_all('users.get', 100, {'user_ids': user_id_or_alias, 'name_case': 'Nom'})
        id = user['items'][0]['uid']
    except KeyError:
        return -1


def get_name_by_id(user_id):
    resp = requests.get('https://api.vk.com/api.php?oauth=1',
                        params={'method': 'users.get',
                                'user_id': user_id
                                })

    try:
        user = resp.json()['response'][0]
        return '{} {}'.format(user['first_name'], user['last_name'])
    except KeyError:
        return 'Unknown'


def get_full_history_with(session):
    return session.tools.get_all('messages.getHistory', 100, {'owner_id': session.my_id, 'user_id': session.other_id})


def divide_messages_by_months(messages, session):
    month = ''
    month_messages = []
    names = {session.my_id: get_name_by_id(session.my_id),
             session.other_id: get_name_by_id(session.other_id)}

    for vk_msg in reversed(messages['items']):
        message_date = datetime.datetime.fromtimestamp(vk_msg['date'])
        message_month = message_date.strftime('%Y-%m')

        if month != message_month:
            month = message_month
            yield {'messages': month_messages, 'month': month}
            month_messages = []

        month_messages.append(Message(text=vk_msg['body'], sender_name=names[vk_msg['from_id']], date=message_date))

    yield {'messages': month_messages, 'month': month}


def vk_send_file_to(session, doc_id, recipient_id):
    token = session.upload.vk.token['access_token']

    resp = requests.post('https://api.vk.com/api.php?oauth=1',
                         params={'method': 'messages.send',
                                 'access_token': token,
                                 'user_id': recipient_id,
                                 'message': 'Книга о разговорах',
                                 'attachment': 'doc{}_{}'.format(session.my_id, doc_id)})

    if resp.status_code == 200:
        return 'Book is sent to {}'.format(recipient_id)
    return 'Book was not sent. Try again.'


def send_file(session, doc_id, send_to_other=False):
    results = [vk_send_file_to(session, doc_id, session.my_id)]

    if send_to_other:
        results.append(vk_send_file_to(session, doc_id, session.other_id))

    return results


def upload_file(session):
    file = session.upload.document(file_path=FILE_NAME, title='Book of chat')
    doc_id = file[0]['id']

    print('\n'.join(send_file(session, doc_id)))

    os.remove(file=FILE_NAME)
