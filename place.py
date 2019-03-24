import re

filename = 'city.csv'
f = open(filename, 'r')
city = f.read().lower().split('\n')

def place(city_Find):
    cityF = []
    word = re.compile('\w+').findall(city_Find)
    for i in word:
        if i.lower() in city:
            cityF.append(i)
    return cityF