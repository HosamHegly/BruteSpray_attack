from typing import Tuple
import urllib
from collections import defaultdict
from lxml import html
import requests
from requests_html import HTMLSession

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

def jaccard_similarity(a, b):
    # convert to set
    a = set(a)
    b = set(b)
    # calucate jaccard similarity
    j = float(len(a.intersection(b))) / len(a.union(b))
    return j

def similarity_value(param, usernames):
    return max(usernames, key=lambda uname: jaccard_similarity(param.lower(), uname)) 

def _pick_params_regex(req_body, passwords, usernames):
    uname = max(req_body, key=lambda x: similarity_value(x, usernames)) 
    
    req_body.pop(uname)
    pname = max(req_body, key=lambda x: similarity_value(x, passwords)) 
    
    return uname, pname

def get_source(url, req_body,passwords_params_list, usernames_params_list, type):
    if type == 'javascript':
        session = HTMLSession()
        r = session.get(url)
        r.html.render()
        body = r.html.html
    else:
        r = requests.get(url)
        body = r.text
    doc = html.document_fromstring(body, base_url=url)
    params = _pick_params(doc.xpath('//form'), req_body)
    params = None
    if params:
        username , password = params
    else: username, password = _pick_params_regex(req_body, passwords_params_list, usernames_params_list)
    print(username, password)
    return username, password 