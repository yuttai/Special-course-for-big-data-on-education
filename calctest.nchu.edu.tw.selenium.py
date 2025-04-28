# https://medium.com/marketingdatascience/selenium%E6%95%99%E5%AD%B8-%E4%B8%80-%E5%A6%82%E4%BD%95%E4%BD%BF%E7%94%A8webdriver-send-keys-988816ce9bed
# https://medium.com/marketingdatascience/%E5%8B%95%E6%85%8B%E7%B6%B2%E9%A0%81%E7%88%AC%E8%9F%B2%E7%AC%AC%E4%BA%8C%E9%81%93%E9%8E%96-selenium%E6%95%99%E5%AD%B8-%E5%A6%82%E4%BD%95%E4%BD%BF%E7%94%A8find-element-s-%E5%8F%96%E5%BE%97%E7%B6%B2%E9%A0%81%E5%85%83%E7%B4%A0-%E9%99%84python-%E7%A8%8B%E5%BC%8F%E7%A2%BC-b66920fc8cab
from selenium.webdriver import EdgeOptions
from logging import debug
from tkinter import simpledialog
from main import open_web, function_logger, find_elements_by_text, on_stale_element_reference_exception, \
    safe_click_element, safe_click_button, find_elements_by_tag_name
from time import sleep

options = EdgeOptions()
options.add_experimental_option("prefs", {
    "download.default_directory": r"C:\Users\Public\Documents\StudyInIUB\Computer Science\career\國立中興大學\\線上測驗系統成績"})
driver = open_web(options=options)
try:
    @function_logger
    def click_next(iterator):
        return next(iterator).click()

    @function_logger
    def click_elements_by_text(web_element, value, text):
        return click_next(find_elements_by_text(web_element, value, text))

    @on_stale_element_reference_exception
    @function_logger
    def get_exam_tr(exam_name):
        for exam_tr in find_elements_by_tag_name(driver, "tr"):
            debug(exam_tr)
            if exam_name in exam_tr.text and any(find_elements_by_text(exam_tr, "semi-typography-link-text", exam_name)):
                # 之所以先判斷 exam_name in exam_tr.text 是因為這比 any 快很多
                return exam_tr
    while exam_name_ := simpledialog.askstring(
            "exam name",
            "Please enter the exam name we need to grade..."):
        exam_tr_ = get_exam_tr(exam_name_)
        if not exam_tr_:
            continue

        @on_stale_element_reference_exception
        @function_logger
        def grade_one_student():
            for answer_tr in find_elements_by_tag_name(driver, "tr"):
                text = answer_tr.text
                debug(text)
                if "未批改試卷" not in text:
                    continue
                safe_click_button(answer_tr, "批改答卷")
                safe_click_button(driver, "確認儲存評分")
                return True
            return False

        safe_click_button(exam_tr_, "檢視答卷")
        while grade_one_student():
            pass
        sleep(1)
        click_elements_by_text(driver, "semi-button-content", "匯出結果")
        click_elements_by_text(driver, "semi-navigation-item-text", "考試")
        exam_tr_ = get_exam_tr(exam_name_)
        if not exam_tr_:
            continue
        safe_click_element(exam_tr_, "semi-typography-link-text", exam_name_)
        safe_click_button(driver, "預覽試卷")
        sleep(1)
        click_elements_by_text(driver, "semi-button-content", "列印試卷")
        click_elements_by_text(driver, "semi-navigation-item-text", "考試")
    driver.quit()
finally:
    # 在這裡加上driver.quit()的原因是因為如果沒加的話，當程式出錯時網頁還會存在，但是想要再次執行時，如果沒有把網頁關掉的話
    # 會出問題，所以才在finally加上driver.quit()，這樣在程式出錯的時候，就可以先執行finally的程式碼，然後才會報錯。
    # 如果想要debug，那就把driver.quit()移到try的最後一行，並且在finally裡加上pass讓finally運作，因為finally不能為空，
    # 不然程式會把網頁關掉，就不能debug了。
    # driver.quit()
    pass
