import sys, time, binascii, socket, select, ssl
import hashlib
from secure import mikrotik as mk

class Mikrotik_api:
    "Routeros api"
    def __init__(self):
        self.sk = self.open_socket(mk.dst, "8728")
        if self.sk is None: raise RuntimeError('could not open socket') 
        self.currenttag = 0
        if not self.login(): raise Exception("Неправильный логин или пароль") 

    def fill_free_slots(self, start="10.24.196.1"):
        from pult_api import Pult_api as pult
        pult = pult()
        ip =[f"10.24.{i1}.{i2}" for i1 in range(196,198+1) for i2 in range(1,256)]
        ip +=[f"10.24.{i1}.{i2}" for i1 in range(200,201+1) for i2 in range(1,256)]
        ip = ip[ip.index(start):]
        for i in ip:
            print(i)
            data = self.talk(["/ip/dhcp-server/lease/print", "=proplist=address", f"?address={i}"])[0]

            if data[0] == "!re":
                pos = data[1]["=last-seen"].find("w")
                if pos+1:
                    if int(data[1]["=last-seen"][:pos]) > 100:
                        print(f"Устройство {data[1]['=comment']} не выходило на связь уже {data[1]['=last-seen'][:pos]} недель и было удалено",
                            f"MAC адрес: {data[1]['=mac-address']}", sep="\n")
                        self.remove_slot(data[1])
                        try:
                            uid = pult.find_uid(ip=data[1]["=address"])
                            pult.remove_ip(uid, data[1]["=address"])
                        except: pass
                        data = (None, data[1])

            if data[0] != "!re":
                self.add_free_slot({"=address": i})

    def find_free_ip(self, wireless=False): #Возвращает список информации о слоте
        ip = []
        if wireless: ip =[f"10.24.{i1}.{i2}" for i1 in range(196,198+1) for i2 in range(1,256)]
        else: ip =[f"10.24.{i1}.{i2}" for i1 in range(200,201+1) for i2 in range(1,256)]
        data = self.talk(["/ip/dhcp-server/lease/print", "?comment=FREE SLOT"])[:-1]
        for i in data:
            if i[1]["=address"] in ip:
                return i[1]

    def get_ip_data(self, ip):
        data = self.talk(["/ip/dhcp-server/lease/print", f"?address={ip}"])[0]
        if data[0] != "!re": data = (None, None)
        return data[1]

    def remove_slot(self, slot_data): # Удаляет слот (достаточно только id слота)
        answ = self.talk(["/ip/dhcp-server/lease/remove", f"=numbers={slot_data['=.id']}"])
        if answ[0][0] != "!done": raise Exception("Ошибка удаления слота")
        print(f"Слот IP {slot_data['=address']} удалён")
        

    def add_free_slot(self, slot_data):
        i = slot_data["=address"]; mac = i + "fff"
        self.talk(["/ip/dhcp-server/lease/add", f"=address={i}", "=comment=FREE SLOT", \
                  f"=mac-address=10:24:{mac[6:8]}:{mac[8]}{mac[10]}:{mac[11:13]}:01"])
        print("Внёс пустой слот")


    def add_user(self, slot_data, mac, comment): #Создаёт пользователя
        answ = self.talk(["/ip/dhcp-server/lease/add", f"=address={slot_data['=address']}", 
                          f"=mac-address={mac}",
                          f"=comment={comment}"])
        if answ[0][0] != "!done": raise Exception("Ошибка при создании пользователя")                          


    def login(self):
        for repl, attrs in self.talk(["/login", "=name=" + mk.login,
                                      "=password=" + mk.password]):
          if repl == '!trap':
            return False
          elif '=ret' in attrs.keys():
        #for repl, attrs in self.talk(["/login"]):
            chal = binascii.unhexlify((attrs['=ret']).encode(sys.stdout.encoding))
            md = hashlib.md5()
            md.update(b'\x00')
            md.update(pwd.encode(sys.stdout.encoding))
            md.update(chal)
            for repl2, attrs2 in self.talk(["/login", "=name=" + username,
                   "=response=00" + binascii.hexlify(md.digest()).decode(sys.stdout.encoding) ]):
              if repl2 == '!trap':
                return False
        return True

    def talk(self, words):
        if self.writeSentence(words) == 0: return
        r = []
        while 1:
            i = self.readSentence();
            if len(i) == 0: continue
            reply = i[0]
            attrs = {}
            for w in i[1:]:
                j = w.find('=', 1)
                if (j == -1):
                    attrs[w] = ''
                else:
                    attrs[w[:j]] = w[j+1:]
            r.append((reply, attrs))
            if reply == '!done': return r

    def writeSentence(self, words):
        ret = 0
        for w in words:
            self.writeWord(w)
            ret += 1
        self.writeWord('')
        return ret

    def readSentence(self):
        r = []
        while 1:
            w = self.readWord()
            if w == '': return r
            r.append(w)

    def writeWord(self, w):
        ##print(("<<< " + w))
        self.writeLen(len(w))
        self.writeStr(w)

    def readWord(self):
        ret = self.readStr(self.readLen())
        ##print((">>> " + ret))
        return ret

    def writeLen(self, l):
        if l < 0x80:
            self.writeByte((l).to_bytes(1, sys.byteorder))
        elif l < 0x4000:
            l |= 0x8000
            tmp = (l >> 8) & 0xFF
            self.writeByte(((l >> 8) & 0xFF).to_bytes(1, sys.byteorder))
            self.writeByte((l & 0xFF).to_bytes(1, sys.byteorder))
        elif l < 0x200000:
            l |= 0xC00000
            self.writeByte(((l >> 16) & 0xFF).to_bytes(1, sys.byteorder))
            self.writeByte(((l >> 8) & 0xFF).to_bytes(1, sys.byteorder))
            self.writeByte((l & 0xFF).to_bytes(1, sys.byteorder))
        elif l < 0x10000000:
            l |= 0xE0000000
            self.writeByte(((l >> 24) & 0xFF).to_bytes(1, sys.byteorder))
            self.writeByte(((l >> 16) & 0xFF).to_bytes(1, sys.byteorder))
            self.writeByte(((l >> 8) & 0xFF).to_bytes(1, sys.byteorder))
            self.writeByte((l & 0xFF).to_bytes(1, sys.byteorder))
        else:
            self.writeByte((0xF0).to_bytes(1, sys.byteorder))
            self.writeByte(((l >> 24) & 0xFF).to_bytes(1, sys.byteorder))
            self.writeByte(((l >> 16) & 0xFF).to_bytes(1, sys.byteorder))
            self.writeByte(((l >> 8) & 0xFF).to_bytes(1, sys.byteorder))
            self.writeByte((l & 0xFF).to_bytes(1, sys.byteorder))

    def readLen(self):
        c = ord(self.readStr(1))
        # print (">rl> %i" % c)
        if (c & 0x80) == 0x00:
            pass
        elif (c & 0xC0) == 0x80:
            c &= ~0xC0
            c <<= 8
            c += ord(self.readStr(1))
        elif (c & 0xE0) == 0xC0:
            c &= ~0xE0
            c <<= 8
            c += ord(self.readStr(1))
            c <<= 8
            c += ord(self.readStr(1))
        elif (c & 0xF0) == 0xE0:
            c &= ~0xF0
            c <<= 8
            c += ord(self.readStr(1))
            c <<= 8
            c += ord(self.readStr(1))
            c <<= 8
            c += ord(self.readStr(1))
        elif (c & 0xF8) == 0xF0:
            c = ord(self.readStr(1))
            c <<= 8
            c += ord(self.readStr(1))
            c <<= 8
            c += ord(self.readStr(1))
            c <<= 8
            c += ord(self.readStr(1))
        return c

    def writeStr(self, str):
        n = 0;
        while n < len(str):
            r = self.sk.send(bytes(str[n:], 'UTF-8'))
            if r == 0: raise RuntimeError("connection closed by remote end")
            n += r

    def writeByte(self, str):
        n = 0;
        while n < len(str):
            r = self.sk.send(str[n:])
            if r == 0: raise RuntimeError("connection closed by remote end")
            n += r

    def readStr(self, length):
        ret = ''
        # print ("length: %i" % length)
        while len(ret) < length:
            s = self.sk.recv(length - len(ret))
            if s == b'': raise RuntimeError("connection closed by remote end")
            # print (b">>>" + s)
            # atgriezt kaa byte ja nav ascii chars
            if s >= (128).to_bytes(1, "big") :
               return s
            # print((">>> " + s.decode(sys.stdout.encoding, 'ignore')))
            ret += s.decode(sys.stdout.encoding, "replace")
        return ret

    def open_socket(self, dst, port, secure=False):
        s = None
        res = socket.getaddrinfo(dst, port, socket.AF_UNSPEC, socket.SOCK_STREAM)
        af, socktype, proto, canonname, sockaddr = res[0]
        skt = socket.socket(af, socktype, proto)
        if secure:
            s = ssl.wrap_socket(skt, ssl_version=ssl.PROTOCOL_TLSv1_2, ciphers="ADH-AES128-SHA256") #ADH-AES128-SHA256
        else:
            s = skt
        s.connect(sockaddr)
        return s

   
if __name__ == '__main__': #Мусор для тестов
    from transliterate import translit
    text = translit("Шаймарданова Ляйсан", language_code='ru', reversed=True)
    #mk = Mikrotik_api()
    #print(mk.remove_slot({"=.id": "*17D571"}))
    #mk.fill_free_slots()
    #x=mk.talk(["/ip/dhcp-server/lease/remove", "=numbers=*17D56E"])#?address=10.24.196"]))
    
    #i = "10.24.200.47"+"0"
    #print(f"=mac-address=10:24:{i[6:8]}:{i[8]}{i[10]}:{i[11:13]}:00")
    #print(mk.talk(["/ip/dhcp-server/lease/add", f"=address={i}", "=comment=FREE SLOT", \
                          #f"=mac-address=10:24:{i[6:8]}:{i[8]}{i[10]}:{i[11:13]}:00"]))