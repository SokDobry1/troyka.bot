restart = True # Если какого то модуля нет, то нужно будет перезапустить мэйн

try:
    import json
except:
    import pip
    pip.main(['install', 'json'])
    restart = False

try:
    import vk_api
except:
    import pip
    pip.main(['install', 'vk_api'])
    restart = False

try:
    import vk
except:
    import pip
    pip.main(['install', 'vk'])
    restart = False

assert restart, "Все модули установлены, перезапустите главную программу"