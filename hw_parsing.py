import requests
from bs4 import BeautifulSoup
from fake_headers import Headers
from pprint import pprint
import json
from logger_1 import logger


def get_headers():
    headers = Headers(browser='chrome', os='win')
    return headers


def get_page(url):
    html = requests.get(url, headers=get_headers().generate()).text
    return html


def pages_quantity(url):
    html = get_page(url=url)
    bs = BeautifulSoup(html, features='html5lib')
    num_pages = bs.find(class_="pager")
    list_span = []
    for span in num_pages.find_all("span"):
        title = span.find("span")
        if title is not None and title.text.isdigit():
            list_span.append(int(title.text))
    return max(list_span)


def get_vacancies(html):
    bs = BeautifulSoup(html, features='html5lib')
    vacancies_list = bs.find_all(class_="vacancy-serp-item__layout")
    return vacancies_list


def searching_keywords(vacancy, *args):
    key_word_in = True
    for key_word in args:
        if key_word in vacancy.lower():
            continue
        else:
            key_word_in = False
            break
    return key_word_in


def vacancy_info(vacancies_list, list_info, *key_words, usd=False):
    for vacancy in vacancies_list:
        description = vacancy.find("div", class_="g-user-content")

        if description is None:
            description = ""
        else:
            description = description.text

        address = vacancy.find("div", class_="vacancy-serp-item-company").\
            find("div", class_="vacancy-serp-item__info").\
            find(attrs={'class': 'bloko-text', 'data-qa': 'vacancy-serp__vacancy-address'}).text
        city = address.split(',')[0]

        if searching_keywords(description, *key_words):
            title = vacancy.find(class_="serp-item__title").text
            link = vacancy.find(class_="serp-item__title")["href"]
            vacancy_tag_div = vacancy.find(class_="vacancy-serp-item-body__main-info").find("div", class_="")
            vacancy_tag_span = vacancy_tag_div.find('span', class_="bloko-header-section-3")
            employer = vacancy.find("div", class_="vacancy-serp-item-company").\
                find("div", class_="bloko-v-spacing-container bloko-v-spacing-container_base-2").\
                find("a").text
            if vacancy_tag_span is not None:
                salary = vacancy_tag_span.text
            else:
                salary = "Зарплата не указана"
            if usd and "usd" not in salary.lower():
                continue

            about_vacancy = {
                "title": title,
                "link": link,
                "salary": salary,
                "employer": employer,
                "city": city
                }
            list_info.append(about_vacancy)
    return list_info


@logger
def iterate_pages(url, *key_words, num_pages=None, usd=False):
    vacancies = []
    if num_pages is None:
        num_pages = pages_quantity(url=url)
    for page in range(num_pages):
        url_page = url + f'&page={page}'
        html = get_page(url=url_page)
        vacancies_list = get_vacancies(html=html)
        vacancies = vacancy_info(vacancies_list, vacancies, *key_words, usd=usd)
    return vacancies


if __name__ == '__main__':
    url = 'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2'
    key_words = "django", "flask"
    vacancies = iterate_pages(url, *key_words, num_pages=10)
    with open('vacancies.json', 'wt', encoding='utf-8') as file:
        json.dump(vacancies, file, indent=2, ensure_ascii=False)
    pprint(vacancies)

    # Salary in USD
    key_words = "python"
    vacancies_usd = iterate_pages(url, *key_words, usd=True)
    with open('vacancies_usd.json', 'wt', encoding='utf-8') as file:
        json.dump(vacancies_usd, file, indent=2, ensure_ascii=False)
