from dialogue.scripts.interface import log_in
from dialogue.scripts.vk_get_messages import get_full_history_with, upload_file
from dialogue.scripts.book import generate_book


def main():
    login = 'chisler@mail.ru'
    password = ''
    with_id = 2025894

    session = log_in()

    messages = get_full_history_with(session)
    generate_book(messages, session)
    upload_file(session)


if __name__ == '__main__':
    main()
