from dialogue.scripts.vk_get_messages import create_vk_session, get_vk_messages, upload_file
from dialogue.scripts.book import generate_book


def main():
    login = 'chisler@mail.ru'
    password = ''
    with_id = 2025894

    session = create_vk_session(login=login, password=password)
    session.other_id = with_id

    messages = get_vk_messages(session)
    generate_book(messages, session)
    upload_file(session)


if __name__ == '__main__':
    main()
