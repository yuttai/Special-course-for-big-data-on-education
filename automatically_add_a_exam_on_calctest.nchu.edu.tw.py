from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from backoff import expo
from logging import DEBUG, basicConfig
from random import randint
from tkinter import simpledialog
import tkinter as tk
from tkinter import ttk
from time import sleep
import main
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
        global exam_name
        #exam_name = simpledialog.askstring("exam name", "Please enter a exam📚:")
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
        # 2023/12/01
        def delete_motion(element):
            element.send_keys(Keys.CONTROL,"a")
            element.send_keys(Keys.DELETE)

        date_start = driver.find_elements(By.CLASS_NAME,"semi-input.semi-input-small")[0]
        date_end = driver.find_elements(By.CLASS_NAME,"semi-input.semi-input-small")[1]
        
        date_start.click()
        delete_motion(date_start)
        date_start.click()
        delete_motion(date_end)

        # 新增兩個視窗分別是輸入考試開始日期和考試結束日期
        startdate = simpledialog.askstring("start date", "Please enter a start date (ex:2023-12-01 15:00:00):")
        enddate = simpledialog.askstring("end date", "Please enter a end date (ex:2024-01-01 22:00:00):")
        date_start.send_keys(startdate)
        date_end.send_keys(enddate)

        # 輸入考試時間
        driver.find_elements(By.CLASS_NAME, "semi-button.semi-button-primary")[-1].click()
        test_time = driver.find_element(By.ID, "limitMinutes")
        test_time.click()
        delete_motion(test_time)
        test_time.send_keys("180")

        driver.find_elements(By.CLASS_NAME, "semi-button.semi-button-primary")[-1].click()
        # -------------------------------------------------------------------------------------

    # 待處理 -----------------------------------------------------------------------------------

    import tkinter as tk

    def create_a_window():

        def submit_action():
            # 獲取取輸入資料
            yes_q = entry_yesno.get()
            one_q = entry_one_choice.get()
            muti_q = entry_mutichoice.get()
            text_q = entry_text.get()

            # 儲存輸入的資料
            exam_data["是非題"] = {"total": entry_yesno.get()}
            exam_data["單選題"] = {"total": entry_one_choice.get()}
            exam_data["多選題"] = {"total": entry_mutichoice.get()}
            exam_data["填充/申論題"] = {"total": entry_text.get()}

            # 對每種題型用 allocate_difficulty 函数
            allocate_difficulty("是非題", yes_q)
            allocate_difficulty("單選題", one_q)
            allocate_difficulty("多選題", muti_q)
            allocate_difficulty("填充/申論題", text_q)

        # 新增視窗
        global root
        root = tk.Tk()
        root.bind("<Return>", submit_action)
        root.title("題目數輸入")
        root.geometry("200x300")

        # 新增輸入框和標籤
        label_yesno = tk.Label(root, text = "是非題題數:")
        label_yesno.pack()
        entry_yesno = tk.Entry(root)
        entry_yesno.insert(0, "0")
        entry_yesno.pack()

        label_one_choice = tk.Label(root, text = "單選題題數:")
        label_one_choice.pack()
        entry_one_choice = tk.Entry(root)
        entry_one_choice.insert(0, "0")
        entry_one_choice.pack()

        label_mutichoice = tk.Label(root, text = "複選題題數:")
        label_mutichoice.pack()
        entry_mutichoice = tk.Entry(root)
        entry_mutichoice.insert(0, "0")
        entry_mutichoice.pack()

        label_text = tk.Label(root, text = "填充/申論:")
        label_text.pack()
        entry_text = tk.Entry(root)
        entry_text.insert(0, "0")
        entry_text.pack()

        # 新增提交按鈕
        submit_button = tk.Button(root, text="提交", command=submit_action)
        submit_button.pack()

        # 這裡不使用 mainloop()，而是使用 wait_window() 等待視窗關閉
        root.wait_window()

    def check_and_close_main_window():
        global open_windows_count, root
        if open_windows_count == 0:
            root.destroy()

    def allocate_difficulty(q_type, num_questions_str):
        global next_window_x, next_window_y, open_windows_count
        def save_difficulty_allocation():
            try:
                # 取得輸入的數值
                easy_count = int(easy_entry.get())
                medium_count = int(medium_entry.get())
                hard_count = int(hard_entry.get())
                score = int(score_entry.get())
                
                # 收集难度分配的数据
                exam_data[q_type]["簡單"] = int(easy_entry.get())
                exam_data[q_type]["中等"] = int(medium_entry.get())
                exam_data[q_type]["困難"] = int(hard_entry.get())
                exam_data[q_type]["題目分數"] = int(score_entry.get())

                # 检查总数是否与输入匹配
                if easy_count + medium_count + hard_count != int(num_questions_str):
                    print(f"錯誤：{q_type}不同難度題目數總和不等於總题目數")
                    return
                print(f"{q_type}: 簡單 {easy_count}, 中等 {medium_count}, 困難 {hard_count}, 題目分數 {score}")
            except ValueError:
                print("請在所有難度等級的輸入框中輸入有效的數字")
                return
            global open_windows_count
            open_windows_count -= 1
            check_and_close_main_window()
            difficulty_window.destroy()
            difficulty_window.destroy()

        # 新增新視窗
        difficulty_window = tk.Toplevel()
        difficulty_window.bind("<Return>", save_difficulty_allocation)
        open_windows_count += 1
        difficulty_window.title(f"分配 {q_type} 的難度")
        difficulty_window.geometry(f"{window_width}x{window_height}+{next_window_x}+{next_window_y}")

        # 更新下一個視窗的位置
        next_window_x += window_width

        # 新增標籤和輸入框
        tk.Label(difficulty_window, text=f"{q_type} 總數：{num_questions_str}").pack()
        
        tk.Label(difficulty_window, text="簡單:").pack()
        easy_entry = tk.Entry(difficulty_window)
        easy_entry.insert(0, "0")
        easy_entry.pack()

        tk.Label(difficulty_window, text="中等:").pack()
        medium_entry = tk.Entry(difficulty_window)
        medium_entry.insert(0, "0")
        medium_entry.pack()

        tk.Label(difficulty_window, text="困難:").pack()
        hard_entry = tk.Entry(difficulty_window)
        hard_entry.insert(0, "0")
        hard_entry.pack()

        tk.Label(difficulty_window, text="題目分數").pack()
        score_entry = tk.Entry(difficulty_window)
        score_entry.insert(0, "10")
        score_entry.pack()

        # 新增保存按紐
        save_button = tk.Button(difficulty_window, text="保存", command=save_difficulty_allocation)
        save_button.pack()

    ''' def wait_for_element(driver, by, identifier, timeout=10):
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, identifier)))'''

    def wait_for_element(driver, by, identifier, timeout=20):
        element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, identifier)))
        return element

    def add_question_motion(q_type, difficulity, score, chapter):
        #wait_for_element(driver, By.XPATH, q_xpath[q_type]).click()
        sleep(0.5)
        driver.find_element(By.XPATH, q_xpath[q_type]).click()
        driver.find_element(By.XPATH, difficulty_xpath[difficulity]).click()
        score_box = driver.find_element(By.ID, "score")
        score_box.click()
        score_box.send_keys(Keys.CONTROL, "a")
        score_box.send_keys(Keys.DELETE)
        score_box.send_keys(score)
        driver.find_element(By.XPATH, '//*[@id="semi-modal-body"]/form/div[4]/div/div/button').click()
        chapter_input = driver.find_element(By.XPATH, '//*[@id="semi-modal-body"]/div/div[1]/div/input')
        chapter_input.click()
        chapter_input.send_keys(chapter)
        sleep(0.5)
        driver.find_elements(By.CLASS_NAME, "semi-checkbox-inner-display")[4].click()
        driver.find_elements(By.CLASS_NAME, "semi-button-content")[-1].click()
        driver.find_element(By.XPATH, "//div[@class='semi-modal-footer']/div/button[2]").click()
        global button_flag
        button_flag = True


    def create_quention_chapter_ui():
        def create_chapter_selection_frame(parent):
            # 使用 Canvas 和 Scrollbar 創建滾動條
            canvas = tk.Canvas(parent)
            scrollbar_y = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
            scrollbar_x = ttk.Scrollbar(parent, orient="horizontal", command=canvas.xview)
            scrollable_frame = ttk.Frame(canvas)

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(
                    scrollregion=canvas.bbox("all")
                )
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

            col = 0
            for q_type, difficulties in exam_data.items():
                tk.Label(scrollable_frame, text=q_type, font=("Arial", 12)).grid(row=0, column=col, sticky="w")
                chapter_vars[q_type] = {}

                row = 1
                for difficulty, count_str in difficulties.items():
                    if difficulty == ("total" or "題目分數"):
                        continue
                    chapter_vars[q_type][difficulty] = []
                    count = int(count_str)

                    for i in range(count):
                        if count == exam_data[q_type]["題目分數"]:
                            continue
                        label_text = f"{difficulty} {i+1}:"
                        tk.Label(scrollable_frame, text=label_text).grid(row=row, column=col, sticky="w")
                        chapter_var = tk.StringVar() # 为每个下拉菜单创建一个 StringVar 对象
                        chapter_combobox = ttk.Combobox(scrollable_frame, textvariable=chapter_var, values=[ch + " " + chapters_dic[ch] for ch in chapters])
                        chapter_combobox.grid(row=row, column=col+1, sticky="w")
                        chapter_combobox.set("1 - 1"+ " " + chapters_dic[chapters[0]])  # 默认选项
                        chapter_vars[q_type][difficulty].append(chapter_var)  # 将 StringVar 对象添加到列表中
                        row += 1
                col += 2
        
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar_y.pack(side="right", fill="y")
            scrollbar_x.pack(side="bottom", fill="x")

        def submit_action():
            # 收集下拉菜单的选择
            for q_type, difficulties in chapter_vars.items():
                selected_chapters[q_type] = {}
                for difficulty, vars in difficulties.items():
                    selected_chapters[q_type][difficulty] = [var.get() for var in vars]

            # 打印或存储选中的章节
            print("用户选择的章节：", selected_chapters)
            root.destroy()

        # 創建主窗口並在其中創建章節選擇的界面
        root = tk.Tk()
        root.title("題目類型和難度")
        root.geometry("800x600")
        create_chapter_selection_frame(root)
        submit_button = tk.Button(root, text="提交", command=submit_action)
        submit_button.pack(side="bottom", pady=10)

        root.mainloop()

    def add_some_questions():
        test_name = driver.find_elements(By.CLASS_NAME, "semi-typography-link-text")
        for test in test_name:
            exam_name = "165155"
            if test.text != exam_name:
                continue
            else:
                test_name[test_name.index(test)].click()
                sleep(0.5)
                empty = driver.find_elements(By.CLASS_NAME, "semi-empty-description")
            if len(empty) == 1:
                create_a_window()
                create_quention_chapter_ui()
                for q_type, difficulties in selected_chapters.items():
                    for difficulty, chapter in difficulties.items():
                        for q_num in chapter:
                            if button_flag == False:
                                driver.find_element(By.CLASS_NAME, "semi-button.semi-button-primary.semi-button-light").click()
                            else:
                                wait_for_element(driver, By.XPATH, '//*[@id="__next"]/div/div[2]/div[1]/div[2]/div/div[2]/div/div[1]/div/button[2]/span').click()
                                #driver.find_element(By.XPATH, '//*[@id="__next"]/div/div[2]/div[1]/div[2]/div/div[2]/div/div[1]/div/button[2]/span').click()
                            #wait_for_element(driver, By.CLASS_NAME, "semi-dropdown-item").click()
                            #driver.find_element(By.XPATH, "//li[contains(text(), '從題庫中隨機抽取')]").click()
                            driver.find_element(By.CLASS_NAME, "semi-dropdown-item").click()
                            q_num_list = str(q_num).split(" ")
                            q_num1 = q_num_list[0] + " " + q_num_list[1] + " " + q_num_list[2]
                            add_question_motion(q_type, difficulty, exam_data[q_type]["題目分數"], q_num1)

                
    # ------------------------------------------------------------------------------------------
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
    
    sleep(1)
    exam_data = {}
    chapter_vars = {}
    selected_chapters = {}
    open_windows_count = 0
    root = None
    next_window_x = 100
    next_window_y = 100
    window_width = 200
    window_height = 200
    q_list = []
    button_flag = False
    
    q_xpath = {"是非題" : '//*[@id="randomType"]/label[1]/span/input',
               "單選題" : '//*[@id="randomType"]/label[2]/span/input',
               "多選題" : '//*[@id="randomType"]/label[3]/span/input',
               "填充/申論題" : '//*[@id="randomType"]/label[4]/span/input'}
    difficulty_xpath = {"簡單" : '//*[@id="randomLevel"]/span[1]/span/span',
                       "中等" : '//*[@id="randomLevel"]/span[2]/span/span',
                       "困難" : '//*[@id="randomLevel"]/span[3]/span/span'}
    chapters = []
    # 每個大章節中的小章節數量
    subchapters_counts = {1: 3,  2: 2,  3: 5,  4: 3, 5: 2, 6: 5, 7: 5, 8: 6,
        9: 2, 10: 2, 11: 3, 12: 1, 13: 2, 14: 2, 15: 3, 16: 1 
    }

    # 根據每個大章節的小章節數量生成章節列表
    for major, sub_count in subchapters_counts.items():
        for sub in range(1, sub_count + 1):
            chapter = f"{major} - {sub}"
            chapters.append(chapter)

    chapters_dic = {"1 - 1": "Functions 函數", 
                    "1 - 2": "The Definition of a Limit & the Limit Laws 極限定義及定理", 
                    "1 - 3": "Continuity 連續",
                    "2 - 1": "The Derivative as a Function & Differentiation Formulas 代數函數的導函數及其微分公式",
                    "2 - 2": "Derivatives of Trigonometric Functions 、The Chain Rule & Implicit Differentiation 三角函數的微分、連鎖律及隱函數微分",
                    "3 - 1": "Rates of Change & Linear Approximations of Differentials 變化率應用題及微分近似式",
                    "3 - 2": "The Mean Value Theorem & Extrema Values 微分均值定理及其極值問題",
                    "3 - 3": "Graphing with Calculus and Technology & Asymptotes 函數圖形繪製及漸近線",
                    "3 - 4": "Optimization Problems 微分的極值應用題",
                    "3 - 5": "Newton's Method Newton 法近似求根",
                    "4 - 1": "Antiderivatives 反導數",
                    "4 - 2": "The Definite Integral & The Fundamental Theorem of Calculus 定積分與微積分基本定理",
                    "4 - 3": "Indefinite Integrals & The Substitution Rule 不定積分變數代換法",
                    "5 - 1": "Find Areas Between Curves & Volumes 積分應用求面積與體積",
                    "5 - 2": "Work & Average Value of a Function 積分應用求功、積分均值定理",
                    "6 - 1": "Inverse Functions and Their Derivatives 反函數之導數",
                    "6 - 2": "The Natural、 Exponential Functions 、Natural 、Logarithmic Functions and Their Derivatives 指數函數與對數函數之微分",
                    "6 - 3": "The derivative of Inverse Trigonometric Function 反三角函數之微分",
                    "6 - 4": "The derivatives of Hyperbolic Functions 雙曲線函數之微分",
                    "6 - 5": "L'Hospital's Rule 羅必達法則",
                    "7 - 1": "Integration by Parts 三角函數之分部積分法",
                    "7 - 2": "Trigonometric Substitution 三角代換法",
                    "7 - 3": "Integration of Rational Functions by Partial Fractions 部分分式積分法",
                    "7 - 4": "Integration Using Tables and Approximate Integration 積分表與近似積分法",
                    "7 - 5": "Improper Integrals 瑕積分",
                    "8 - 1": "積分應用~曲線長",
                    "8 - 2": "Area of a Surface of Revolution 旋轉曲面積",
                    "8 - 3": "Applications to Physics and Engineering 工程物理應用題",
                    "8 - 4": "Applications to Economics and Biology 經濟、生物應用題",
                    "8 - 5": "Probability 機率",
                    "8 - 6": "Linear 1st order Differential Equations 一階線性微分方程式之應用題",
                    "9 - 1": "Calculus in Polar Coordinates 極座標及其曲線",
                    "9 - 2": "極座標錐曲面",
                    "10 - 1": "The test methods of Sequences 、Series、Alternating Series 數列、級數與交錯級數之審斂法",
                    "10 - 2": "Power Series、Taylor and Maclaurin Series and its Applications 冪級數、Taylor級數展開及其應用",
                    "11 - 1": "The Dot Product、The Cross Product of vectors & Equations of Lines and Planes 向量之點積與叉積與線、面方程式、圓柱曲面",
                    "11 - 2": "Derivatives and Integrals of Vector Functions 向量函數之微分與積分",
                    "11 - 3": "Arc Length and Curvature & Motion in Space 曲線曲率與速度、加速度",
                    "12 - 1": "Partial Derivatives of Functions of Several Variables 多變數函數之極限、連續、微分、連鎖律",
                    "12 - 2": "Lagrange Multipliers of Maximum and Minimum Values Lagrange法求拘束極值",
                    "13 - 1": "Directional Derivatives and the Gradient Vector 方向導數及其梯度",
                    "13 - 2": "Tangent Planes 切平面",
                    "14 - 1": "Double Integrals over Rectangles 、Polar Coordinates & General Regions 卡氏、極座標雙重積分及其應用求曲面",
                    "14 - 2": "Triple Integrals in Cylindrical Coordinates、Spherical Coordinates 三大座標系統三重積分",
                    "15 - 1": "Line Integrals & The Green's Theorem for Line Integrals 曲線積分與平面Green定理",
                    "15 - 2": "Curl and Divergence散度與旋度",
                    "15 - 3": "Surface Integrals & Stokes' Theorem 、The Divergence Theorem 曲面積分與Stokes定理、散度定理",
                    "16 - 1": "二階微分方程式"}
    #add_one_exam()
    add_some_questions()
    driver.quit()
finally:
    # 在這裡加上driver.quit()的原因是因為如果沒加的話，當程式出錯時網頁還會存在，但是想要再次執行時，如果沒有把網頁關掉的話
    # 會出問題，所以才在finally加上driver.quit()，這樣在程式出錯的時候，就可以先執行finally的程式碼，然後才會報錯。
    # 如果想要debug，那就把driver.quit()移到try的最後一行，並且在finally裡加上pass讓finally運作，因為finally不能為空，
    # 不然程式會把網頁關掉，就不能debug了。
    # driver.quit()
    pass
