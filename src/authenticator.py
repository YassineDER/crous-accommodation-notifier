import logging
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, parse_qs

from src.settings import Settings

settings = Settings()

logger = logging.getLogger(__name__)


class Authenticator:
    """Class that handles the authentication to the CROUS website and returns a WebDriver object that is authenticated."""

    def __init__(self, email: str, password: str, delay: int = 2):
        self.email = email
        self.password = password
        self.delay = delay

    def authenticate_driver(self, driver: WebDriver) -> None:
        """Authenticates the given WebDriver object to the CROUS website."""

        logger.info("Authenticating to the CROUS website...")

        sleep(self.delay)

        # Step 1: Go to the initial login page (will redirect with a fresh login_challenge)
        logger.info(f"Going to the initial login page: {settings.MSE_INITIAL_LOGIN_URL}")
        driver.get(settings.MSE_INITIAL_LOGIN_URL)

        # Wait for redirect to URL that contains the login_challenge parameter
        try:
            WebDriverWait(driver, 15).until(EC.url_contains("login_challenge="))
            current_url = driver.current_url
            parsed = urlparse(current_url)
            challenge = parse_qs(parsed.query).get("login_challenge", [None])[0]
            if challenge:
                logger.info(f"Obtained login_challenge token: {challenge}")
        except Exception:
            logger.warning("Did not detect login_challenge in URL within timeout; continuing anyway")
        sleep(self.delay)

        # Step 2: choose the correct authentication method
        logger.info("Choosing the correct authentication method")
        mse_connect_button = driver.find_element(By.CLASS_NAME, "loginapp-button")
        # mse_connect_button.click() # somehow doesn't work. We simulate a click instead :
        driver.execute_script("arguments[0].click();", mse_connect_button)
        sleep(self.delay)

        # Step 3: Input credentials and submit
        logger.info("Inputting credentials")
        username_input = driver.find_element(By.ID, "login_login")
        password_input = driver.find_element(By.ID, "login_password")

        username_input.send_keys(self.email)
        password_input.send_keys(self.password)

        logger.info("Submitting the form")
        password_input.send_keys(Keys.RETURN)

        sleep(self.delay)

        # Step 4: Validate the rules
        # self._validate_rules(driver)

        # Step 5: Force update the auth status
        driver.get("https://trouverunlogement.lescrous.fr/mse/discovery/connect")

        # Done
        logger.info("Successfully authenticated to the CROUS website")

    def _validate_rules(self, driver: WebDriver) -> None:
        """Validates the rules of the CROUS website."""
        logger.info("Validating the rules of the CROUS website")

        driver.get("https://trouverunlogement.lescrous.fr/tools/42/rules")

        sleep(self.delay)

        # <button class="fr-btn" type="submit" name="searchSubmit">Passer à la recherche de logements</button>

        validate_button = driver.find_element(By.NAME, "searchSubmit")

        validate_button.click()

        sleep(self.delay)
