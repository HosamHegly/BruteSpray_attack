import logging
from typing import Tuple
import urllib
from collections import defaultdict
from lxml import html
import requests
from requests_html import HTMLSession

#picks the login form in page
def pickForm(forms, req_body):
    input_list = []
    for form in forms:
        for input in form.inputs:
            input_list.append(input.get('name'))
        keys = list(req_body.keys())
        if set(keys).issubset(input_list):
            return form

#identify the user and password params in the body
def _pick_params(form, req_body):
    username = None
    password = None
    for input in form.inputs:
        if input.tag == 'input':
            inputName = input.get('name')
            for param in req_body:
                if inputName == param:
                    if input.type == 'email':
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
    #param with max potetntial for being the username
    uname = max(req_body, key=lambda x: similarity_value(x, usernames)) 
    
    req_body.pop(uname)
    #param with max potetntial for being the password
    pname = max(req_body, key=lambda x: similarity_value(x, passwords)) 
    
    return uname, pname

def get_source(args, params_list):
    """
    find the username and password params in the body
    """
    if args['type'] == 'javascript':
        session = HTMLSession()
        r = session.get(args["url"])
        r.html.render()
        body = r.html.html
    else:
        r = requests.get(args["url"])
        body = r.text
        
    doc = html.document_fromstring(body, base_url=args["url"])
    form = pickForm(doc.xpath('//form'), args["req_body"])

    params = _pick_params(form, args["req_body"])
    if params:
        logging.info('[webParser] Fetched user and password params from html')
        args["user_param"], args["password_param"] = params
    else: 
        logging.info('[webParser] Fetched user and password params from json list')
        args["user_param"], args["password_param"] = _pick_params_regex(args["req_body"], params_list["password_param"], params_list["user_param"])
    
    args["req_body_type"] = get_req_type(args["headers"])

    return args
    
    # get content type from headers
def get_req_type(header):
    type = header["content-type"]

    if "json" in type:
        return "JSON"

    elif "xml" in type:
        import xmltodict
        
    elif "multipart" in type:
        return "multipart"

    else:
        import urllib

        return "URL_ENCODED"
