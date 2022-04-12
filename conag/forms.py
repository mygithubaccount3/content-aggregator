from django import forms
from decouple import config


class SearchForm(forms.Form):
    query = forms.CharField(label='', max_length=100, required=False, error_messages={'max_length': 'Max query length: 100'},
                            widget=forms.TextInput(attrs={'class': 'form-control me-2 search-field', 'type': 'search', 'placeholder': 'Search', 'aria-label': 'Search'}))

    page = forms.IntegerField(max_value=50, min_value=1, required=False)

    def search(self, html_tags, source):
        articles = []

        for tag in html_tags:
            article = {
                'title': '',
                'summary': '',
                'tag': '',
                'time': '',
                'link': ''
            }

            article_title_tag = None
            article_summary_tag = None
            article_tag_tag = None
            article_time_tag = None

            if source == 'bbc':
                article_title_tag = tag.select_one('div > div > a')
                article_summary_tag = tag.select_one('div > div > p')
                article_tag_tag = tag.select_one(
                    'div > div:last-of-type > div > dl > div:nth-of-type(2) > dd')
                article_time_tag = tag.select_one(
                    'div > div:last-of-type > div > dl > div:first-of-type > dd > span > span:nth-of-type(2)')
                article.update(link=f"{config('BBC_WEBSITE') + article_title_tag.get('href')}")
            elif source == 'cnn':
                article_title_tag = tag.select_one('article a')
                article.update(link=f"{config('CNN_WEBSITE') + article_title_tag.get('href')}")

            if article_title_tag is not None:
                if ((self.cleaned_data.get('query') in article_title_tag.get_text())):
                    article.update(title=article_title_tag.get_text())
                else:
                    continue
            else:
                continue

            if article_summary_tag is not None:
                if ((self.cleaned_data.get('query') in article_summary_tag.get_text())):
                    article.update(summary=article_summary_tag.get_text())

            if article_tag_tag is not None:
                article.update(tag=article_tag_tag.get_text())

            if article_time_tag is not None and 'ago' in article_time_tag.get_text():
                article.update(time=article_time_tag.get_text())

            articles.append(article)

        return articles
