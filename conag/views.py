import os
from django import http
from django.http import HttpRequest, HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from django.views.generic import TemplateView
from .forms import SearchForm


class IndexView(TemplateView):
    def get(self, request: http.HttpRequest) -> http.HttpResponse:
        return render(request, 'conag/greeting.html')


class BbcView(TemplateView):
    template_name = 'conag/index.html'
    form_class = SearchForm
    page = 1
    articles_per_page = 10

    def get(self, request: HttpRequest, page: int = page) -> HttpResponse | HttpResponsePermanentRedirect:
        if request.GET.get('page') or page:
            page_obj = None
            form = self.form_class(request.GET)

            if form.is_valid():
                cleaned_page = form.cleaned_data.get('page')

                soup = self.__get_bs4_instance('https://bbc.com/sport', 'lxml')
                sport_news_html_tags = soup.select('.gs-c-promo-body')
                del sport_news_html_tags[-25:]

                articles = form.search(sport_news_html_tags)

                paginator = Paginator(articles, self.articles_per_page)
                page_number = cleaned_page or page  # escape GET
                page_obj = paginator.get_page(page_number)

            return render(request, self.template_name, {'page_obj': page_obj, 'form': form})
        else:
            return redirect('conag:bbc', permanent=True, page=1)

    def __get_bs4_instance(self, html_document: str, parser: str) -> BeautifulSoup:
        response = requests.get(html_document)
        return BeautifulSoup(response.text, parser)


class CnnView(TemplateView):
    def get(self, request: HttpRequest) -> HttpResponse:
        articles = []
        service = Service(executable_path=ChromeDriverManager().install())
        # chrome_options = webdriver.ChromeOptions()
        # # chrome_options.binary_location = os.environ.get('GOOGLE_CHROME_BIN')
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        # chrome_options.add_argument('--no-sandbox')
        # chrome_options.add_argument('--disable-dev-shm-usage')

        browser = webdriver.Chrome(service=service)

        # browser.set_window_size(950, 800)

        browser.get("https://edition.cnn.com/health")
        html = browser.page_source
        soup = BeautifulSoup(html, 'lxml')
        tags = soup.find('h2', string='Latest').find_next_siblings('li')

        for tag in tags:
            articles.append(tag.find_next(
                'span', class_='cd__headline-text').get_text())

        # browser.close()
        # driver.quit()

        return render(request, 'conag/index.html', {'articles': articles})
