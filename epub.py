import requests
import vk_api
from upload_file import upload_file
from ebooklib import epub
from constants import login, password
from jinja2 import Template
import datetime

import vk
import time


class Message(object):
    def __init__(self, text='', sender_name='', date=None):
        self.text = text
        self.sender_name = sender_name
        self.date = date

    def __str__(self):
        return '{}'.format(self.text)


def get_vk_tools_and_upload(login, password):
    vk_session = vk_api.VkApi(login, password)
    try:
        vk_session.authorization()
    except vk_api.AuthorizationError as error_msg:
        print(error_msg)

    return vk_api.VkTools(vk_session), vk_api.VkUpload(vk_session)


def get_vk_my_id(tools):
    return int(tools.vk.token['user_id'])


def get_name_by_id(id):
    resp = requests.get('https://api.vk.com/api.php?oauth=1',
                        params={'method': 'users.get', 'user_id': id})

    user = resp.json()['response'][0]
    try:
        return '{} {}'.format(user['first_name'], user['last_name'])
    except KeyError:
        return 'Unknown'


def get_full_history_with(tools=None, user_id='me'):
    my_id = get_vk_my_id(tools=tools)

    if user_id == 'me' and tools:
        user_id = my_id

    return tools.get_all('messages.getHistory', 100, {'owner_id': my_id, 'user_id': user_id})


def generate_html_for_month(month_messages, month):
    stringed_messages = []
    date = None
    author = None

    for message in month_messages:
        current_date = message.date.strftime('%Y-%m-%d')

        full_message = ''
        if author != message.sender_name:
            author = message.sender_name
            full_message = '<b>{}</b> \n'.format(author)

        if date == current_date:
            full_message += message.__str__()
        else:
            date = current_date
            full_message = '<b>{}</b> <br> {}'.format(date, full_message)


        stringed_messages.append(full_message)

    html = open('templates/chat_template.html').read()
    template = Template(html)
    return template.render(messages=stringed_messages, month=month)


def divide_messages_by_months(messages, my_id, other_id):
    year_month = ''
    month_messages = []

    names = {my_id: get_name_by_id(my_id), other_id: get_name_by_id(other_id)}
    vk_messages = reversed(messages['items'])
    for vk_msg in vk_messages:
        message_date = datetime.datetime.fromtimestamp(vk_msg['date'])
        if year_month != message_date.strftime('%Y-%m'):
            year_month = message_date.strftime('%Y-%m')
            yield month_messages
            month_messages = []
        month_messages.append(Message(text=vk_msg['body'], sender_name=names[vk_msg['from_id']], date=message_date))
    yield month_messages


def get_vk_messages_and_id(tools, with_id):
    my_id = get_vk_my_id(tools)
    messages = get_full_history_with(tools, with_id)
    return messages, my_id


def start_book():
    book = epub.EpubBook()
    # set metadata
    book.set_identifier('111')
    book.set_title('Dialogue')
    book.set_language('ru')

    book.add_author('Chikko')
    return book


def generate_chapter(html, month):
    # create chapter
    chapter = epub.EpubHtml(title=month, file_name='{}.xhtml'.format(month), lang='ru')
    chapter.content = html
    return chapter


def generate_book(messages, my_id, with_id):
    book = start_book()
    chapters = []
    months = []

    for month_messages in divide_messages_by_months(messages, my_id, with_id):
        if not month_messages:
            continue
        month = str(month_messages[0].date.strftime('%m-%Y'))
        months.append(month)

        html = generate_html_for_month(month_messages, month)
        chapters.append(generate_chapter(html, month))

    for chapter in chapters:
        book.add_item(chapter)

    # book.toc = tuple(epub.Link('{}.xhtml'.format(month), month, month) for month in months)
    book.toc = tuple(chapters)

    # add default NCX and Nav file
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # define CSS style
    style = ''
    default_css = epub.EpubItem(uid="style_default", file_name="styles/chat.css", media_type="text/css", content=style)

    # add CSS file
    book.add_item(default_css)

    book.spine = ['nav'] + chapters

    # write to the file
    epub.write_epub('book.epub', book, {})


def check_if_book(text, api, out=0, time=60, how_many_requested=10):
    mes = api.messages.get(out=out, count=1, time_offset=time)
    done = False
    if len(mes) > 1 and text == mes[1]['body']:
        build_book(int(mes[1]['uid']))
        done = True
    if how_many_requested > 10:
        exit()
    return done


def main():
    session = vk.Session(access_token='')
    api = vk.API(session)
    how_many_requested = 0

    while True:
        check_if_book(api=api, text='book', how_many_requested=how_many_requested)
        time.sleep(60)


def build_book(with_id=-1):
    tools, upload = get_vk_tools_and_upload(login=login, password=password)
    messages, my_id = get_vk_messages_and_id(tools, with_id)
    generate_book(messages, my_id, with_id)
    upload_file(upload=upload, my_id=my_id, with_id=with_id)


if __name__ == '__main__':
    main()
