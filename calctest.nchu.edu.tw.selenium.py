# https://medium.com/marketingdatascience/selenium%E6%95%99%E5%AD%B8-%E4%B8%80-%E5%A6%82%E4%BD%95%E4%BD%BF%E7%94%A8webdriver-send-keys-988816ce9bed
# https://medium.com/marketingdatascience/%E5%8B%95%E6%85%8B%E7%B6%B2%E9%A0%81%E7%88%AC%E8%9F%B2%E7%AC%AC%E4%BA%8C%E9%81%93%E9%8E%96-selenium%E6%95%99%E5%AD%B8-%E5%A6%82%E4%BD%95%E4%BD%BF%E7%94%A8find-element-s-%E5%8F%96%E5%BE%97%E7%B6%B2%E9%A0%81%E5%85%83%E7%B4%A0-%E9%99%84python-%E7%A8%8B%E5%BC%8F%E7%A2%BC-b66920fc8cab
from selenium import webdriver
from selenium.webdriver.common.by import By
from backoff import expo
from logging import DEBUG, basicConfig, debug
from tkinter import simpledialog
import main

basicConfig(level=DEBUG)
driver = webdriver.Edge()
try:
    main.open_web(driver)

    @main.on_predicate(wait_gen=expo, predicate=lambda x: not x)
    @main.function_logger
    def find_non_empty_elements_by_tag_name():
        return driver.find_elements(By.TAG_NAME, "tr")

    @main.function_logger
    def grade_one_exam(exam_name):
        for exam_tr in find_non_empty_elements_by_tag_name():
            debug(exam_tr)
            if exam_name not in exam_tr.text:
                continue
            if not any(
                link_text.text == exam_name
                for link_text in exam_tr.find_elements(
                    By.CLASS_NAME, "semi-typography-link-text"
                )
            ):
                continue

            @main.on_stale_element_reference_exception
            @main.function_logger
            def grade_one_student():
                for answer_tr in find_non_empty_elements_by_tag_name():
                    text = answer_tr.text
                    debug(text)
                    if "未批改試卷" not in text:
                        continue
                    main.safe_click(answer_tr, "批改答卷")
                    main.safe_click(driver, "確認儲存評分")
                    return True
                return False

            next(main.find_buttons_by_text(exam_tr, "檢視答卷")).click()
            while grade_one_student():
                pass
            for navigation in driver.find_elements(
                By.CLASS_NAME, "semi-navigation-item-text"
            ):
                if navigation.text == "考試":
                    navigation.click()
                    return

    main.safe_click(driver, "登入")

    course = simpledialog.askstring("course name", "Please enter a course📚:")
    main.on_stale_element_reference_exception(
        lambda: next(
            div
            for div in driver.find_elements(By.TAG_NAME, "div")
            if course == div.text
        ).click()
    )()
    while exam_name_ := simpledialog.askstring(
        "exam name", "Please enter the exam name we need to grade..."
    ):
        grade_one_exam(exam_name_)
finally:
    driver.quit()
