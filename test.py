from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import requests



payload = {'uname': 'test1', 'pass': 'testt'}
resp = requests.post(url='http://testphp.vulnweb.com/userinfo.php', data = payload, allow_redirects=False)
print(resp.text)
