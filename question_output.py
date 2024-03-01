from selenium import webdriver
from selenium.webdriver.common.by import By
from backoff import expo
from logging import DEBUG, basicConfig
from tkinter import simpledialog
from time import sleep
import pandas as pd
from openpyxl.utils import get_column_letter
import main

basicConfig(level=DEBUG)
driver = webdriver.Edge()
try:
    main.open_web(driver)
    main.on_predicate(wait_gen=expo, predicate=lambda x: not x)
    main.safe_click(driver, "登入")

    @main.function_logger
    def crab_chapters_data():
        global chapter_list
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By
        from bs4 import BeautifulSoup
        # 打開網頁並執行一些操作
        main.safe_click(driver, "選擇章節")
        final_url = driver.current_url  # 或者等待某個特定元素加載完成

        # 等待直到網頁內容加載完成
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

        # 獲取網頁源代碼
        html_source = driver.page_source

        # 解析網頁內容
        soup = BeautifulSoup(html_source, 'html.parser')

        # 專注於解析第二個 table
        def extract_chapters_from_second_table(soup):
            tables = soup.find_all('table')
            if len(tables) < 2:
                return []  # 如果沒有足夠的表格，返回空列表

            second_table = tables[1]
            chapters = []
            for table_row in second_table.find_all('tr'):
                cells = table_row.find_all('td')
                if len(cells) >= 2:
                    chapter_number = cells[1].text.strip()
                    chapter_title = cells[2].text.strip()
                    chapters.append(f"{chapter_number}  {chapter_title}")
            return chapters
        
        def extract_all_chapters():
            chapters = []
            # 定位到第三個 ul 元素
            pagination_ul = driver.find_elements(By.CSS_SELECTOR, 'ul')[2]
            page_numbers = pagination_ul.find_elements(By.TAG_NAME, 'li')[1:6]

            for i in range(len(page_numbers)):
                # 點擊頁碼
                page_numbers[i].click()
                
                # 等待頁面加載
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
                
                # 提取當前頁面的章節資料
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                chapters.extend(extract_chapters_from_second_table(soup))

                # 重新定位到第三個 ul 元素並更新頁碼元素列表
                pagination_ul = driver.find_elements(By.CSS_SELECTOR, 'ul')[2]
                page_numbers = pagination_ul.find_elements(By.TAG_NAME, 'li')[1:6]


            return chapters
        
        chapter_list = extract_all_chapters()

    def ui():
        import tkinter as tk
        from tkinter import Toplevel, Frame, Checkbutton, StringVar
        global chapter_vars
        def open_selection_window():
            global chapter_vars  # 使用全局變量來保存勾選框的狀態

            selection_window = Toplevel(window)
            selection_window.title("選擇章節")
            selection_window.geometry("+{}+{}".format(window.winfo_x() + 200, window.winfo_y() + 50))

            chapters_per_page = 10
            total_chapters = 48
            options = chapter_list

            pages = []
            chapter_vars = {}
            for i in range(0, total_chapters, chapters_per_page):
                frame = Frame(selection_window)
                pages.append(frame)
                for j in range(i, min(i + chapters_per_page, total_chapters)):
                    var = StringVar(value="0")
                    if options[j] in selected_options:  # 如果章節已被選擇，預設為勾選
                        var.set("1")
                    chk = Checkbutton(frame, text=options[j], variable=var)
                    chk.pack()
                    chapter_vars[options[j]] = var

            def show_page(index):
                for frame in pages:
                    frame.pack_forget()
                pages[index].pack()

            # 頁碼按鈕
            page_buttons_frame = Frame(selection_window)
            for i in range(len(pages)):
                btn = tk.Button(page_buttons_frame, text=str(i + 1), command=lambda i=i: show_page(i))
                btn.pack(side=tk.LEFT)
            page_buttons_frame.pack(side=tk.TOP)

            # 底部按鈕
            bottom_buttons_frame = Frame(selection_window)

            # 確認按鈕
            confirm_btn = tk.Button(bottom_buttons_frame, text="確認", command=lambda: [submit_selections(chapter_vars), selection_window.destroy()])
            confirm_btn.pack(side=tk.LEFT)

            # 取消按鈕
            cancel_btn = tk.Button(bottom_buttons_frame, text="取消", command=selection_window.destroy)
            cancel_btn.pack(side=tk.LEFT)

            bottom_buttons_frame.pack(side=tk.BOTTOM)

            show_page(0)  # 顯示第一頁


        def submit_selections(chapter_vars):
            for chapter, var in chapter_vars.items():
                if var.get() == "1":
                    if chapter not in selected_options:
                        add_selected_option(chapter)
                elif chapter in selected_options:
                    remove_selected_option(chapter)

        def add_selected_option(option_text):
            def remove_option():
                option_frame.destroy()
                del selected_options[option_text]
                chapter_vars[option_text].set("0")  # 更新副視窗中的勾選框

            option_frame = tk.Frame(window)
            option_frame.pack()

            tk.Label(option_frame, text=option_text).pack(side=tk.LEFT)
            remove_btn = tk.Button(option_frame, text="取消", command=remove_option)
            remove_btn.pack(side=tk.LEFT)

            selected_options[option_text] = option_frame

        def remove_selected_option(option_text):
            selected_options[option_text].destroy()
            del selected_options[option_text]

        def show_selected_chapters():
            selected_chapters = [chapter for chapter, var in chapter_vars.items() if var.get() == "1"]
            print("Selected Chapters:", selected_chapters)
            f(selected_chapters)
            window.destroy()
        
        def f(chapters):
            # Input chapters
            input_box = driver.find_element(By.XPATH, '//*[@id="semi-modal-body"]/div/div[1]/div/input')
            input_box.click()
            def click_all_chpters(chapter):
                input_box.send_keys(chapter)
                sleep(0.5)
                driver.find_element(By.XPATH, '//*[@id="semi-modal-body"]/div/div[2]/div/div/div/div[1]/div/table/tbody/tr[1]/td[1]/span/span/span/span').click()
                input_box.click()
                input_box.clear()
            for chapter in chapters:
                click_all_chpters(chapter[:5])
            driver.find_element(By.XPATH, '//*[@id="dialog-0"]/div/div[3]/div/button[2]/span').click()

        window = tk.Tk()
        window.title("主視窗")
        window.geometry("550x450")

        selected_options = {}
        chapter_vars = {}

        chapter_btn = tk.Button(window, text="章節", command=open_selection_window)
        chapter_btn.pack()

        submit_main_btn = tk.Button(window, text="提交主畫面", command=show_selected_chapters)
        submit_main_btn.pack()

        window.mainloop()

    def generate_excel_file_of_problems():
        # 存儲所有頁面的資料
        data = []
        page_obj = driver.find_elements(By.CLASS_NAME, 'semi-page-item')
        prob_number = page_obj[-2].text
        for i in range(int(prob_number)):
            # 抓取當前頁面的表格資料
            table = driver.find_elements(By.TAG_NAME, 'table')[0]  # 調整為實際的選擇器
            rows = table.find_elements(By.TAG_NAME, 'tr')[1:]  # 跳過表頭
            
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, 'td')  # 找到每一列的數據
                data.append([col.text for col in cols])  # 將數據加到列表中
            
            next_button = driver.find_element(By.CLASS_NAME, 'semi-page-item.semi-page-next')  # 調整為實際的下一頁按鈕選擇器
            next_button.click()
            sleep(1)  # 等待頁面加載

        
        # 將資料轉換成 DataFrame
        df = pd.DataFrame(data, columns=['題目', '類型', '章節', '難度', '建立者' , '練習次數', '答對次數', "功能"])  # 調整列名為實際情況

        # 計算答對比例
        df['練習次數'] = pd.to_numeric(df['練習次數'], errors='coerce').fillna(0)
        df['答對次數'] = pd.to_numeric(df['答對次數'], errors='coerce').fillna(0)
        df['答對比例'] = ((df['答對次數'] / df['練習次數']) * 100).round(2)  # 先計算百分比，再四捨五入到小數點後兩位

        # 將數值轉換為百分比格式的字符串
        df['答對比例'] = df['答對比例'].apply(lambda x: f'{x}%')

        # 將答對比例列移動到答對次數後面
        # 注意：如果你已經有 '答對比例' 列在 DataFrame 中，你可以透過列重排來達成，而不需要刪除再插入
        cols = df.columns.tolist()
        cols.insert(cols.index('答對次數')+1, cols.pop(cols.index('答對比例')))
        df = df[cols]

        # 匯出到 Excel，保存到桌面
        path = r'C:\Users\User\Desktop\微積分題庫.xlsx'  # 將 YourUserName 替換成你的使用者名稱
        df.to_excel(path, index=False)

        # 然後，使用 openpyxl 加載剛剛保存的 Excel 檔案
        from openpyxl import load_workbook
        wb = load_workbook(path)
        ws = wb.active

        # 調整每個欄位的寬度
        for column_cells in ws.columns:
            length = max(len(str(cell.value)) for cell in column_cells)
            ws.column_dimensions[get_column_letter(column_cells[0].column)].width = length

        # 保存對 Excel 檔案所做的更改
        wb.save(path)

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
    sleep(1)
    driver.find_elements(By.CLASS_NAME, "semi-navigation-item-text")[1].click()
    chapter_list = []
    crab_chapters_data()
    ui()
    sleep(1)
    generate_excel_file_of_problems()
    driver.quit()
finally:
    pass
