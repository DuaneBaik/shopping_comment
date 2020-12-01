import requests
import time
import csv
from bs4 import BeautifulSoup
from selenium import webdriver

class Category:

    def __init__(self,cat_id,prod_quan,comm_quan):

        self.cat_id = cat_id
        self.prod_quan = prod_quan
        self.comm_quan = comm_quan

    def check(self):
        print('현재 설정된 카테고리 넘버는 {0}이고, 지정한 상품의 개수는 {1}, 후기의 개수는 {2}입니다.'.format(self.cat_id,self.prod_quan,self.comm_quan))

    def max_prod_check(self):

        url = "https://search.shopping.naver.com/search/category?catId="+ self.cat_id + "&frm=NVSHCAT&origQuery&pagingIndex=1&pagingSize=40&productSet=model&query&sort=rel&timestamp=&viewType=list"
        req = requests.get(url)
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')

        max_count = soup.select(
            'ul[class=subFilter_seller_filter__3yvWP] > li > a > span[class=subFilter_num__2x0jq]'
        )

        max_prod = max_count[1].text.replace(',','')

        if self.prod_quan == 'all' :
            self.prod_quan = max_prod

        elif int(self.prod_quan) > int(max_prod) :
            print("지정한 상품의 개수가 최대 상품의 개수를 초과하여, 최대개수인 {0}개로 조정됩니다.".format(max_prod))
            self.prod_quan = max_prod

    def max_comm_check(self, max_comm):

        if self.comm_quan == 'all' :
            self.comm_quan = max_comm
        elif int(self.comm_quan) > max_comm :
            print("지정한 후기의 개수가 최대 후기의 개수를 초과하여, 최대개수인 {0}개로 조정됩니다.".format(max_comm))
            self.comm_quan = max_comm


    def url_getter(self):

        global url_truck

        if int(self.prod_quan) % 80 == 0 :
            page_no = int(self.prod_quan)//80
        else :
            page_no = int(self.prod_quan)//80 + 1

        url_truck = []

        for i in range(page_no) :

            url = "https://search.shopping.naver.com/search/category?catId="+ self.cat_id + "&frm=NVSHCAT&origQuery&pagingIndex="+ str(i + 1) +"&pagingSize=80&productSet=model&query&sort=rel&timestamp=&viewType=list"

            driver = webdriver.Chrome('./chromedriver')
            driver.get(url)

            self.scroller(driver)

            ls = driver.find_elements_by_class_name('basicList_item__2XT81')

            for data in ls :
                url_truck.append(data.find_element_by_css_selector('a').get_attribute('href'))

    def scroller(self,driver):

        scroll_pause_sec = 1

        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            time.sleep(scroll_pause_sec)

            new_height = driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:

                time.sleep(scroll_pause_sec)
                new_height = driver.execute_script("return document.body.scrollHeight")

                if new_height == last_height:
                    break

            last_height = new_height

    def fake_check(self, driver):

        list = driver.find_element_by_class_name('floatingTab_detail_tab__2T3U7').find_elements_by_css_selector('li')
        for index in list :
            if index.find_element_by_tag_name('strong').text == '쇼핑몰리뷰' :
                return True

    def page_swap(self, driver, page_info):

        if page_info == 'next':
            print("실행1")
            print(driver.find_element_by_class_name('review_section_review__1hTZD').find_element_by_class_name('pagination_pagination__2M9a4').find_element_by_class_name('pagination_next__3ycRH').text)
            cord = driver.find_element_by_class_name('review_section_review__1hTZD').find_element_by_class_name('pagination_pagination__2M9a4').find_element_by_class_name('pagination_next__3ycRH')

        elif page_info > 8 :
            print("실행2")
            cord = driver.find_element_by_class_name('review_section_review__1hTZD').find_element_by_class_name('pagination_pagination__2M9a4').find_elements_by_css_selector('a')[(page_info + 1) % 10 + 2]
        else :
            print("실행3")
            cord = driver.find_element_by_class_name('review_section_review__1hTZD').find_element_by_class_name('pagination_pagination__2M9a4').find_elements_by_css_selector('a')[page_info + 1]

        driver.execute_script("arguments[0].click();", cord)


    def comm_getter(self):

        for index in range(int(self.prod_quan)) :

            url = url_truck[index]

            driver = webdriver.Chrome('./chromedriver')
            driver.get(url)

            self.scroller(driver)

            if self.fake_check(driver) != True:
                continue

            max_comm = driver.find_element_by_class_name('floatingTab_detail_tab__2T3U7').find_elements_by_css_selector('li')[-2].find_element_by_css_selector('em').text.replace(',','')
            self.max_comm_check(int(max_comm))

            comm_page = int(self.comm_quan) // 20
            comm_left = int(self.comm_quan) % 20

            prod_name = driver.find_element_by_class_name('top_summary_title__15yAr').find_element_by_tag_name('h2').text
            f = open(prod_name + '.csv' , 'w' , newline='',encoding='utf-8')
            wr = csv.writer(f)
            wr.writerow(['star_point', 'comment', 'photo'])
            for i in range(comm_page) :

                self.comm_getter_2(driver, 20, wr)

                if (i % 10) == 9 :
                    self.page_swap(driver, 'next')
                    time.sleep(1)
                    #driver.find_element_by_class_name('review_section_review__1hTZD').find_element_by_class_name('pagination_pagination__2M9a4').find_element_by_class_name('pagination_next__3ycRH').click()

                if i == (comm_page - 1) :
                    break
                self.page_swap(driver, i)
               # driver.find_element_by_class_name('review_section_review__1hTZD').find_element_by_class_name('pagination_pagination__2M9a4').find_elements_by_css_selector('a')[i+2].click()
                self.scroller(driver)

            if comm_left != 0 :

                if comm_page != 0 :

                    self.page_swap(driver, comm_page - 1)
                #    driver.find_element_by_class_name('review_section_review__1hTZD').find_element_by_class_name('pagination_pagination__2M9a4').find_elements_by_css_selector('a')[comm_page % 10].click()
                    self.scroller(driver)


                self.comm_getter_2(driver, comm_left, wr)

            f.close()

    def comm_getter_2(self,driver,r,writer) :

        items = driver.find_element_by_class_name('reviewItems_list_review__1sgcJ').find_elements_by_css_selector('li')

        for prod in range(r):
            img_truck = []

            star = items[prod].find_element_by_class_name('reviewItems_average__16Ya-').text
            comm = items[prod].find_element_by_class_name('reviewItems_text__XIsTc').text
            if len(items[prod].find_element_by_class_name("reviewItems_review__1eF8A").find_elements_by_css_selector('div')) == 2:
                img_ls = items[prod].find_element_by_class_name('reviewItems_review_thumb__CK7I2').find_elements_by_class_name(
                    'reviewItems_img_box__2zrNv')

                for img in img_ls:
                    img_truck.append(img.find_element_by_tag_name('img').get_attribute('src'))

            writer.writerow([star,comm,img_truck.replace('[','')])





def setting() :

    cat_id = input("원하는 상품의 카테고리 ID를 입력해주세요. : ") # 원하는 상품의 카테고리 id를 입력받는다
    prod_quan = input("카테고리 내 후기를 긁고싶은 상품의 개수를 입력하세요. 모든 상품을 긁으시려면 all 입력. : ") # 후기를 긁고싶은 상품의 개수를 입력받는다. 입력한 값이 네이버에서 보유한 상품의 개수를 초과할 경우, 자동으로 그 상한에 맞춰진다.
    comm_quan = input("상품별로 얻고싶은 후기의 개수를 입력하세요. 모든 후기를 얻으시려면 all 입력. : ") # 상품별 긁을 후기의 개수를 설정한다.

    new_prod = Category(cat_id,prod_quan,comm_quan)

    return new_prod


new_prod = setting()
new_prod.check()
new_prod.max_prod_check()
new_prod.url_getter()
new_prod.comm_getter()