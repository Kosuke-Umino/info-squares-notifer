from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome import service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import json
import urllib3

START_IDX_WITH_FIT_SLIDE = 4
START_IDX_WITH_UNFIT_SLIDE = START_IDX_WITH_FIT_SLIDE + 1
START_IDX_WITHOUT_SUB_SLIDE = 0

CHROMEDRIVER_PATH = <YOUR_CHROMEDRIVER_PATH>
INFOSQUARES_URL = 'https://infosquares.the-shanaiho.com/'
WEBHOOK_URL = <YOUR_WEBHOOK_URL>  # テスト用

BASE_MESSAGE = 'InfoSquares の Check List 欄をテスト通知　※以下は期限厳守（月・木曜日定期通知）\n'


def is_slide_fit_with_frame(num_slide, num_article):
    return num_slide == num_article


def get_check_list_info(slides, idx):
    article = slides[idx]
    # TODO: 解析要素に不要なaタグがある場合にリンクが修正できない事象が発生したため、情報収集方法を修正する
    link = article.find_element(By.TAG_NAME, "a").get_attribute("href")
    title = article.find_element(By.CLASS_NAME, "ttl").text
    category = article.find_element(By.CLASS_NAME, "cat").text
    date = article.find_element(By.CLASS_NAME, "date").text

    return link, title, category, date


def create_message(num_read_slick, mod, num_read_slide, slides, item_slide):
    message = BASE_MESSAGE
    if num_read_slick == 0:
        idx_current_slide = START_IDX_WITHOUT_SUB_SLIDE
        for _ in range(num_read_slide):
            message += create_sentence(slides, idx_current_slide)
            idx_current_slide += 1
    else:
        idx_current_slide = START_IDX_WITH_FIT_SLIDE
        next_button = item_slide.find_element(By.CLASS_NAME, "slick-next")
        for _ in range(num_read_slick):
            for _ in range(num_read_slide):
                message += create_sentence(slides, idx_current_slide)
                idx_current_slide += 1
            next_button.click()

        for _ in range(mod):
            message += create_sentence(slides, idx_current_slide)
            idx_current_slide += 1

    return message


def create_message_with_unfit_slide(num_read_slick, mod, num_active_slide, slides, item_slide):
    idx_current_slide = START_IDX_WITH_UNFIT_SLIDE
    message = BASE_MESSAGE
    next_button = item_slide.find_element(By.CLASS_NAME, "slick-next")
    for count_read in range(num_read_slick):
        if not count_read:
            num_read_slide = num_active_slide - 1
        else:
            num_read_slide = num_active_slide
        for _ in range(num_read_slide):
            message += create_sentence(slides, idx_current_slide)
            idx_current_slide += 1
        next_button.click()

    for _ in range(mod):
        message += create_sentence(slides, idx_current_slide)
        idx_current_slide += 1

    return message


def create_sentence(slides, idx_current_slide):
    link, title, category, date = get_check_list_info(slides, idx_current_slide)
    return f"・<{link}|{category} {title} (掲載日: {date})>\n"


def post_message(message, post_url):
    send_message = {
        "text": message,
    }

    http = urllib3.PoolManager()
    send_data = json.dumps(send_message).encode('utf-8')
    http.request('POST', post_url, body=send_data)


def main():
    # 画面非表示及びドライバーの設定
    options = Options()
    options.add_argument('--headless')
    chrome_service = service.Service(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=chrome_service, options=options)

    # Info Squares ログインページ
    driver.get(INFOSQUARES_URL)
    driver.find_element(By.CLASS_NAME, "list-group-item").send_keys(Keys.ENTER)

    # Okta でログインするために待機
    sleep(8)

    # Info Squares トップページを class を手掛かりに掘り下げる (タグを使用したパス (XPATH) でも掘り下げ可能)
    items_box = driver.find_element(By.CLASS_NAME, "itemsBox")
    item_slide = items_box.find_elements(By.CLASS_NAME, "item_slide_kazroom_boardmsg")[1]
    slick_track = item_slide.find_element(By.CLASS_NAME, "slick-track")
    slides = slick_track.find_elements(By.CLASS_NAME, "slick-slide")

    num_slide = len(slides)
    num_article = len(slick_track.find_elements(By.TAG_NAME, "article"))
    num_cloned_slick = len(slick_track.find_elements(By.CLASS_NAME, "slick-cloned"))
    num_activable_slide = num_slide - num_cloned_slick
    num_active_slide = len(slick_track.find_elements(By.CLASS_NAME, "slick-active"))

    # 実処理
    if is_slide_fit_with_frame(num_slide, num_article):
        num_read_slick, mod = (0, 0) if num_activable_slide <= 4 else divmod(num_activable_slide, num_active_slide)
        message = create_message(num_read_slick, mod, num_active_slide, slides, item_slide)
    else:
        num_read_slick, mod = divmod(num_activable_slide, num_active_slide)
        message = create_message_with_unfit_slide(num_read_slick, mod, num_active_slide, slides, item_slide)

    post_message(message, WEBHOOK_URL)

    driver.close()
    driver.quit()


if __name__ == '__main__':
    main()
    quit(0)

