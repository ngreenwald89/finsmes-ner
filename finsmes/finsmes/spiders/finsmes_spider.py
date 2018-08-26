import csv
import codecs
import scrapy


class FinsmesSpider(scrapy.Spider):
    name = "finsmes"

    def start_requests(self):
        # urls = [
        #     'http://www.finsmes.com/category/usa/page/1',
        #     'http://www.finsmes.com/category/usa/page/2',
        # ]
        urls = [
            'http://www.finsmes.com/category/usa/page/{}'.format(i) for i in range(1816)
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def tutorial_parse(self, response):
        """
        https://doc.scrapy.org/en/latest/intro/tutorial.html
        :param response:
        :return:
        """
        page = response.url.split("/")[-2]
        filename = 'pages-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)

    def parse(self, response):
        """

        :param response: TextResponse object. Page of finsmes articles, with article summaries
        :return: list of article summaries as strings. write to file
        """
        # article summaries are in entry-summary tags
        p_text = response.css('div.entry-summary p::text').extract()
        urls = response.css('div.entry-summary div.at-above-post-cat-page.addthis_tool::attr(data-url)').extract()
        zipped = zip(urls, p_text)


        page_number = response.url.split('/')[-1]
        filename = 'files/page-%s.csv' % page_number

        with codecs.open(filename, 'w', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['url', 'summary'])
            for row in zipped:
                try:
                    w.writerow(row)
                except Exception as e:
                    self.log('{}: {}. Failed to write row: {}.'.format(filename, e, row))
