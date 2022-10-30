restart = True # Если какого то модуля нет, то нужно будет перезапустить мэйн

try:
    import bs4
except:
    import pip
    pip.main(['install', 'bs4'])
    restart = False

try:
    import transliterate
except:
    import pip
    pip.main(['install', 'transliterate'])
    restart = False

try:
    import requests
except:
    import pip
    pip.main(['install', 'requests'])
    restart = False

assert restart, "Все модули установлены, перезапустите главную программу"