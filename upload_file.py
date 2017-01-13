import requests

how_many_are_requested = 0


def send_file(token, my_id, user_id, doc_id):
    resp = requests.post('https://api.vk.com/api.php?oauth=1',
                         params={'method': 'messages.send',
                                 'access_token': token,
                                 'user_id': user_id,
                                 'message': 'Книга о разговорах',
                                 'attachment': 'doc{}_{}'.format(my_id, doc_id)})
    print(resp)
    return resp


def upload_file(upload, my_id, with_id):
    file = upload.document(file_path='book.epub', title='Book of chat')
    doc_id = file[0]['id']
    # attachment = file[0]['url'].split('https://vk.com/')[1]
    print(file)
    token = upload.vk.token['access_token']
    send_file(token, my_id, with_id, doc_id)
    print('sent to {}'.format(with_id))


