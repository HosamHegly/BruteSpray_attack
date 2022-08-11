import logging
from bs4 import BeautifulSoup


def check_login(post_response, status_code, web_parser) -> bool:
    """
    checks if login was successful by checking if status code changed and checks if form is still in the page
    """
    
    logging.info("[check_login] Status code!: " + str(status_code))

    if status_code >= 400:
        logging.info(
            "[check_login] Status code changed and its >= 400 ! : " + str(status_code)
        )
        return False
    elif status_code != web_parser.status_code:
        logging.info("[check_login] Status code changed!: " + str(status_code))
        return True

    from html_similarity import style_similarity, structural_similarity, similarity

    k = 0.3
    parser = BeautifulSoup(post_response, "html.parser")
    forms = parser.findAll("form")
    webParser_form = web_parser.form
    max_similarity = 0
    for web_form in forms:
        similarity = k * structural_similarity(str(webParser_form), str(web_form)) + (
            1 - k
        ) * style_similarity(str(webParser_form), str(web_form))
        if similarity > max_similarity:
            max_similarity = similarity
    logging.info(" max_similarity: " + str(max_similarity))
    if max_similarity < 0.8:
        logging.info("[check_login] max_similarity: " + str(max_similarity))
        return True

    return False
