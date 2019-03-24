""" import requests
from bs4 import BeautifulSoup
import csv

response = requests.get(f"https://www.citypopulation.de/php/india-westbengal.php")

soup = BeautifulSoup(response.content, 'html5lib')


table = soup.find_all('td', attrs = {'class':'rname'})

print("Writing start in file")

for i in table:
    if str(type(i.a)) == "<class 'bs4.element.Tag'>":
        filename = 'city.txt'
        f = open(filename, 'a') 
        f.write(f"{i.a.text}\n")
    else:
        pass

print("Write Complete") """

import csv
import re

city_Find = "want to go Naihati but barasat"
filename = 'city.csv'
f = open(filename, 'r')

city = f.read().lower().split('\n')
print(city)

cityF = []
word = re.compile('\w+').findall(city_Find)
for i in word:
    if i.lower() in city:
        cityF.append(i)
print(cityF)
