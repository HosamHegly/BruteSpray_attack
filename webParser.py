import logging
import random
import time
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup as bs


class webParser:
    """
    this class' main purpose is to get the needed information to perform the attack successfully
    * initiates a playwright instance  with firefox web driver and goes to the login page.
    * locates the login form using a scoring system.
    * locates the username and password input fields and the login button
    * builds a string for the css locator for the login button
    * performs 2 failed login attempts with randomly generated passwords to retrieves the response status code, headers, body and content length


    """

    async def getsource(self, url, params_list, pass_user) -> None:
        """ """
        p = await async_playwright().start()
        browser = await p.firefox.launch()
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_selector("input[type=submit], button[type=submit]")

        self.headers = None
        body = await page.content()
        soup = bs(body, "html.parser")
        forms = soup.findAll("form")
        self.form = self.findForm(
            forms, params_list["ButtonList"], params_list["loginTexts"]
        )

        self.user_param, self.password_param = self._findUserPass(
            self.form, params_list["passwordParam"], params_list["userParam"]
        )

        # performs 2 failed login attempts by choosing 2 random usernames from
        # the csv files and generating 2 random passwords and calculates the average
        # content length of the 2 failed attempt response pages
        self.contentLen = 0
        for i in range(0, 2):
            username = pass_user["Usernames"][
                random.randint(0, len(pass_user["Usernames"]) - 1)
            ]
            password = self._pass_gen()
            logging.info("random password generated: " + str(password))

            await self._getRequest(
                self.user_param, self.password_param, page, username, password
            )
            self.contentLen += self.contentLen

        self.contentLen = self.contentLen / 2
        await browser.close()
        await p.stop()
        # get request body content type
        self.req_body_type = self._get_req_type()

    def _findUserPass(self, form, passwords, usernames) -> tuple:
        """ "
        identify the user and password params in the body
        """

        username = None
        password = None
        inputs = {}
        for input in form.findChildren("input"):
            if input["type"].lower() != "submit":
                inputName = input["name"]
                inputs[inputName] = ""
                if input["type"] == "email":
                    username = inputName
                elif input["type"] == "password":
                    password = inputName

        if not username:
            username = self._pick_param(inputs, usernames)
            inputs.pop(username)
        if not password:
            password = self._pick_param(inputs, passwords)

        return username, password

    async def _getRequestData(self, req) -> None:
        """
        Fetch request method, url, body, response status_code, request headers
        """

        if req.method == "POST":
            self.post_data = req.post_data_json
            self.method = req.method
            self.action = req.url
            response = await req.response()
            self.status_code = response.status
            self.headers = {k.lower(): v for k, v in req.headers.items()}

            for param in self.headers:
                self.headers[param] = str(self.headers[param])

            # Remove content length and cookies from headers
            if "cookie" in self.headers:
                self.headers.pop("cookie")

            if "content-length" in self.headers:
                self.headers.pop("content-length")

    async def _getRequest(
        self, username_element, password_element, page, username, password
    ) -> None:

        await page.fill("input[name=" + username_element + "]", username)
        await page.fill("input[name=" + password_element + "]", password)

        logging.info("username_element: " + str(username_element))
        logging.info("password_element: " + str(password_element))

        page.once("request", self._getRequestData)
        await page.locator(self.button_attr).click()
        content = await page.content()
        self._wait()

        self.contentLen = len(str(content))

    def _wait(self):
        while self.headers == None:
            time.sleep(1)

    def formScore(self, form, button, buttonList, loginTexts) -> float:
        """
        Gives each form a score on how likely it being the login
        form based on the form's button id, name, value, the forms structure and texts
        found in the form such as "login" or "sign in"
        """

        buttonValueScore = 0
        buttonNameScore = 0
        buttonIdScore = 0
        score = 0
        if "value" in button:
            buttonValueScore = self._similarity_value(button["value"], buttonList)
        if "name" in button:
            buttonNameScore = self._similarity_value(button["name"], buttonList)
        if "id" in button:
            buttonIdScore = self._similarity_value(button["id"], buttonList)
        buttonTextScore = self._similarity_value(button.text, buttonList)

        button_score = max(
            buttonValueScore, buttonTextScore, buttonNameScore, buttonIdScore
        )

        if button_score == 1:
            return 10

        score += button_score

        for label in loginTexts:
            if label in str(form.text).lower():
                score += 0.3

        inputs = []
        for inp in form.findChildren("input"):
            if (
                inp["type"] == "text"
                or inp["type"] == "email"
                or inp["type"] == "password"
            ):
                inputs.append(inp)

        if len(inputs) < 2:
            return 0

        if len(form.findChildren("input", {"type": "password"})) == 1:
            score += 0.5
        if len(form.findChildren("input", {"type": "email"})) == 1:
            score += 0.3
        return score

    def findForm(self, forms, buttonList, loginTexts):
        """
        Picks the form with highest score
        """

        maxScore = 0
        for form in forms:
            buttons = form.findChildren(attrs={"type": "submit"})
            if len(buttons) == 0:
                buttons = form.findChildren(attrs={"type": "Button"})

            for button in buttons:
                score = self.formScore(form, button, buttonList, loginTexts)
                if score > maxScore:
                    maxScore = score
                    pickedForm = form
                    self.buttonLocator(button)

        return pickedForm

    def buttonLocator(self, button) -> None:
        """
        Build a string locator based on the button element's attributes
        """
        button_att = button.name
        for k in button.attrs:
            if k != "style":
                attr = button[k]
                if isinstance(button[k], list):
                    attr = str(" ".join(button[k]))
                button_att += "[" + k + "=" + attr.replace(" ", "\ ") + "]"
        self.button_attr = button_att

    def _get_req_type(self) -> str:
        """Get content type from headers"""
        type = self.headers["content-type"]

        if "json" in type:
            return "JSON"

        elif "xml" in type:
            return "XML"

        elif "multipart" in type:
            return "multipart"

        else:
            return "URL_ENCODED"

    def _pass_gen(self) -> str:
        """
        Generate strong password randomly
        """
        char_seq = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!#$%&'()*+,-./:;<=>?@[\]^_`{|}~"
        password = ""
        for len in range(10):
            random_char = random.choice(char_seq)
            password += random_char

        list_pass = list(password)
        random.shuffle(list_pass)
        final_password = "".join(list_pass)
        return final_password

    def _pick_param(self, inputs, list):
        """ "Param with max potential for being the username or password"""
        inputName = max(inputs, key=lambda x: self._similarity_value(x, list))
        return inputName

    def _jaccard_similarity(self, a, b):
        # Convert to set
        a = set(a)
        b = set(b)
        # calucate jaccard similarity
        j = float(len(a.intersection(b))) / len(a.union(b))
        return j

    def _similarity_value(self, param, usernames):
        if not param:
            return 0
        max = 0
        for uname in usernames:
            score = self._jaccard_similarity(param.lower(), uname)
            if score > max:
                max = score
        return max
