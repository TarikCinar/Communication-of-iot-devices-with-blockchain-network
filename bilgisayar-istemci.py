import socket
import json5
import time
import hashlib

data={}
##komut alındıktan sonra burada bir önceki zincire göre yeni bir zincir oluşturuluyor ama raspberrryden true değeri gelmediği sürece bu zincir blockchain
##zincirine eklenmiyorki karşılıklı olarak aynı düzeyde zincir oluşsun yoksa bir karmaşıklık olur
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

##burada vir önceki zincirin hash , proof ve index değerini döndürüyor
def prew_chain():
    with open("data.json") as file:
        data = json5.load(file)
        data = data[-1]
    veriler = [data["hash"], data["proof"], data["index"]]
    return veriler


##bu fonksiyon yeni bir hash oluşturuyor
def hash():
    with open("data.json") as file:
        data = json5.load(file)
        data = str(data[-1])
    return hashlib.sha256(data.encode()).hexdigest()

##bu fonksiyon en son zinciri döndürüyor
def veriAl():
    with open('data.json') as json_file:
        data = json5.load(json_file)
        data = data[-1]
    return data

#bu fonksiyon raspberryden true değeri gelirse oluşturulan block zincirini blockchain zincirine ekliyor
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


####burada raspberrynin sunucusuna bağlanarak aşağıdaki komuta göre işlemleri yolluyor
def istemci(data):
    istemciSoketi = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = "192.168.43.73"
    port = 5000
    Buffer_Boyutu = 1024
    istemciSoketi.connect((host, port))
    mesaj=str(data)
    print("Gonderilecek veri: ", mesaj.encode())
    istemciSoketi.send(mesaj.encode())
    print("Veri sunucuya basarili bir sekilde gonderildi.")
    sunucudanGelenMesaj = istemciSoketi.recv(Buffer_Boyutu).decode()
    print("Sunucudan Gelen Mesaj: ", sunucudanGelenMesaj)
    if sunucudanGelenMesaj=="true": #raspberrye gönderilen zincir doğrulanır ve true değeri gelirse zinciri ağa ekliyoruz
        veriEkle(data)
    print("Sunucudan onay mesaji da alindigina gore; istemci tarafinda da baglanti koparilabilir")
    istemciSoketi.close()

##burada raspberriye yollanacak komut veriliyor ve ilk olarak bir blockchain zinciri oluşturuluyoır
zincirOlustur("isik kapat")