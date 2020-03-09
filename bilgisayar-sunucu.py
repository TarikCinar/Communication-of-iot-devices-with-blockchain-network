
import hashlib
import socket
import json5

#son zinciri veriyor
def veriAl():
    with open('data.json') as json_file:
        data = json5.load(json_file)
        data = data[-1]
    return data

#veri doğrulanırsa zincire ekleniyor
def veriEkle(veri):
    veri=json5.loads(veri)

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

#gelen zinciri kontrol ediyor doğru iste true yanlış ise flase yolluyor
def kontrol(veri):
    sonZincir = oncekiZincir()
    hash = sonZincir[0]
    index = sonZincir[2]
    veri = json5.loads(veri)
    if hash == veri["prev_hash"] and index == veri["index"] - 1:
        return True
    return False

#önceki zinciri veriyor
def oncekiZincir():
    with open("data.json") as file:
        data = json5.load(file)
        data = data[-1]
    veriler = [data["hash"], data["proof"], data["index"]]
    return veriler

##hash atmamızı sağlayan fonksiyon
def hash():
    with open("data.json") as file:
        data = json5.load(file)
        data = str(data[-1])
    return hashlib.sha224(data.encode()).hexdigest()

##tüm zinciri listeleye biliyoruz
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

#suan flask olmadığı için herhangi bir işlem yapmıyoruz gelen verilerle
def islemler(mesaj):
    print(mesaj)


##burası raspberryden gelecek verileri tutmamızı sağlayan sunucu kodu
def sunucu():
    sunucuSoketi = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '' # burası localhostta çalışırrrr
    port = 12345
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
            if kontrol(istemcidenGelenMesaj.decode()): # raspberryden gelen mesaj once kontrol ediliyor eğer kontrol doğrulanırsa hem zincire yollanıyor hemde raspberrye true degeri yollanıyor
                veriEkle(istemcidenGelenMesaj.decode())
                baglanti.send("true".encode())
            else:
                baglanti.send("false".encode())
        baglanti.close()
        print(baglantiAdedi, "nolu istemci ile baglanti kesildi.")
        baglantiAdedi += 1

sunucu()

