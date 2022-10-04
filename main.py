import traceback
import importer
from mikrotik_api import Mikrotik_api as mk_api
from pult_api import Pult_api as pult_api
from transliterate import translit

def mac_checker(mac):
    if len(mac.split(":")) != 6 and len(mac.split("-")) != 6:
        return False
    return True

try:

    mk = mk_api()
    pult = pult_api()

    print("""Добро пожаловать в меню скрипта. Выберите задачу:
1) Создать пользователя
2) Добавить ip адреса
3) Заполнить таблицу mikrotik пустыми слотами
4) Удалить ip адрес из профиля
5) Добавить денег на счёт""")
    answ = input()

    if answ in ["1","2","5",]:
        name = {"f": "", "i": "", "o": ""}
        name["f"] = input("Введите фамилию: ")
        name["i"] = input("Введите имя: ")

    if answ == "1": name["o"] = input("Введите отчество: ")

    if answ == "1":
        tarifs = pult.get_tarifs(937) # {<Имя тарифа>: {"tarifid": <Айди тарифа>, "price": <Стоимость>}}
        print(*[i for i in tarifs], "Введите название тарифа, выше доступные тарифы (лучше копировать название):", sep='\n')
        selected_tarif = input()
        try: tarifs[selected_tarif]
        except: raise Exception("Неверное название тарифа")


        uid = pult.create_user(name)
        pult.add_auth_without_login(uid)
        pult.add_status(uid)
        pult.add_tarif(uid, tarifs[selected_tarif]["tarifid"])
        pult.deposit_money(uid, tarifs[selected_tarif]["price"])

    if answ in ["2","5"]: 
        if name["i"] == "": temp = f"{name['f']}"
        else: temp = f"{name['f']}+{name['i']}"
        uid = pult.find_uid(name=temp)

    if answ in ["1","2"]:
        while True:
            print("Добавляем:\n1)Проводное устройство\n2)Беспроводное устройство")
            inp = input()
            if inp == "1":
                mac = input("Введите MAC адрес устройства: ")
                while not mac_checker(mac): mac = input("Введите MAC адрес устройства: ")

                data = mk.find_free_ip()
                mk.remove_slot(data)
                mk.add_user(data, mac, translit(f"{name['f']} {name['i']}", language_code='ru', reversed=True))
                pult.add_ip(uid, data["=address"])
            elif inp == "2":
                mac = input("Введите MAC адрес устройства: ")
                while not mac_checker(mac): mac = input("Введите MAC адрес устройства: ")

                data = mk.find_free_ip(wireless=True)
                mk.remove_slot(data)
                mk.add_user(data, mac, "MOBILE: " +translit(f"{name['f']} {name['i']}", language_code='ru', reversed=True))
                pult.add_ip(uid, data["=address"])
            else: break

    if answ == "3":
        start = input("IP старта (по умолчанию 10.24.196.1): ")
        if start:
            mk.fill_free_slots(start)
        else: mk.fill_free_slots()

    if answ == "4":
        ip = input("Введите IP для удаления: ")
        data = mk.get_ip_data(ip)
        mk.remove_slot(data)
        mk.add_free_slot(data)
        uid = pult.find_uid(ip=ip)
        pult.remove_ip(uid, ip)

    if answ == "5":
        amount = input("Введите количество денег для внесения: ")
        pult.deposit_money(uid, amount)

except Exception as e:
    print("Ошибка в работе:", e, sep=" ")

input("Завершена работа программы, нажмите ENTER")