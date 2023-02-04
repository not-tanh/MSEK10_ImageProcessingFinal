import os
import json
import time
import urllib.error

import cv2
import urllib.parse as parse
import imutils
import selenium.common.exceptions
from selenium import webdriver


HOMEPAGE = 'https://tiki.vn'


class TikiCrawler:
    category_links = [
        'https://tiki.vn/dien-thoai-may-tinh-bang/c1789?src=c.1789.hamburger_menu_fly_out_banner',
        'https://tiki.vn/dien-tu-dien-lanh/c4221?src=c.4221.hamburger_menu_fly_out_banner',
        'https://tiki.vn/thiet-bi-kts-phu-kien-so/c1815?src=c.1815.hamburger_menu_fly_out_banner',
        'https://tiki.vn/laptop-may-vi-tinh-linh-kien/c1846?src=c.1846.hamburger_menu_fly_out_banner',
        'https://tiki.vn/may-anh/c1801?src=c.1801.hamburger_menu_fly_out_banner',
        'https://tiki.vn/dien-gia-dung/c1882?src=c.1882.hamburger_menu_fly_out_banner',
        'https://tiki.vn/nha-cua-doi-song/c1883?src=c.1883.hamburger_menu_fly_out_banner',
        'https://tiki.vn/bach-hoa-online/c4384?src=c.4384.hamburger_menu_fly_out_banner',
        'https://tiki.vn/do-choi-me-be/c2549?src=c.2549.hamburger_menu_fly_out_banner',
        'https://tiki.vn/lam-dep-suc-khoe/c1520?src=c.1520.hamburger_menu_fly_out_banner',
        'https://tiki.vn/the-thao-da-ngoai/c1975?src=c.1975.hamburger_menu_fly_out_banner',
        'https://tiki.vn/o-to-xe-may-xe-dap/c8594?src=c.8594.hamburger_menu_fly_out_banner',
        'https://tiki.vn/hang-quoc-te/c17166?src=c.17166.hamburger_menu_fly_out_banner',
        'https://tiki.vn/nha-sach-tiki/c8322?src=c.8322.hamburger_menu_fly_out_banner'
    ]
    MAX_ITEMS_PER_CATEGORY = 99999999

    # TODO: checkpoint
    def __init__(self):
        self.crawled_urls = set()
        try:
            with open('data.json.bak', 'r') as f:
                self.products = json.load(f)['data']
        except:
            self.products = []
        try:
            with open('crawled_urls.txt', 'r') as f:
                for line in f:
                    self.crawled_urls.add(line.strip())
        except FileNotFoundError:
            print('crawled_urls.txt not found, we haven\'t crawled anything')
        try:
            with open('checkpoint.json', 'r') as f:
                self.checkpoint = json.load(f)
        except:
            self.checkpoint = None

    def get_product_infos_current_page(self, driver):
        def get_hidden_url(url):
            if url.startswith('https://tka.'):
                url = url.rsplit('redirect=', 1)[-1]
                return parse.unquote(url, 'utf8')
            return url

        # Wait for all items to appear
        time.sleep(5)
        product_a_tags = driver.find_elements_by_class_name('product-item')

        product_infos = []
        for tag in product_a_tags:
            product = dict()
            href = tag.get_attribute('href')
            if href is not None:
                product['url'] = get_hidden_url(href)
                if product['url'] in self.crawled_urls:
                    continue

                product_info_div = tag.find_element_by_class_name('info')
                product['name'] = product_info_div.find_element_by_class_name('name').text
                product['price'] = product_info_div.find_element_by_class_name('price-discount__price').text

                product_thumbnail = tag.find_element_by_class_name('thumbnail')
                img_tags = product_thumbnail.find_elements_by_css_selector('img')
                img_url = None
                try:
                    for img_tag in img_tags:
                        if '/product/' in img_tag.get_attribute('src'):
                            img_url = img_tag.get_attribute('src')
                            image = imutils.url_to_image(img_url)

                            if product['name']:
                                image_path = os.path.join('images', product['name'].lower().replace(' ', '-') + '.png')
                            else:
                                image_path = os.path.join('images', str(time.time()).replace('.', '') + '.png')
                            cv2.imwrite(image_path, image)
                            product['image_path'] = image_path
                            break
                except urllib.error.HTTPError:
                    print('Error url:', img_url)
                    continue
                product_infos.append(product)
                self.crawled_urls.add(product['url'])
        return product_infos

    def run(self):
        try:
            driver = webdriver.Chrome('./chromedriver')

            if self.checkpoint is None:
                self.checkpoint = {'cat_index': 0, 'current_cat_page_url': self.category_links[0]}
            start_from = self.checkpoint['cat_index']

            for i in range(start_from, len(self.category_links)):
                next_page = self.checkpoint['current_cat_page_url']
                count = 0

                while next_page is not None:
                    print('Processing', next_page)
                    driver.get(next_page)

                    product_infos = self.get_product_infos_current_page(driver)
                    self.products += product_infos
                    try:
                        pagination_container = driver.find_element_by_xpath('//div[@data-view-id="product_list_pagination_container"]')
                    except selenium.common.exceptions.NoSuchElementException:
                        break
                    # next page icon should be the last li with an icon in it
                    next_page_icon = pagination_container.find_elements_by_css_selector('li')[-1]
                    if not next_page_icon.find_elements_by_css_selector('i'):
                        next_page = None
                    else:
                        next_page = next_page_icon.find_elements_by_css_selector('a')[-1].get_attribute('href')
                        self.checkpoint['current_cat_page_url'] = next_page

                    count += len(product_infos)
                    if count > self.MAX_ITEMS_PER_CATEGORY:
                        print('Maximum number of items exceeded, skip to next category')
                        break

                if i < len(self.category_links) - 1:
                    self.checkpoint['cat_index'] = i + 1
                    self.checkpoint['current_cat_page_url'] = self.category_links[i+1]
            print('Done')
        finally:
            with open('crawled_urls.txt', 'w') as f:
                for crawled_url in self.crawled_urls:
                    f.write(crawled_url)
                    f.write('\n')
            with open('checkpoint.json', 'w') as f:
                json.dump(self.checkpoint, f, indent=4, ensure_ascii=False)
            with open('new_data.json', 'w') as f:
                json.dump({'data': self.products}, f, indent=4, ensure_ascii=False)


class ShopeeCrawler:
    def __init__(self):
        self.crawled_urls = set()
        try:
            with open('data.json', 'r') as f:
                self.products = json.load(f)
        except:
            self.products = []
        try:
            with open('crawled_urls_shopee.txt', 'r') as f:
                for line in f:
                    self.crawled_urls.add(line.strip())
        except FileNotFoundError:
            print('crawled_urls_shopee.txt not found, we haven\'t crawled anything')
        try:
            with open('checkpoint_shopee.json', 'r') as f:
                self.checkpoint = json.load(f)
        except:
            self.checkpoint = None


if __name__ == '__main__':
    crawler = TikiCrawler()
    crawler.run()
