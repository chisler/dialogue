from ebooklib import epub
from jinja2 import Template

from .vk_get_messages import divide_messages_by_months
from .constants import DEFAULT_BOOK_LANGUAGE, DEFAULT_AUTHOR, FILE_NAME


def generate_html_for_month(month_messages):
    stringed_messages = []
    date = None
    author = None

    for message in month_messages['messages']:
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
    return template.render(messages=stringed_messages, month=month_messages['month'])


def start_book(title='Dialogue', language=DEFAULT_BOOK_LANGUAGE, author=DEFAULT_AUTHOR):
    book = epub.EpubBook()

    book.set_identifier('415')
    book.set_title(title)
    book.set_language(language)
    book.add_author(author)

    return book


def generate_chapter(html, month):
    chapter = epub.EpubHtml(title=month, file_name='{}.xhtml'.format(month), lang='ru')
    chapter.content = html
    return chapter


def generate_book(messages, session):
    book = start_book()
    chapters = []

    for month_messages in divide_messages_by_months(messages, session):
        if not month_messages:
            continue

        html = generate_html_for_month(month_messages)
        chapters.append(generate_chapter(html, month_messages['month']))

    for chapter in chapters:
        book.add_item(chapter)

    book.toc = tuple(chapters)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    book.spine = ['nav'] + chapters

    epub.write_epub(FILE_NAME, book, {})
