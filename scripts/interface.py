from .vk_get_messages import create_vk_session, SessionVk, get_vk_id_by_url


def get_credentials():
    print('Login:', end='')
    login = input()
    print('Password:', end='')
    password = input()
    return login, password


def log_in():
    print('Hi! Enter your vk credentials in order to access your messages.')

    login, password = get_credentials()
    session = create_vk_session(login, password)
    while session.my_id < 0:
        print('Something is wrong. Check it!')
        login, password = get_credentials()
        session = create_vk_session(login, password)
        print()

    print("Copy here the link of friend's page:", end='')
    url = input()
    other_id = get_vk_id_by_url(session, url)

    while other_id < 0:
        print('Something is wrong. Check it!')
        url = input()
        other_id = get_vk_id_by_url(session, url)
        print()

    session.other_id = other_id

    return session
