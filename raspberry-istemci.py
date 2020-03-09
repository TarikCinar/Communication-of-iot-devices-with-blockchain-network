import socket
import Adafruit_DHT
import time

import json5
import hashlib

data={}
def zincirOlustur(veri):
    oncekiZincir =prew_chain()
    data = {'islem': veri,
            'prev_hash': oncekiZincir[0],
            'hash': hash(),
            'timestamp': time.time(),
            'proof': oncekiZincir[1] * 2,
            'index': oncekiZincir[2] + 1
            }
    print("veriler eklendi")
    istemci(data)

def prew_chain():
    with open("data.json") as file:
        data = json5.load(file)
        data = data[-1]
    veriler = [data["hash"], data["proof"], data["index"]]
    return veriler


def hash():
    with open("data.json") as file:
        data = json5.load(file)
        data = str(data[-1])
    return hashlib.sha224(data.encode()).hexdigest()


def veriAl():
    with open('data.json') as json_file:
        data = json5.load(json_file)
        data = data[-1]
    return data

def veriEkle(veri):
    print(veri["islem"])
    with open("data.json") as openfile:
        zincir = json5.load(openfile)

    data = {'islem': veri["islem"],
            'prev_hash': veri["prev_hash"],
            'hash': veri["hash"],
            'timestamp': veri["timestamp"],
            'proof': veri["proof"],
            'index': veri["index"]}
    zincir.append(data)
    with open("data.json", "w") as file:
        json5.dump(zincir, file, indent=4, ensure_ascii=False)
    print("veriler eklendi")



def istemci(data):
    istemciSoketi = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = "192.168.43.117"
    port = 12345
    Buffer_Boyutu = 1024
    istemciSoketi.connect((host, port))
    mesaj=str(data)
    print("Gonderilecek veri: ", mesaj.encode())
    istemciSoketi.send(mesaj.encode())
    print("Veri sunucuya basarili bir sekilde gonderildi.")
    sunucudanGelenMesaj = istemciSoketi.recv(Buffer_Boyutu).decode()
    print("Sunucudan Gelen Mesaj: ", sunucudanGelenMesaj)
    if sunucudanGelenMesaj=="true":
        veriEkle(data)
    print("Sunucudan onay mesaji da alindigina gore; istemci tarafinda da baglanti koparilabilir")
    istemciSoketi.close()

##iki dakikada bir dht11 sensöründen verileri çekerek bilgisayara gönderir
sayac=0
while True:
    dakika=int(time.strftime("%M"))
    if dakika %2==0:
        if sayac!=1:
            sicaklik, nem = Adafruit_DHT.read_retry(11, 4)
            zincirOlustur({"sicaklik":str(int(sicaklik)),"nem":str(int(nem))})
        sayac=1
    else:
        sayac=0

