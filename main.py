import requests
import bs4
import fake_headers
import time
from unicodedata import normalize
import json


headers_gen = fake_headers.Headers(browser='firefox', os='win')
response = requests.get('https://spb.hh.ru/search/vacancy?text=python+django+flask&salary=&ored_clusters=true&area=1&area=2',
                        headers=headers_gen.generate(), proxies={})
main_html = response.text
main_soup = bs4.BeautifulSoup(main_html, 'lxml')

div_main_vacancy_list_tag = main_soup.find('main', class_="vacancy-serp-content")

vacancy_tags = div_main_vacancy_list_tag.find_all('div', class_="serp-item")

parsed_data = []

for vacancy_tag in vacancy_tags:
    h3_tag = vacancy_tag.find('h3', class_='bloko-header-section-3')
    a_tag = h3_tag.find('a')
    company_tag = vacancy_tag.find('div', class_= 'vacancy-serp-item__meta-info-company')

    link_relative = a_tag['href']
    company = normalize('NFKD', company_tag.text).encode('UTF-8', 'ignore').decode().strip()


    time.sleep(0.1)
    response_main_full = requests.get(link_relative, headers=headers_gen.generate())
    response_main_full_html = response_main_full.text
    main_full_soup = bs4.BeautifulSoup(response_main_full_html, features='lxml')
    main_full_tag = main_full_soup.find(attrs={"data-qa": "vacancy-salary"})
    address_tag = main_full_soup.find(attrs={"data-qa": "vacancy-serp__vacancy-address"})

    if main_full_tag == None:
        salary_full_text = 'Не указана зп'
    else:
        salary_full_text = normalize('NFKD', main_full_tag.text).encode('UTF-8', 'ignore').decode().strip()
    address = normalize('NFKD', address_tag.text).encode('UTF-8', 'ignore').decode().strip()


    parsed_data.append({
        'link': link_relative,
        'salary': salary_full_text,
        'company': company,
        'address': address
    })

with open("data_file.json", "w", encoding='UTF-8') as write_file:
    json.dump(parsed_data, write_file, ensure_ascii=False, indent=4)

