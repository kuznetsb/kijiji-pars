import os.path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, select, Table, Column, Integer, String, MetaData

## Setup chrome options
chrome_options = Options()
chrome_options.add_argument("--headless") # Ensure GUI is off
chrome_options.add_argument("--no-sandbox")
homedir = os.path.expanduser("~")
webdriver_service = Service(f"{homedir}/chromedriver/stable/chromedriver")


def create_db():

    meta = MetaData()

    global ads
    ads = Table('ads', meta,
        Column('id_ad', Integer, primary_key = True),
        Column('img', String(250)),
        Column('name', String(250), nullable = False),
        Column('place', String(250), nullable = False),
        Column('date', String(30)),
        Column('beds', String(250)),
        Column('description', String(1000), nullable = False),
        Column('price', String(16))
    )

    engine = create_engine("mysql+mysqlconnector://kuznetsb:4545@localhost/kijijidb")
    meta.create_all(engine)

    global conn
    conn = engine.connect()



def get_items(file_path):
    with open(file_path) as file:
        src = file.read()

    soup = BeautifulSoup(src, 'lxml')
    items_divs = soup.find_all('div', class_ = 'clearfix')

    create_db()

    for item in items_divs:
        if info := item.find('div', class_ = 'info'):
            if info_container := info.find('div', class_ = 'info-container'):
                if title := info_container.find('div', class_ = 'title'):
                    title_ads = title.get_text().strip()
                if price_ad := info_container.find('div', class_ = 'price'):
                    price_ads = price_ad.get_text().strip()
                if descrp := info_container.find('div', class_ = 'description'):
                    descrp_ads = descrp.get_text().strip()
                if location := info_container.find('div', class_ = 'location'):
                    if date := location.find('span', class_ = 'date-posted'):
                        date_ads = date = date.get_text().strip()
                    if loc := location.find('span'):
                        loc_ads = loc.get_text().strip()
        if rental_info := item.find('div', class_ = 'rental-info'):
            if bedrooms := rental_info.find('span', class_ = 'bedrooms'):
                bedrooms_ad = [i.strip() for i in bedrooms.get_text().split()]
                bedrooms_ads = ''.join(bedrooms_ad)
        if left_col := item.find('div', class_ = 'left-col'):
            if image := left_col.find('div', class_= 'image'):
                if image.img:
                    img_ads = image.img['src']
        if info and rental_info and left_col:
            table_insert = ads.insert().values(name = title_ads, price = price_ads, description = descrp_ads, date = date_ads, place = loc_ads, img = img_ads, beds = bedrooms_ads)
            conn.execute(table_insert)


def pagination(url):
    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
    driver.get(url=url)
    isNext = True
    while isNext:
        with open('page-info.html', 'w') as file:
            file.write(driver.page_source)
        get_items(file_path='/home/kuznetsb/code/dataOX-test/page-info.html')
        try:
            button_next = driver.find_element(By.XPATH, "/html[@id='reset']/body[@id='PageSRP']/div[@id='MainContainer']/div[@id='mainPageContent']/div[@class='layout-3 new-real-estate-srp']/div[@class='col-2 new-real-estate-srp']/main/div[@class='container-results large-images']/div[@class='bottom-bar']/div[@class='pagination']/a[@title='Next']")
            button_next.click()
            window_after = driver.window_handles[0]
            driver.switch_to.window(window_after)
        except Exception:
            isNext = False


def main():
    pagination(url="https://www.kijiji.ca/b-apartments-condos/city-of-toronto/c37l1700273")

if __name__ == "__main__":
    main()
