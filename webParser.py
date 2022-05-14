from typing import Tuple
import urllib
from collections import defaultdict
from lxml import html
import requests
from requests_html import HTMLSession
def _form_score(form, req_body):
    '''rate form by score. form with highest score is the has the highest chance of being the log in form'''
    for input in form.inputs:
        inputName = input.get('name')
        for param in req_body:
            if inputName == param:
                if input.type == 'text' or input.type == 'email':
                    username = inputName
                elif input.type == 'password':
                    password = inputName
    
    return username, password if username and password else None


def _pick_params(forms, req_body):
    '''rate form by score. form with highest score is the has the highest chance of being the log in form'''
    username = None
    password = None
    for form in forms:
        for input in form.inputs:
            if input.tag == 'input':
                inputName = input.get('name')
                print('input: ' + inputName +'+  ' + input.tag)
                for param in req_body:
                    if inputName == param:
                        if input.type == 'text' or input.type == 'email':
                            username = inputName
                        elif input.type == 'password':
                            password = inputName
                    if username and password:
                        return username, password  
    return None

def _pick_params_regex(req_body):
    pass

def get_source(url, req_body, type):
    if type == 'javascript':
        session = HTMLSession()
        r = session.get(url)
        r.html.render()
        body = r.html.html
        print('\n\n\n\n\n\n\n\n' + str(body) + '\n\n\n\n\n\n')
    else:
        r = requests.get(url)
        body = r.text
    print('get req')
    doc = html.document_fromstring(body, base_url=url)
    print(' html.document_fromstring(r.text, base_url=url)')
    print('\n\n\n\n\n\n ' + str(len(doc.xpath('//form'))))
    params = _pick_params(doc.xpath('//form'), req_body)
    print("_pick_params(doc.xpath('//form'), req_body)")
    if params:
        username , password = params
    else: username, password = _pick_params_regex(req_body)
    return username, password 