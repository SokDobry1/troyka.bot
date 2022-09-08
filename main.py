import requests
from bs4 import BeautifulSoup as bs
HEADERS = {"Authorization": "Basic U29rRG9icnk6MTIzNTEyMzVhcA=="}

def get_tarifs(uid): pass # Функция внизу

name = {"f": "Тест", "i": "Тестов", "o": "4"}
user_id = 0 
tarifs = get_tarifs(17096)







#url = "https://pult.well-telecom.ru"


#response = requests.get(url, headers=headers)
def create_user(name):
    global HEADERS
    _url=f"https://pult.well-telecom.ru/?mod=users&act=addusr&segment=7&cli_type=0&paytype=0&name_f={name['f']}&name_i={name['i']}&name_o={name['o']}&shortname=&dog_num=&dog_date=08.09.2022&dogbyid=on&login=&loginbyid=on&email=&lim_money=0&phone1=&phone2=&phone3=&objectname=%D0%A1%D0%9F%D0%B1%2C+1+%D0%9C%D1%83%D1%80%D0%B8%D0%BD%D1%81%D0%BA%D0%B8%D0%B9+%D0%BF%D1%80%D0%BE%D1%81%D0%BF%D0%B5%D0%BA%D1%82+%D0%B4.1+%D0%BA.2&objid=5075&street_1586771035=194&flat=&par=&flor=&alsoloaded=1&save=%D0%94%D0%BE%D0%B1%D0%B0%D0%B2%D0%B8%D1%82%D1%8C+%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D0%B5%D0%BB%D1%8F"
    response = requests.post(_url, headers=HEADERS)
    status_str = bs(response.text, "html.parser").find_all('p')[1]
    if status_str["class"][0] == "Error": raise Exception("Пользователь уже существует")
    else:
        txt = status_str.contents[0]
        id_pos = txt.find("ID: ") + len("ID: ")
        temp = ""
        for x in txt[id_pos:]:
            if x.isdigit(): temp += x
            else: return int(temp)
        
#print(create_user(name))


def get_tarifs(uid):
    global HEADERS
    _url = f"https://pult.well-telecom.ru/?mod=users&act=trflist&uid={uid}&service=INET&FormName=form1&InputName=tarifid&DisplayName=tarifname&reload=yes&show=noheader"
    response = requests.get(_url, headers=HEADERS)

    def get_names(response): #Возвращает массив названий тарифов
        names = bs(response.text, "html.parser").find_all("b")
        return [i.contents[0] for i in names]

    def get_prices(response): #Возвращает массив цен
        prices = bs(response.text, "html.parser").find_all("td")[2::2]
        temp = []
        for i in prices:
            temp += [""]; i= str(i)
            for x in str(i): 
                if x.isdigit(): temp[-1] += x
            temp[-1] = int(temp[-1])
        return temp

    def get_tarifids(response): #Возвращает массив с айди тарифов
        tarifids = bs(response.text, "html.parser").find_all("td")[1::2]
        raw_id = [i.contents[0] for i in tarifids]; temp = []
        for i in raw_id:
            answ = ""
            for x in i:
                if x.isdigit(): answ += x
            temp += [answ]
        return temp
    
    temp = {}
    names, prices, tarifids = get_names(response), get_prices(response), get_tarifids(response)
    for i in range(len(names)):
        temp.update({names[i]: {"tarifid": tarifids[i], "price": prices[i]}})
    return temp

def add_tarif(uid, tarifid):
    from datetime import datetime
    date_start = f"{datetime.now().day}.{datetime.now().mounth}.{datetime.now().year}"
    url=f"https://pult.well-telecom.ru/?mod=users&act=edituserservice&uid={uid}&reload=yes&show=noheader&service=INET&bw_type=AUTO&noipcost=0&tarifid={tarifid}&date_start={date_start}&curdescription&save=Сохранить изменения"