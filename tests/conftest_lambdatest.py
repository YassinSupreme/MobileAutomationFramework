from pathlib import Path
import allure
import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
import datetime
from utils.config import get_lambdatest_config
import requests
import time

driver = None


# Simulating a scenario where the Appium driver is not initialized
class AppiumDriverNotInitializedError(Exception):
    def __init__(self, message="Appium driver is not initialized"):
        super().__init__(message)


def upload_app_to_lambdatest(app_path, retries=3, backoff_seconds=2):
    """
    Upload APK to LambdaTest and get app_url
    """
    config = get_lambdatest_config()
    username = config["username"]
    access_key = config["access_key"]
    
    # LambdaTest app upload API endpoint
    url = "https://manual-api.lambdatest.com/app/upload"
    files = {
        "appFile": (Path(app_path).name, open(app_path, "rb"), "application/octet-stream"),
    }

    for attempt in range(1, retries + 1):
        response = requests.post(url, files=files, auth=(username, access_key))
        if response.status_code in (200, 201):
            data = response.json()
            app_url = data.get("app_url") or data.get("appId") or data.get("app_id")
            if app_url:
                print(f"App uploaded successfully. App URL: {app_url}")
                return app_url
        print(f"Upload attempt {attempt} failed ({response.status_code}). Retrying...")
        time.sleep(backoff_seconds * attempt)
    print(f"Failed to upload app after {retries} attempts. Last response: {response.text}")
    raise Exception("Failed to upload app to LambdaTest")


@pytest.fixture(scope="function")
def setup(request):
    global driver
    config = get_lambdatest_config()
    
    options = UiAutomator2Options()
    
    # LambdaTest capabilities
    options.platform_name = "Android"
    options.device_name = config["device_name"]
    options.platform_version = config["platform_version"]
    app_url = (config.get("app_url") or "").strip()
    upload_strategy = (config.get("upload_strategy") or "auto").strip().lower()
    if app_url:
        options.app = app_url
        print(f"Using pre-uploaded app: {app_url}")
    elif upload_strategy == "auto":
        options.app = upload_app_to_lambdatest("app/android/General-Store.apk")
    else:
        raise Exception("upload_strategy=skip but no app_url provided in config")
    
    # Test configuration
    options.lt_project = config["project_name"]
    options.lt_build = config["build_name"]
    
    # LambdaTest credentials and grid URL
    username = config["username"]
    access_key = config["access_key"]
    grid_url = config["grid_url"]
    
    # Create the complete grid URL with credentials
    complete_url = f"https://{username}:{access_key}@{grid_url.replace('https://', '')}"
    
    print(f"Connecting to LambdaTest: {grid_url}")
    
    driver = webdriver.Remote(complete_url, options=options)
    driver.implicitly_wait(10)
    
    request.cls.driver = driver
    
    yield
    
    if driver:
        driver.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):
    """
    Extends the PyTest Plugin to take and embed screenshot in html report, whenever test fails.
    :param item:
    """
    pytest_html = item.config.pluginmanager.getplugin("html")
    outcome = yield
    report = outcome.get_result()
    extra = getattr(report, "extra", [])
    # Generate a timestamp in the format YYYY-MM-DD_HH-MM-SS
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%I-%M-%S-%p")

    if report.when == "call" or report.when == "setup":
        xfail = hasattr(report, "wasxfail")
        if (report.skipped and xfail) or (report.failed and not xfail):
            file_name = (report.nodeid.replace("::", "_")).replace(
                "/", "_"
            ) + f"_{timestamp}.png"
            SS_PATH = Path(__file__).parent.parent / "reports/screenshots/failed"
            SS_PATH.mkdir(parents=True, exist_ok=True)
            
            _capture_screenshot(SS_PATH / file_name)
            
            if file_name:
                image_path = SS_PATH / file_name
                try:
                    if driver is None:
                        raise AppiumDriverNotInitializedError
                    allure.attach(driver.get_screenshot_as_png())
                except AppiumDriverNotInitializedError as e:
                    print(f"An error occurred: {e}")

                # Encode the path to HTML-safe format
                encoded_path = image_path.as_uri()
                html = (
                    f'<div><img src="{encoded_path}" alt="screenshot" style="width:150px;height:300px;" '
                    'onclick="window.open(this.src)" align="right"/></div>'
                )
                extra.append(pytest_html.extras.html(html))
        report.extras = extra


def _capture_screenshot(name):
    try:
        if driver is None:
            raise AppiumDriverNotInitializedError
        driver.get_screenshot_as_file(name)
    except AppiumDriverNotInitializedError as e:
        print(f"An error occurred: {e}")


def pytest_exception_interact(node, call, report):
    """
    Pending Implementation: Setup API response (request & response) data in Log
    """
    if report.failed:
        test_name = node.name  # Get the name of the test
        test_file = node.parent.nodeid  # Get the test file path

        exception_info = call.excinfo  # Get the ExceptionInfo instance
        exception_type = exception_info.type
        exception_value = exception_info.value

        print(f"Test Name: {test_name}")
        print(f"Test File: {test_file}")
        print(f"Exception Type: {exception_type}")
        print(f"Exception Value: {exception_value}")

