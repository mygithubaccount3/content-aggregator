import os
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
import requests
from bs4 import BeautifulSoup
from selenium import webdriver


def get_bs4_instance(html_document: str, parser: str) -> BeautifulSoup:
    response = requests.get(html_document)
    return BeautifulSoup(response.text, parser)


def bbc(request, page=1):
    if request.GET.get('page') or page:
        articles = []
        page_obj = {}
        soup = get_bs4_instance('https://bbc.com/sport', 'lxml')
        sport_news_html_tags = soup.select('.gs-c-promo-body')
        del sport_news_html_tags[-25:]

        for tag in sport_news_html_tags:
            article = {
                'title': '',
                'summary': '',
                'tag': '',
                'time': ''
            }

            if tag.select_one('.gs-c-promo-heading__title') is not None:
                article.update(title=tag.select_one(
                    '.gs-c-promo-heading__title').get_text())
            else:
                continue

            if tag.select_one('.gs-c-promo-summary') is not None:
                article.update(summary=tag.select_one(
                    '.gs-c-promo-summary').get_text())

            if tag.select_one('.qa-section-tag a') is not None:
                article.update(tag=tag.select_one(
                    '.qa-section-tag a').get_text())

            if tag.select_one('.gs-u-vh') is not None and 'ago' in tag.select_one('.gs-u-vh').get_text():
                article.update(time=tag.select_one('.gs-u-vh').get_text())

            articles.append(article)
            paginator = Paginator(articles, 10)
            page_number = request.GET.get('page') or page
            page_obj = paginator.get_page(page_number)

        # print(titles)

        return render(request, 'conag/index.html', {'page_obj': page_obj})
    else:
        # return redirect('/conag/bbc?page=1', permanent=True)
        return redirect('conag:bbc', permanent=True, page=1)


def cnn(request):
    articles = []
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get('GOOGLE_CHROME_BIN')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    browser = webdriver.Chrome(executable_path=os.environ.get('CHROMEDRIVER_PATH'), chrome_options=chrome_options)
    browser.set_window_size(950, 800)

    browser.get("https://edition.cnn.com/health")
    html = browser.page_source
    soup = BeautifulSoup(html, 'lxml')
    tags = soup.find('h2', string='Latest').find_next_siblings('li')

    for tag in tags:
        articles.append(tag.find_next(
            'span', class_='cd__headline-text').get_text())

    # browser.close()

    return render(request, 'conag/index.html', {'articles': articles})
