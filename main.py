import argparse
import logging
from typing import List

import telepot
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.remote.webdriver import WebDriver

from src.authenticator import Authenticator
from src.parser import Parser
from src.models import UserConf
from src.notification_builder import NotificationBuilder
from src.settings import Settings
from src.telegram_notifier import TelegramNotifier

logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.INFO,
)
logger = logging.getLogger("accommodation_notifier")


def load_users_conf() -> List[UserConf]:
    bounds = "4.686130820251236_45.92775190489084_5.069965659118424_45.52655459432095"  # Nantes area
    return [
        UserConf(
            conf_title="Me",
            telegram_id=settings.MY_TELEGRAM_ID,
            search_url=f"https://trouverunlogement.lescrous.fr/tools/42/search?bounds={bounds}",  # type:ignore
            # search_url="https://trouverunlogement.lescrous.fr/tools/42/search",  # type:ignore
            ignored_ids=[2755],
        )
    ]


def create_driver(browser: str = "chrome", headless: bool = True) -> WebDriver:
    """Create a Selenium WebDriver using Selenium Manager-managed drivers.

    browser: 'chrome' or 'firefox'
    headless: run without opening a visible browser window
    """
    browser = browser.lower()
    if browser == "firefox":
        ff_options = FirefoxOptions()
        if headless:
            logging.info("Running Firefox in headless mode")
            ff_options.add_argument("-headless")
        else:
            logging.info("Running Firefox in non-headless mode")
        # Create Firefox driver (Selenium Manager will resolve geckodriver)
        return webdriver.Firefox(options=ff_options)
    elif browser == "chrome":
        ch_options = ChromeOptions()
        if headless:
            logging.info("Running Chrome in headless mode")
            ch_options.add_argument("--headless=new")
            ch_options.add_argument("--disable-gpu")
        else:
            logging.info("Running Chrome in non-headless mode")

        ch_options.add_argument("--disable-dev-shm-usage")
        ch_options.add_argument("--no-sandbox")
        # Create Chrome driver (Selenium Manager will resolve chromedriver)
        return webdriver.Chrome(options=ch_options)
    else:
        raise ValueError("Unsupported browser. Use 'chrome' or 'firefox'.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the script in headless mode or not."
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Run the script without headless mode",
    )
    parser.add_argument(
        "--browser",
        choices=["chrome", "firefox"],
        default="chrome",
        help="Browser to use for Selenium (default: chrome)",
    )

    args = parser.parse_args()

    settings = Settings()
    bot = telepot.Bot(token=settings.TELEGRAM_BOT_TOKEN)
    bot.getMe()  # test if the bot is working

    user_confs = load_users_conf()

    notification_builder = NotificationBuilder()
    notifier = TelegramNotifier(bot)

    while True:
        try:
            # Fresh driver and authentication every cycle
            driver = create_driver(browser=args.browser, headless=not args.no_headless)
            try:
                Authenticator(settings.MSE_EMAIL, settings.MSE_PASSWORD).authenticate_driver(driver)

                parser = Parser(driver)

                for conf in user_confs:
                    logging.info(f"Handling configuration : {conf}")
                    search_results = parser.get_accommodations(conf.search_url)  # type: ignore
                    notification = notification_builder.search_results_notification(search_results)
                    if notification:
                        notifier.send_notification(conf.telegram_id, notification)
            finally:
                # Always close the driver before sleeping / next cycle
                driver.quit()

            logging.info(
                f"Sleeping {settings.POLL_INTERVAL_SECONDS}s before next check..."
            )
            import time
            time.sleep(settings.POLL_INTERVAL_SECONDS)
        except Exception:
            logger.exception("Error during polling loop; stopping.")
            break
