# https://medium.com/marketingdatascience/selenium%E6%95%99%E5%AD%B8-%E4%B8%80-%E5%A6%82%E4%BD%95%E4%BD%BF%E7%94%A8webdriver-send-keys-988816ce9bed
# https://medium.com/marketingdatascience/%E5%8B%95%E6%85%8B%E7%B6%B2%E9%A0%81%E7%88%AC%E8%9F%B2%E7%AC%AC%E4%BA%8C%E9%81%93%E9%8E%96-selenium%E6%95%99%E5%AD%B8-%E5%A6%82%E4%BD%95%E4%BD%BF%E7%94%A8find-element-s-%E5%8F%96%E5%BE%97%E7%B6%B2%E9%A0%81%E5%85%83%E7%B4%A0-%E9%99%84python-%E7%A8%8B%E5%BC%8F%E7%A2%BC-b66920fc8cab
from selenium import webdriver, common
from backoff import expo, on_exception, on_predicate
from typing import Callable
from logging import DEBUG, basicConfig, debug


def function_logger(function: Callable):
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


@function_logger
def find_buttons_by_text(web_element, text):
    return (button for button in web_element.find_elements_by_class_name("semi-button-content") if button.text == text)


@function_logger
def safe_click(web_element, text):
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


basicConfig(level=DEBUG)
driver = webdriver.Edge()
try:
    while True:
        driver.get('http://calctest.nchu.edu.tw/')
        driver.find_element_by_id("email").send_keys("yuttai@nchu.edu.tw")
        from tkinter import simpledialog, messagebox
        from ctypes import windll
        # driver.find_element_by_id("password").send_keys()
        # https://stackoverflow.com/questions/2963263/how-can-i-create-a-simple-message-box-in-python/15275420
        # https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-messageboxw
        match windll.user32.MessageBoxW(
                0,
                'Please enter the password in the website, and press Continue. Or press retry if you want to start over again...',
                'password',
                6):  # MB_CANCELTRYCONTINUE
            case 2:  # IDCANCEL
                exit()
            case 11:  # IDCONTINUE
                break

    @on_predicate(wait_gen=expo, predicate=lambda x: not x)
    @function_logger
    def find_non_empty_elements_by_tag_name():
        return driver.find_elements_by_tag_name("tr")

    @function_logger
    def grade_one_exam(exam_name):
        for exam_tr in find_non_empty_elements_by_tag_name():
            debug(exam_tr)
            if exam_name not in exam_tr.text:
                continue
            if not any(
                    link_text.text == exam_name
                    for link_text in exam_tr.find_elements_by_class_name('semi-typography-link-text')):
                continue

            @on_stale_element_reference_exception
            @function_logger
            def grade_one_student():
                for answer_tr in find_non_empty_elements_by_tag_name():
                    text = answer_tr.text
                    debug(text)
                    if '未批改試卷' not in text:
                        continue
                    safe_click(answer_tr, '批改答卷')
                    safe_click(driver, '確認儲存評分')
                    return True
                return False
            next(find_buttons_by_text(exam_tr, '檢視答卷')).click()
            while grade_one_student():
                pass
            for navigation in driver.find_elements_by_class_name("semi-navigation-item-text"):
                if navigation.text == '考試':
                    navigation.click()
                    return

    safe_click(driver, '登入')
    on_stale_element_reference_exception(lambda: next(
        div
        for div in driver.find_elements_by_tag_name('div')
        if '111-1_化工系_1225' == div.text).click())()
    while exam_name_ := simpledialog.askstring('exam name', 'Please enter the exam name we need to grade...'):
        grade_one_exam(exam_name_)
finally:
    driver.quit()
