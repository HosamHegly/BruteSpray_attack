import urllib
from collections import defaultdict
from lxml import html
import requests

def _form_score(form):
    '''rate form by score. form with highest score is the has the highest chance of being the log in form'''
    score = 0
    if 'log' in str(form.get('name')).lower() or 'sign' in str(form.get('name')).lower():
        score += 10

    if len(form.inputs.keys()) in (2, 3):
        score += 10

    typecount = defaultdict(int)
    for x in form.inputs:
        type_ = x.type if isinstance(x, html.InputElement) else "other"
        typecount[type_] += 1

    if typecount['text'] >= 1 or typecount['email'] >= 1:
        score += 10
    if not typecount['text']:
        score -= 10

    if typecount['password'] == 1:
        score += 10
    if not typecount['password']:
        score -= 10

    if typecount['checkbox'] > 1:
        score -= 10
    if typecount['radio']:
        score -= 10

    return score


def _pick_form(forms):
    '''find the form that has the highest chance to be the log ing form'''
    return sorted(forms, key=_form_score, reverse=True)[0]

def _pick_params(form, doc):
    ''' find username, password... parameter names in form'''
    submit = None
    for p in form.inputs:
        if p.type == 'text' or p.type == 'email':
            username = p.get('name')

        if p.type == 'password':
            password = p.get('name')

        if p.type == 'submit':
            submit = p.get('value')

    if(not submit):
        '''query = '//form[@id='+form.get("id")+']//button[@type=submit]'
        submit = doc.xpath(query)'''
        submit = "aaaaa"

    return username, password, submit


def get_source(url):
    r = requests.get(url, verify=False)
    doc = html.document_fromstring(r.text, base_url=url)
    form = _pick_form(doc.xpath('//form'))

    username , password , submit = _pick_params(form,doc)
    action = form.get('action')
    method = form.get('method')
    return username, password, submit, action, method







