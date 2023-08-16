from selenium import webdriver, common
from selenium.webdriver.common.by import By
from backoff import expo, on_exception, on_predicate
from typing import Callable
from logging import DEBUG, basicConfig, debug
from random import randint
from time import sleep


def function_logger(function: Callable):
    function_name = function.__name__
    from functools import wraps

    @wraps(function)
    def function_logger_inner(*args, **kwargs):
        debug(function_name + f" start with args: {args} and kwargs: {kwargs}")
        try:
            return function(*args, **kwargs)
        finally:
            debug(function_name + " end")

    return function_logger_inner


exceptions = common.exceptions
StaleElementReferenceException = exceptions.StaleElementReferenceException
on_stale_element_reference_exception = on_exception(
    wait_gen=expo, exception=StaleElementReferenceException
)


@function_logger
def find_buttons_by_text(web_element, text):
    return (
        button
        for button in web_element.find_elements(By.CLASS_NAME, "semi-button-content")
        if button.text == text
    )


@function_logger
def safe_click(web_element, text):
    before_clicked = True

    @function_logger
    def predicate(buttons):
        return before_clicked or buttons  # 兩個條件有一符合就是True。

    @on_predicate(wait_gen=expo, predicate=predicate)
    @function_logger
    def main_loop():
        try:
            if buttons := list(find_buttons_by_text(web_element, text)):
                buttons[0].click()
                nonlocal before_clicked
                before_clicked = False  # 點完後變成false
            return buttons
        except StaleElementReferenceException:
            debug(StaleElementReferenceException)
        except exceptions.ElementClickInterceptedException:
            debug(exceptions.ElementClickInterceptedException)
        except exceptions.WebDriverException:
            debug(exceptions.ElementClickInterceptedException)

    main_loop()


basicConfig(level=DEBUG)
driver = webdriver.Edge()
try:
    while True:
        driver.get("http://calctest.nchu.edu.tw/")
        driver.find_element(By.ID, "email").send_keys("yuttai@nchu.edu.tw")
        from tkinter import simpledialog, messagebox
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

    @on_predicate(wait_gen=expo, predicate=lambda x: not x)
    @function_logger
    def find_non_empty_elements_by_tag_name():
        return driver.find_elements(By.TAG_NAME, "tr")

    @function_logger
    def add_one_exam():
        """
        自動新增考試(雖然目前還無法完全自動)
        """
        exam_name = str(randint(0, 999999))
        safe_click(driver, "新增考試")
        sleep(2)
        driver.find_element(
            By.ID,
            "name",
        ).send_keys(exam_name)
        # 以下--------內的幾行目前是失敗的，根本沒反應，所以就人工點一點吧😂
        # -------------------------------------------------------------------------------------
        driver.find_element(
            By.XPATH,
            "/html/body/div[5]/div/div[2]/div/div/div[2]/form/div[2]/div/div/div/div[1]/div/input",
        ).send_keys("2023-01-01 00:00:00")

        driver.find_element(
            By.XPATH,
            "/html/body/div[5]/div/div[2]/div/div/div[2]/form/div[2]/div/div/div/div[2]/div/input",
        ).send_keys("2050-12-31 23:59:00")

        driver.find_element(
            By.XPATH,
            "/html/body/div[6]/div/div[2]/div/div/div[2]/form/div[3]/div/div/div[1]/input",
        ).send_keys("180")

        driver.find_element(By.XPATH, "//*[contains(text(),確認新增)]").click()
        # -------------------------------------------------------------------------------------

    safe_click(driver, "登入")

    course = simpledialog.askstring("course name", "Please enter a course📚:")
    if course == "":
        course = "Test"
    on_stale_element_reference_exception(
        lambda: next(
            div
            for div in driver.find_elements(By.TAG_NAME, "div")
            if course == div.text
        ).click()
    )()
    add_one_exam()
finally:
    driver.quit()
