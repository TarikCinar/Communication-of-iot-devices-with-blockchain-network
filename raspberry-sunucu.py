
import RPi.GPIO as GPIO
import time
import socket
import sys

import json5
import hashlib

#raspberry pinlerini açıp bmc dizilimini ayarlıyoruz ve 12. pine çıkış veriyoruz
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(12, GPIO.OUT)

def veriEkle(veri):
    veri = json5.loads(veri)
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
    islemler(veri["islem"])

#bilgisayardan gelen işlemlerin yapıldığı blok
def islemler(islem):
    print("islem :",islem)
    if islem == "isik ac":
        GPIO.output(12, GPIO.HIGH)
        print("isik acildi")
    if islem == "isik kapat":
        GPIO.output(12, GPIO.LOW)
        print("isik kapandi")


def kontrol(veri):
    sonZincir = oncekiZincir()
    o_hash = sonZincir[0]
    o_index = sonZincir[2]
    veri = json5.loads(veri)
    if o_hash == veri["prev_hash"] and o_index == veri["index"] - 1:
        print("kontrol dogru")
        return True
    print("kontrol yanlış")
    return False


def oncekiZincir():
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

def listele():
    with open("data.json") as openfile:
        zincir = json5.load(openfile)
    for i in zincir:
        print("{")
        print("    'islem:'", i["islem"])
        print("    'prev_hash:'", i["prev_hash"])
        print("    'hash:'", i["hash"])
        print("    'timestamp:'", i["timestamp"])
        print("    'proof:'", i["proof"])
        print("    'index:'", i["index"])
        print("}")

def sunucu():
    sunucuSoketi = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = ''
    port = 5000
    Buffer_Boyutu = 1024
    sunucuSoketi.bind((host, port))
    sunucuSoketi.listen(5)
    print("\n" + str(port), "portu acildi ve baglantilar dinleniyor" + "\n")
    baglantiAdedi = 1

    while True:
        print("\n" + "*******************************************" + "\n")
        print(baglantiAdedi, "nolu baglanti bekleniyor....")
        baglanti, istemciIPAdresi = sunucuSoketi.accept()  # Baglanti talebi olusturuldu
        print("istemciden gelen", baglantiAdedi, "nolu baglanti kabul edildi")
        print('Baglanan istemci IP Adresi ve Portu:', istemciIPAdresi)
        print("Istemciden mesaj alinmasi bekleniyor...")
        while True:
            istemcidenGelenMesaj = baglanti.recv(Buffer_Boyutu)
            if not istemcidenGelenMesaj:
                break
            print("Istemciden mesaj geldi: ", istemcidenGelenMesaj.decode())
            print("Istemciden mesaj alindi ve Buffer bosaldi.", baglantiAdedi, "nolu istemci ile baglanti kesiliyor...")
            if kontrol(istemcidenGelenMesaj.decode()):
                veriEkle(istemcidenGelenMesaj.decode())
                baglanti.send("true".encode())
            else:
                baglanti.send("false".encode())
        baglanti.close()
        print(baglantiAdedi, "nolu istemci ile baglanti kesildi.")
        baglantiAdedi += 1

sunucu()

