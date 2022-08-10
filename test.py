from bs4 import BeautifulSoup as bs
from playwright.sync_api import sync_playwright


with sync_playwright() as p:
    browser = p.firefox.launch()
    page = browser.new_page()


    page.goto("http://testphp.vulnweb.com/login.php")
    soup = bs(page.content(), "html.parser")
    results = soup.find(attrs={'type' : 'button'})
    print(str(results))