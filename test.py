from lxml import html
from time import sleep
from urllib import request, response
from requests_html import HTMLSession
import requests
from xml.etree import ElementTree as et

request = requests.get('https://defendtheweb.net/auth')
ht = html.document_fromstring(request.text)

from bs4 import BeautifulSoup
soup = BeautifulSoup(request.text, "html.parser")

inputs=soup.find("input", {"name": "token"})
print(inputs['value'])