from logger_1 import test_1, logger
from logger_2 import test_2
from hw_parsing import iterate_pages
import json


iterate_pages = logger(iterate_pages)

if __name__ == '__main__':
    test_1()
    test_2()

    # Third task
    url = 'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2'
    key_words = "django", "flask"
    vacancies = iterate_pages(url, *key_words, num_pages=10)
