#coding: utf-8
import re
import urllib
from datetime import date

from bs4 import BeautifulSoup
from simplejson import dumps

class SuperjobCalendarParser():

    def __init__(self, base_url, debug=False):
        self.base_url = base_url
        self.days = {}
        self.debug = debug
        self.months_names = {
            u'Январь': 1,
            u'Февраль': 2,
            u'Март': 3,
            u'Апрель': 4,
            u'Май': 5,
            u'Июнь': 6,
            u'Июль': 7,
            u'Август': 8,
            u'Сентябрь': 9,
            u'Октябрь': 10,
            u'Ноябрь': 11,
            u'Декабрь': 12,
        }
        self._go()

    def _go(self):
        self.get_years_links()
        self.parse_calendar()

    def _get_soup(self, url):
        if self.debug:
            print 'fetch', url
        return BeautifulSoup(urllib.urlopen(url).read().decode('utf8'))

    def _to_date(self, year, month, day):
        return date(int(year), self.months_names.get(month), int(day))

    def get_years_links(self):
        soup = self._get_soup(self.base_url)
        links = soup.findAll('a', {'href': re.compile(self.base_url + '(\d+)/')})
        this_year = soup.find('span', {'class': 'bigger'}).get_text()
        self.year_links = dict([(re.findall(self.base_url + '(\d+)/', l.attrs['href'])[0], l.attrs['href']) for l in links])
        self.year_links.update({int(this_year): self.base_url})

    def parse_calendar(self):
        for year, url in self.year_links.iteritems():
            soup = self._get_soup(url)
            for month in soup.findAll('td', {'class': 'pk_container'}):
                month_text = month.find('div', {'class': 'pk_header'}).get_text()
                for day in month.find('div', {'class': 'pk_cells'}).findAll('div'):
                    if day.attrs['class'] != ['pk_other']:
                        date_day = self._to_date(year, month_text, day.get_text())
                        if day.attrs['class'] == ['pk_holiday', 'pie']:
                            self.days[date_day] = 'holiday'
                        elif day.attrs['class'] == ['pk_preholiday', 'pie']:
                            self.days[date_day] = 'short'
                        else:
                            self.days[date_day] = 'work'

    def serialize(self):
        return dumps(dict([(x[0].isoformat(), x[1]) for x in self.days.iteritems()]))


# example:

if __name__ == '__main__':
    s = SuperjobCalendarParser('http://www.superjob.ru/proizvodstvennyj_kalendar/', debug=True)

    all_days = s.days
    print all_days.get(date(2012, 2, 2))
    print all_days.get(date(2008, 1, 23))
    print all_days.get(date(2014, 1, 7))
    print all_days.get(date(2014, 2, 2))

    # json for save
    json = s.serialize()
