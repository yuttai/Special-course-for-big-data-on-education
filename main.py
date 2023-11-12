from selenium import common
from selenium.webdriver.common.by import By
from typing import Callable
from logging import debug
from backoff import expo, on_exception, on_predicate


def function_logger(function: Callable):

    """這是一個docorator，用於印出函數的名稱及參數等資訊，以便除錯。

    主要功能為觀察函數的運作情況。
    decorator通常用@符號表示，用來修飾函數。
    它就如同微積分符號一樣，微分前後雖然有些差異，但都還是函數，只是被修飾的函數中會被添加一些使它更方便的功能。

    This is a decorator, it can be use to print out the name and parameter of a function.
    it helps people debug.
    """

    function_name = function.__name__
    from functools import wraps

    @wraps(function)
    def function_logger_inner(*args, **kwargs):
        debug(function_name + f' start with args: {args} and kwargs: {kwargs}')
        try:
            return function(*args, **kwargs)
        finally:
            debug(function_name + ' end')
    return function_logger_inner

exceptions = common.exceptions
StaleElementReferenceException = exceptions.StaleElementReferenceException
on_stale_element_reference_exception = on_exception(wait_gen=expo, exception=StaleElementReferenceException)

"""這段程式可以自動的等待一段時間再重新嘗試載入網站，它會自動加長時間間隔
(基本上指數性增加，但可能有添加一點點隨機的變化)，
確保網站完全跑出來了在執行動作。
it will try after wait some time by itself, and extend the waiting time automatically."""

@function_logger
def find_buttons_by_text(web_element, text):
    return (button for button in web_element.find_elements(By.CLASS_NAME,"semi-button-content") if button.text == text)


@function_logger
def safe_click(web_element, text):

    """用來尋找網頁中的物件並點擊。倘若失敗則會有「智慧地」嘗試。

    先尋找符合的按鈕，並點擊。如果出現異常或失敗，那麼就過一段時間再不斷嘗試。
    如果點過了會有變數儲存它的狀態，避免不小心重複點擊!
    This is a function that is used to find and click on an object in a web page.
    The function will retry if the object is not found or if the click fails.
    The function will also keep track of whether or not the object has been clicked
    so that it does not accidentally click on it multiple times.(google翻的😅)
    """

    before_clicked = True

    @function_logger
    def predicate(buttons):
        return before_clicked or buttons

    @on_predicate(wait_gen=expo, predicate=predicate)
    @function_logger
    def main_loop():
        try:
            if buttons := list(find_buttons_by_text(web_element, text)):
                buttons[0].click()
                nonlocal before_clicked
                before_clicked = False
            return buttons
        except StaleElementReferenceException:
            debug(StaleElementReferenceException)
        except exceptions.ElementClickInterceptedException:
            debug(exceptions.ElementClickInterceptedException)
        except exceptions.WebDriverException:
            debug(exceptions.ElementClickInterceptedException)
    main_loop()

def open_web(driver):
    while True:
        driver.get("http://calctest.nchu.edu.tw/")
        driver.find_element(By.ID, "email").send_keys("yuttai@nchu.edu.tw")
        from ctypes import windll

        match windll.user32.MessageBoxW(
            0,
            "Please enter the password in the website, and press Continue. Or press retry if you want to start over again...",
            "password",
            6,
        ):  # MB_CANCELTRYCONTINUE
            case 2:  # IDCANCEL
                exit()
            case 11:  # IDCONTINUE
                break
    