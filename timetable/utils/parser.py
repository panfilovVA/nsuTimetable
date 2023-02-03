import requests
from bs4 import BeautifulSoup as bs

response = requests.get("https://table.nsu.ru/group/20213")
soup = bs(response.text)
subjects = soup.find_all('div', {"class": "subject"})
res = [[], [], []]  # room teacher subject
for subject in subjects:
    subj = {"name": subject["title"].strip()}
    if subject.previousSibling.previousSibling.text.strip() == "пр" or subject.previousSibling.previousSibling.text.strip() == 'ф, пр' or subject.previousSibling.previousSibling.text.strip() == 'лаб':
        subj["type"] = "Seminar"
    elif subject.previousSibling.previousSibling.text.strip() == 'лаб':
        subj["type"] = "Lecture"
    if {"name": subject.nextSibling.nextSibling.text.strip()} not in res[0]:
        res[0].append({"name": subject.nextSibling.nextSibling.text.strip()})
    if subject.nextSibling.nextSibling.nextSibling.nextSibling is not None:
        if {"name": subject.nextSibling.nextSibling.nextSibling.nextSibling.text.strip()} not in res[1]:
            res[1].append({"name": subject.nextSibling.nextSibling.nextSibling.nextSibling.text.strip()})
        subj["teacher"] = subject.nextSibling.nextSibling.nextSibling.nextSibling.text.strip()

    if subj not in res[2]:
        res[2].append(subj)
print(res)
