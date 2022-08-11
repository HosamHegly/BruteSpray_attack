from bs4 import BeautifulSoup as bs
from attack.headless import headless
from playwright.sync_api import sync_playwright


with sync_playwright() as p:
    browser = p.firefox.launch(headless=False)
    page = browser.new_page()
    

    page.goto("https://brokencrystals.com/userlogin")
    page.fill("input[name=user]", "mohamadassi173@gmail.com")
    page.fill("input[name=password]", "assialahjugbal")
    with page.expect_response("https://brokencrystals.com/userlogin") as response_info:
        page.click('button[type=submit]')
        
        print(str(response_info.value))
   
