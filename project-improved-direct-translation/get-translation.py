import urllib.request
from bs4 import BeautifulSoup

contents = urllib.request.urlopen("https://sv.bab.la/lexikon/svensk-engelsk/l%C3%A4nk").read()

# https://www.crummy.com/software/BeautifulSoup/bs4/doc/
soup = BeautifulSoup(contents, 'html.parser')
# print(soup.prettify())
translations = soup.body.find('ul', attrs={'class':'sense-group-results'}).find_all('a')
translations_text = []
for translation in translations:
    translations_text.append(translation.string)
    
print(translations_text)