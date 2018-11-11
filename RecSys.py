from bs4 import BeautifulSoup

import requests

url = 'https://www10.uta.fi/opas/opintojakso.htm?id=30422&lang=en&lvv=2018&uiLang=en'

r = requests.get(url)

data = r.text

soup = BeautifulSoup(data, 'html.parser')

div_elem = soup.find("div", {"class": "department_header department_header_D"})
course_code = div_elem.text.split()[0].strip()

div_elem = soup.find("div", {"class": "infobox_header"})
organiser = div_elem.find_next_sibling('div').text.strip()

study_modules = []
h2_elem = soup.find('h2', text='Belongs to following study modules')
div_elem = h2_elem.find_next_sibling('div')
for link in div_elem('a'):
    study_modules.append(link.string)

h2_elem = soup.find('h2', text='Teaching language')
teaching_language = h2_elem.next_sibling.strip()

div_elem = soup.find("div", {"class": "opintojakso_toteutukset_wrapper"})
links = []
teacher = ''
for link in div_elem.findChildren('a'):
    links.append(link.get('href'))
for link in links:
    r = requests.get('https://www10.uta.fi' + link)
    data = r.text
    soup = BeautifulSoup(data, 'html.parser')
    h2_elem = soup.find('h2', text='Teachers')
    teacher = h2_elem.find_next_sibling('div').find("div", {"class": "ope"}).text.split(',')[0].strip()

print(course_code)
print(organiser)
for study_module in study_modules:
    print(study_module)
print(teaching_language)
print(teacher)
