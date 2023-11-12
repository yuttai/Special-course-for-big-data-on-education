from selenium import webdriver, common
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from backoff import expo
from logging import DEBUG, basicConfig
from random import randint
from tkinter import simpledialog
from time import sleep
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
    def add_one_exam():
        """
        自動新增考試(雖然目前還無法完全自動)
        """
        exam_name = str(randint(0, 999999))
        main.safe_click(driver, "新增考試")
        sleep(2)
        driver.find_element(
            By.ID,
            "name",
        ).send_keys(exam_name)
        # 以下--------內的幾行目前是失敗的，根本沒反應，所以就人工點一點吧😂
        # 2023/11/12更新 已經改好了可以動新增新的考試
        # -------------------------------------------------------------------------------------
        def delete_motion(element):
            element.send_keys(Keys.CONTROL,"a")
            element.send_keys(Keys.DELETE)

        date_start = driver.find_elements(By.CLASS_NAME,"semi-input.semi-input-small")[0]
        date_end = driver.find_elements(By.CLASS_NAME,"semi-input.semi-input-small")[1]
        
        date_start.click()
        delete_motion(date_start)
        date_start.click()
        delete_motion(date_end)
        date_start.send_keys("2024-11-10 15:00:00")
        date_end.send_keys("2050-12-31 23:59:00")

        driver.find_elements(By.CLASS_NAME, "semi-button.semi-button-primary")[-1].click()
        test_time = driver.find_element(By.ID, "limitMinutes")
        test_time.click()
        delete_motion(test_time)
        test_time.send_keys("180")

        driver.find_elements(By.CLASS_NAME, "semi-button.semi-button-primary")[-1].click()
        # -------------------------------------------------------------------------------------

    main.safe_click(driver, "登入")

    course = simpledialog.askstring("course name", "Please enter a course📚:")
    if course == "":
        course = "Test"
    main.on_stale_element_reference_exception(
        lambda: next(
            div
            for div in driver.find_elements(By.TAG_NAME, "div")
            if course == div.text
        ).click()
    )()
    add_one_exam()
finally:
    driver.quit()
