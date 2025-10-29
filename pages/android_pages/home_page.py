import datetime
import re
import inspect
import time
from pathlib import Path
from seleniumpagefactory.Pagefactory import PageFactory
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from utils.locators.android_locators import (
    HomePageLocator,
    LoginPageLocator,
    CommonLocator,
)
from utils.common import get_logger
from utils.data import TestData


class HomePage(PageFactory):
    def __init__(self, driver):
        super().__init__()
        self.driver = driver
        self.home_locator = HomePageLocator
        self.login_locator = LoginPageLocator
        self.common_locator = CommonLocator
        self.default_wait_seconds = 30

    def page_factory_test(self):
        self.driver.double_click()

    def wait(self, method, locator):
        """Wait until an element is present using the given method and locator string."""
        wait = WebDriverWait(self.driver, self.default_wait_seconds)
        wait.until(EC.presence_of_element_located((method, locator)))

    def wait_for_presence(self, locator_tuple, timeout=None):
        """Wait for presence of element located by a locator tuple (By, value)."""
        wait = WebDriverWait(self.driver, timeout or self.default_wait_seconds)
        return wait.until(EC.presence_of_element_located(locator_tuple))

    def wait_for_visible(self, locator_tuple, timeout=None):
        """Wait for visibility of element located by a locator tuple (By, value)."""
        wait = WebDriverWait(self.driver, timeout or self.default_wait_seconds)
        return wait.until(EC.visibility_of_element_located(locator_tuple))

    def capture_screenshot(self):
        """
        Capture SS For Particular Page. Naming Convention generated with timestamp, folder, file, class name

        Returns:
            None
        """
        current_frame = inspect.currentframe()
        caller_frame = inspect.getouterframes(current_frame, 2)[1][0]

        # Get test case function name and class name
        function_name = caller_frame.f_code.co_name
        class_name = self.__class__.__name__

        # Get Python file name
        file_name = Path(caller_frame.f_globals["__file__"]).name

        # Get the folder name of the calling script
        script_path = Path(caller_frame.f_globals["__file__"])
        calling_folder_name = script_path.parent.name

        # Generate timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%I-%M-%S-%p")

        # Generate screenshot file name
        screenshot_name = f"{calling_folder_name}_{file_name}_{class_name}_{function_name}_{timestamp}.png"

        # Construct screenshot file path
        SS_PATH = Path(__file__).parent.parent.parent / "reports/screenshots/passed"
        screenshot_path = SS_PATH / screenshot_name

        # Ensure directory exists and take the screenshot
        SS_PATH.mkdir(parents=True, exist_ok=True)
        self.driver.get_screenshot_as_file(screenshot_path)

    def scroll_to_text(self, txt):
        """
        This method help with scroll to defined text
        :return:
        """
        scroll_expression = (
            f"new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView("
            f'new UiSelector().text("{txt}"))'
        )
        self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, scroll_expression)

    def clear_amount(self, price_str):
        """Normalize price string like "$1,234.50" to float 1234.50. Returns None on error."""
        cleaned = re.sub(r"[^\d\.]", "", price_str or "")
        try:
            return float(cleaned) if cleaned else None
        except ValueError:
            return None

    def check_home_page_elements(self):
        """
        This method checks if all the elements on the home page are visible
        :return:
        """
        try:
            self.wait_for_visible((AppiumBy.ID, self.home_locator.logo))
            self.wait_for_visible((AppiumBy.ID, self.home_locator.balance))
            return True
        except Exception:
            return False

    def filling_form(self, country, name, gender):
        driver = self.driver
        log = get_logger()
        driver.find_element(*self.login_locator.COUNTRY_DROPDOWN).click()
        self.scroll_to_text(country)
        self.driver.find_element(
            By.XPATH, self.login_locator.select_country(country)
        ).click()
        driver.find_element(*self.login_locator.NAME_FIELD).send_keys(name)
        driver.hide_keyboard()
        self.driver.find_element(
            By.XPATH, self.login_locator.select_gender(gender)
        ).click()
        driver.find_element(*self.login_locator.LETS_SHOP).click()
        log.info("Successfully Filled The Form & Proceed To Shopping")

    def validating_blank_name_error_message(self):
        driver = self.driver
        log = get_logger()
        driver.find_element(*self.login_locator.COUNTRY_DROPDOWN).click()
        self.scroll_to_text(TestData.COUNTRY)
        self.driver.find_element(
            By.XPATH, self.login_locator.select_country(TestData.COUNTRY)
        ).click()
        self.driver.find_element(
            By.XPATH, self.login_locator.select_gender(TestData.GENDER)
        ).click()
        driver.find_element(*self.login_locator.LETS_SHOP).click()
        err_msg = driver.find_element(*self.common_locator.TOAST_MESSAGE).text
        assert TestData.ERR_MSG in err_msg
        log.info(f"Successfully Validated, {err_msg}")

    def shopping(self):
        log = get_logger()
        self.filling_form(TestData.COUNTRY, TestData.NAME, TestData.GENDER)
        self.scroll_to_text(TestData.PRODUCT_ONE)
        self.driver.find_element(
            By.XPATH, self.home_locator.product_add_to_cart(TestData.PRODUCT_ONE)
        ).click()
        self.driver.find_element(*self.home_locator.CART_BUTTON).click()
        wait = WebDriverWait(self.driver, self.default_wait_seconds)
        wait.until(
            EC.text_to_be_present_in_element(self.home_locator.CART_TITLE, "Cart")
        )

        # validating product name
        product_name = self.driver.find_element(*self.home_locator.PRODUCT_NAME).text
        assert TestData.PRODUCT_ONE in product_name

        # validating product price
        product_price = self.driver.find_element(*self.home_locator.TOTAL_AMOUNT).text
        assert TestData.PRODUCT_ONE_PRICE in product_price
        log.info(f"Successfully Added Product, {product_name}, Price: {product_price}")

    def validating_cart_price(self):
        log = get_logger()
        self.filling_form(TestData.COUNTRY, TestData.NAME, TestData.GENDER)
        self.scroll_to_text(TestData.PRODUCT_ONE)
        self.driver.find_element(
            By.XPATH, self.home_locator.product_add_to_cart(TestData.PRODUCT_ONE)
        ).click()
        self.scroll_to_text(TestData.PRODUCT_TWO)
        self.driver.find_element(
            By.XPATH, self.home_locator.product_add_to_cart(TestData.PRODUCT_TWO)
        ).click()
        log.info(
            f"Successfully Added Product, {TestData.PRODUCT_ONE} & {TestData.PRODUCT_TWO} into Cart"
        )
        self.capture_screenshot()
        self.driver.find_element(*self.home_locator.CART_BUTTON).click()

        wait = WebDriverWait(self.driver, self.default_wait_seconds)
        wait.until(
            EC.text_to_be_present_in_element(self.home_locator.CART_TITLE, "Cart")
        )
        prices = self.driver.find_elements(*self.home_locator.PRODUCT_PRICE)
        count = 0
        for price in prices:
            clean_price = self.clear_amount(price.text)
            count += clean_price
        log.info(f"Total Counted Price is {count}")

        # validating product price
        total_price = self.driver.find_element(*self.home_locator.TOTAL_AMOUNT).text
        assert count == self.clear_amount(total_price)
        log.info(f"Validated Total Price: {total_price} with count: {count}")
        self.capture_screenshot()

        terms_and_conditions = self.driver.find_element(
            *self.home_locator.TERMS_AND_CONDITIONS_BUTTON
        )
        self.driver.execute_script(
            "mobile: longClickGesture",
            {"elementId": terms_and_conditions.id, "duration": 2000},
        )
        alert_title = self.driver.find_element(
            *self.home_locator.TERMS_AND_CONDITIONS_BUTTON_TITLE
        ).text
        assert TestData.TOC_TITLE == alert_title
        log.info(f"Validated Terms Of Conditions, {alert_title}")
        self.capture_screenshot()

        self.driver.find_element(*self.common_locator.OK).click()
        self.driver.find_element(*self.home_locator.CHECKBOX).click()
        self.driver.find_element(*self.home_locator.PROCEED_BUTTON).click()

        # Switching To Webview
        web_view = (By.ID, "com.androidsample.generalstore:id/webView")
        wait.until(EC.presence_of_element_located(web_view))
        # Allow the webview context to appear then switch by name
        time.sleep(2)
        contexts = self.driver.contexts
        webview_context = next((c for c in contexts if "WEBVIEW" in c), None)
        if webview_context:
            self.driver.switch_to.context(webview_context)
        else:
            raise AssertionError("WEBVIEW context not found after navigating to web view")
        time.sleep(1)
        self.driver.find_element(By.XPATH, "//*[@name='q']").send_keys(
            "Hello Appium !!!"
        )
        self.driver.find_element(By.XPATH, "//*[@name='q']").send_keys(Keys.ENTER)
        log.info("Validated Apps Webview")
        self.capture_screenshot()

        # Switching Back To App
        self.driver.press_keycode(4)
        self.driver.switch_to.context("NATIVE_APP")
        self.driver.find_element(*self.login_locator.GENDER).click()
        log.info("Validated Apps Native Interaction")
        self.capture_screenshot()
