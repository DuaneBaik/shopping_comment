import requests
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

    def url_getter(self):

        if int(self.prod_quan) % 80 == 0 :
            page_no = int(self.prod_quan)//80
        else :
            page_no = int(self.prod_quan)//80 + 1
        print(self.prod_quan)
        for i in range(page_no) :

            url = "https://search.shopping.naver.com/search/category?catId="+ self.cat_id + "&frm=NVSHCAT&origQuery&pagingIndex="+ str(i + 1) +"&pagingSize=80&productSet=model&query&sort=rel&timestamp=&viewType=list"

            driver = webdriver.Chrome('./chromedriver')
            driver.get(url)
            print(driver.find_element_by_class_name('basicList_item__2XT81').find_element_by_tag_name('a').get_attribute('href'))

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