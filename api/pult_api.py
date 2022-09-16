import requests
from bs4 import BeautifulSoup as bs
from secure import headers


class Pult_api:
    def __init__(self):
        self.headers = headers

    def create_user(self, name):
        _url=f"https://pult.well-telecom.ru/?mod=users&act=addusr&segment=7&cli_type=0&paytype=0&name_f={name['f']}&name_i={name['i']}&name_o={name['o']}&shortname=&dog_num=&dog_date=08.09.2022&dogbyid=on&login=&loginbyid=on&email=&lim_money=0&phone1=&phone2=&phone3=&objectname=%D0%A1%D0%9F%D0%B1%2C+1+%D0%9C%D1%83%D1%80%D0%B8%D0%BD%D1%81%D0%BA%D0%B8%D0%B9+%D0%BF%D1%80%D0%BE%D1%81%D0%BF%D0%B5%D0%BA%D1%82+%D0%B4.1+%D0%BA.2&objid=5075&street_1586771035=194&flat=&par=&flor=&alsoloaded=1&save=%D0%94%D0%BE%D0%B1%D0%B0%D0%B2%D0%B8%D1%82%D1%8C+%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D0%B5%D0%BB%D1%8F"
        response = requests.post(_url, headers=self.headers)
        status_str = bs(response.text, "html.parser").find_all('p')[1]
        if status_str["class"][0] == "Error": raise Exception("Пользователь уже существует")
        else:
            txt = status_str.contents[0]
            id_pos = txt.find("ID: ") + len("ID: ")
            temp = ""
            for x in txt[id_pos:]:
                if x.isdigit(): temp += x
                else:
                    print(f"Пользователь создан с id {int(temp)}") 
                    return int(temp)
        Exception("Ошибка при создании пользователя")
            


    def get_tarifs(self, uid):
        
        _url = f"https://pult.well-telecom.ru/?mod=users&act=trflist&uid={uid}&service=INET&FormName=form1&InputName=tarifid&DisplayName=tarifname&reload=yes&show=noheader"
        response = requests.get(_url, headers=self.headers)

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
        print("Получены данные о тарифах")
        return temp

    def add_tarif(self, uid, tarifid):
        
        from datetime import datetime
        date_start = f"{datetime.now().day}.{datetime.now().month}.{datetime.now().year}"
        _url=f"https://pult.well-telecom.ru/?mod=users&act=edituserservice&uid={uid}&reload=yes&show=noheader&service=INET&bw_type=AUTO&noipcost=0&tarifid={tarifid}&date_start={date_start}&curdescription&save=Сохранить изменения"
        response = requests.post(_url, headers=self.headers)
        print("Добавлен тариф")

    def add_status(self, uid):
        
        from datetime import datetime
        date_start = f"{datetime.now().day}.{datetime.now().month}.{datetime.now().year}"
        _url = f"https://pult.well-telecom.ru/?mod=users&act=statuschange&uid={uid}&newstatus=1&datestart={date_start}&timestart=00:00:00&save=1&confirmed=Подтвердить назначение нового статуса"
        response = requests.post(_url, headers=self.headers)
        print("Создан статус активности")

    def add_auth_without_login(self, uid):
        
        _url = f"https://pult.well-telecom.ru/?mod=users&act=editusr&uid={uid}&save=1&shortname=&login={uid}&pwd1=&pwd2=&lknopass_enable=1&email=&lim_money=0&lim_months=0&money_alert_porog=50&phone1=&phone2=&phone3=&sms=&sms_old=&sms_lang_old=&sms_status_old=&sms_lang=RUS&sms_status=ACTIVE&objid=5075&street_561433143=&flat=&par=&flor=&chtarif=1"
        response = requests.post(_url, headers=self.headers)
        print("Включена функция входа без логина и пароля")

    def deposit_money(self, uid, amount):
        def rand_hex_gen():
            import random
            answ = ""
            for i in range(32):
                answ += format(random.randint(1,16), 'x')
            return answ

        
        from datetime import datetime
        cur_date = f"{datetime.now().day}.{datetime.now().month}.{datetime.now().year}"
        _url = f"https://pult.well-telecom.ru/?mod=users&act=addpay&uid={uid}&pay_unique={rand_hex_gen()}&pay_type=1&pay_docnum=&datepay={cur_date}&sumpay={amount}&confirmed_pay=1&pay_doc=&save=Зачислить+на+лицевой+счет"
        response = requests.post(_url, headers=self.headers)
        print(f"Внесены средства в размере {amount} рублей")

    def add_ip(self, uid, ipaddr, comment=""):
        
        _url = f"https://pult.well-telecom.ru/?mod=users&act=editip&uid={uid}&id=&service=33653&ipaddr={ipaddr}&mac=&comment={comment}&enable=on&autoban=on&autoban_smtp=on&save=Добавить"
        response = requests.post(_url, headers=self.headers)
        print(f"Добавлен ip: {ipaddr}")

    def find_uid(self, ip="", name=""):
        if ip:
            _url = f"https://pult.well-telecom.ru/?mod=users&act=list&go=1&searchwellpay=&search_region=0&search_district=&objectname=&objid=&street=&par=&flor=&flat=&wherefind=fullname&part=all&query=&phone=&userIp[]={ip}&searchmac=&searchvlan=&search_service=&userstatus=-2&statusdaysznak=min&statusdays=&traffic_last_days=&cli_type=&paytype=-1&speedtype=&isvip=&isPon=&minbalanceznak=>&minbalance=&loyalty=&ticksign=>&tickcnt=&trf_inet_price_sign=>&trf_inet_price=&trf_other_price_sign=>&trf_other_price=&users_equipment_name=&users_equipment_desc=&ticket_last_date=&go=1"
        elif name: _url = f"https://pult.well-telecom.ru/?mod=users&act=list&go=1&searchwellpay=&search_region=0&search_district=&objectname=&objid=&street=&par=&flor=&flat=&wherefind=fullname&part=all&query={name}&phone=&searchmac=&searchvlan=&search_service=&userstatus=-2&statusdaysznak=min&statusdays=&traffic_last_days=&cli_type=&paytype=-1&speedtype=&isvip=&isPon=&minbalanceznak=>&minbalance=&loyalty=&ticksign=>&tickcnt=&trf_inet_price_sign=>&trf_inet_price=&trf_other_price_sign=>&trf_other_price=&users_equipment_name=&users_equipment_desc=&ticket_last_date=&go=1"
        response = requests.get(_url, headers=self.headers)
        data = bs(response.text, "html.parser").find_all("tr", {"class":"first"})
        if len(data):
            uid = data[0].a.contents[0]
            return uid
        raise Exception("Ничего не найдено")

    def remove_ip(self, uid, ip):
        _url = f"https://pult.well-telecom.ru/?mod=users&act=viewips&uid={uid}"
        response = requests.get(_url, headers=self.headers)
        data = bs(response.text, "html.parser").find_all("table", {"class":"Users"})[0]
        list_lines = data.find_all("tr")[1:]
        for i in list_lines:
            cur_ip = i.b.contents[0]
            if cur_ip == ip:
                ip_id = i.find_all("input")[2]["value"]
                _url = f"https://pult.well-telecom.ru/?mod=users&act=viewips&uid={uid}&delip={ip_id}"
                response = requests.post(_url, headers=self.headers)
                print(f"IP {cur_ip} удалён у пользователя {uid}")
                return
        raise Exception("IP не обнаружен")
    




if __name__ == '__main__':
    pult = Pult_api()
    pult.remove_ip("17261", "10.24.200.81")
"""
    name = {"f": "", "i": "", "o": ""}
    name["f"] = input("Введите фамилию: ")
    name["i"] = input("Введите имя: ")
    name["o"] = input("Введите отчество: ")

    tarifs = get_tarifs(937) # {<Имя тарифа>: {"tarifid": <Айди тарифа>, "price": <Стоимость>}}
    print(*[i for i in tarifs], "Введите название тарифа, выше доступные тарифы (лучше копировать название):", sep='\n')
    selected_tarif = input()
    tarifs[selected_tarif]


    uid = create_user(name)
    add_auth_without_login(uid)
    add_status(uid)
    add_tarif(uid, tarifs[selected_tarif]["tarifid"])
    deposit_money(uid, tarifs[selected_tarif]["price"])
"""