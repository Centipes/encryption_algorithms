
import math
from PyQt5 import QtCore


#---------------------------------------

PI19 = 3141592653589793238
E19 = 2718281828459045235
R220 = 14142135623730950488

IV = 278939022647121645315628355772935338798

SUBCHIPHERS_NUM = 3

lmask = 0xFFFFFFFFFFFFFFFF
blocksize = 128

def mod(x): return x & lmask
def xor(x, y): return mod(x ^ y)
def l_sh(x, y): return mod(x << y)
def r_sh(x, y): return mod(x >> y)
def add(x, y): return mod(x + y)
def sub(x, y): return mod(x - y)
def mul(x, y): return mod(x * y)
def _or(x, y): return mod(x | y)
def _and(x, y): return mod(x & y)


# повернуть влево на количество битов субшифра, то есть 3 (циклический сдвиг влево)
def rot(x, shift, size=64):
    return mod(_or(l_sh(x, shift), r_sh(x, size - shift)))


def expand_key(key, key_len):
    # Этап 1. Инициализация
    kx = []
    # Инициализация первых трех слов
    kx.append(add(PI19, SUBCHIPHERS_NUM))
    kx.append(mul(E19, key_len))
    kx.append(rot(R220, SUBCHIPHERS_NUM))

    # Инициализация остальных слов
    for i in range(3, 256):
        kx.append(add(xor(xor(r_sh(kx[i-3], 23),l_sh(kx[i-3], 41)), kx[i-2]),kx[i-1]))


    key_words = int_to_arr(key)

    # Этапы 2 и 3
    for j in range(math.ceil(len(key_words)/128)):
        for i in range(min(len(key_words)-128*j, 128)):
            kx[i] = xor(kx[i], key_words[i+j*128]) # Этап 2. Сложение
        shuffle_key(kx) # Этап 3. Перемешивание

    # Этап 4. Завершающий этап расширения - первые 30 слов добавляются в конец списка kx
    for i in range(30):
        kx.append(kx[i])
    return kx

# Процедура перевода ключа key и дополнительного ключа spice в список
def int_to_arr(num, length=None):

    if not length: # key может иметь произвольную длину, spice и блок входного текста имеют фиксированную длину.
        length = math.ceil((len(bin(num))-2)/64)

    words = []
    for i in range(length):
        words.insert(0, (num>>64*i)&lmask)

    return words

# Процедура перемешивания
def shuffle_key(kx):
    s = []
    for i in range(248, 256):
        s.append(kx[i])

    for j in range(3): # рекомендовано повторить три раза перемешивание
        for i in range(256):
            s[0] = xor(s[0], add(xor(kx[i], kx[(i+83) & 255]), kx[s[0] & 255]))
            s[2] = add(s[2], kx[i])
            s[1] = add(s[0], s[1])
            s[3] = xor(s[3], s[2])
            s[5] = sub(s[5], s[4])
            s[7] = xor(s[7], s[6])
            s[3] = add(s[3], r_sh(s[0], 13))
            s[4] = xor(s[4], l_sh(s[1], 11))
            s[5] = xor(s[5], l_sh(s[3], _and(s[1], 31)))
            s[6] = add(s[6], r_sh(s[2], 17))
            s[7] = _or(s[7], add(s[3], s[4]))
            s[2] = sub(s[2], s[5])
            s[0] = sub(s[0], xor(s[6], i))
            s[1] = xor(s[1], add(s[5], PI19))
            s[2] = add(s[2], r_sh(s[7], j))
            s[2] = xor(s[2], s[1])
            s[4] = sub(s[4], s[3])
            s[6] = xor(s[6], s[5])
            s[0] = add(s[0], s[7])
            kx[i] = add(s[2], s[6])

def output(s):
    return (s[0]<<64)|s[1]

def encrypt(pt, kx, spice):
    pt = int_to_arr(pt, 2)
    s0 = add(pt[0], kx[blocksize])
    s1 = add(pt[1], kx[blocksize+1]) & lmask
    for i in range(8):
        k = kx[s0&255]
        s1 = add(s1, k) & lmask
        s0 = xor(s0, l_sh(k, 8))
        s1 = xor(s1, s0) & lmask
        s0 = sub(s0, r_sh(s1, 11))
        s0 = xor(s0, l_sh(s1, 2))
        s0 = sub(s0, spice[i^4])
        s0 = add(s0, xor(l_sh(s0, 32), add(PI19, blocksize)))
        s0 = xor(s0, r_sh(s0, 17))
        s0 = xor(s0, r_sh(s0, 34))
        t = spice[i]
        s0 = xor(s0, t)
        s0 = add(s0, l_sh(t, 5))
        t = r_sh(t, 4)
        s1 = add(s1, t) & lmask
        s0 = xor(s0, t)
        s0 = add(s0, l_sh(s0, 22 + (s0&31)))
        s0 = xor(s0, r_sh(s0, 23))
        s0 = sub(s0, spice[i^7])
        t = s0&255
        k = kx[t]
        kk = kx[t+3*i+1]
        s1 = xor(s1, k) & lmask
        s0 = xor(s0, l_sh(kk, 8))
        kk = xor(kk, k)
        s1 = add(s1, r_sh(kk, 5)) & lmask
        s0 = sub(s0, l_sh(kk, 12))
        s0 = xor(s0, kk &~ 255)
        s1 = add(s1, s0) & lmask
        s0 = add(s0, l_sh(s1, 3))
        s0 = xor(s0, spice[i^2])
        s0 = add(s0, kx[blocksize+16+i])
        s0 = add(s0, l_sh(s0, 22))
        s0 = xor(s0, r_sh(s1, 4))
        s0 = add(s0, spice[i^1])
        s0 = xor(s0, r_sh(s0, 33+i))

    pt[0] = add(s0, kx[blocksize+8])
    pt[1] = add(s1, kx[blocksize+9]) & lmask

    return output(pt)


def decrypt(ct, kx, spice):
    ct = int_to_arr(ct, 2)
    s0 = sub(ct[0], kx[blocksize+8])
    s1 = sub(ct[1], kx[blocksize+9]) & lmask
    for i in range(7, -1, -1):
        t = s0
        t = r_sh(t, 33+i)
        s0 = xor(s0, t)
        s0 = sub(s0, spice[i^1])
        t = s1
        t = r_sh(t, 4)
        s0 = xor(s0, t)
        k = s0
        k = l_sh(k, 22)
        t = s0
        t = sub(t, k)
        t = l_sh(t, 22)
        s0 = sub(s0, t)
        s0 = sub(s0, kx[blocksize+16+i])
        s0 = xor(s0, spice[i^2])
        t = s1
        t = l_sh(t, 3)
        s0 = sub(s0, t)
        s1 = sub(s1, s0) & lmask
        tt = s0&255;
        k = kx[tt]
        tt += 3 * i + 1
        kk = kx[tt]
        kk = xor(kk, k)
        t = kk & ~255
        s0 = xor(s0, t)
        t = kk
        t = l_sh(t, 12)
        s0 = add(s0, t)
        t = kk
        t = r_sh(t, 5)
        s1 = sub(s1, t) & lmask
        kk = kx[tt]
        kk = l_sh(kk, 8)
        s0 = xor(s0, kk)
        s1 = xor(s1, k) & lmask
        s0 = add(s0, spice[i^7])
        t = s0
        t = r_sh(t, 23)
        s0 = xor(s0, t)
        t = s0
        t = r_sh(t, 46)
        s0 = xor(s0, t)
        tt = 22 + (s0 & 31)
        t = s0
        t = l_sh(t, tt)
        kk = s0
        kk = sub(kk, t)
        kk = l_sh(kk, tt)
        s0 = sub(s0, kk)
        kk = spice[i]
        t = kk
        kk = r_sh(kk, 4)
        s0 = xor(s0, kk)
        s1 = sub(s1, kk) & lmask
        k = t
        k = l_sh(k, 5)
        s0 = sub(s0, k)
        s0 = xor(s0, t)
        t = s0
        t = r_sh(t, 17)
        s0 = xor(s0, t)
        t = PI19 + blocksize
        k = s0
        k = sub(k, t)
        k = l_sh(k, 32)
        t = xor(t, k)
        s0 = sub(s0, t)
        s0 = add(s0, spice[i^4])
        t = s1
        t = l_sh(t, 2)
        s0 = xor(s0, t)
        t = s1
        t = r_sh(t, 11)
        s0 = add(s0, t)
        s1 = xor(s1, s0) & lmask
        tt = s0 & 255
        k = kx[tt]
        t = k
        t = l_sh(t, 8)
        s0 = xor(s0, t)
        s1 = sub(s1, k) & lmask

    ct[0] = sub(s0, kx[blocksize])
    ct[1] = sub(s1, kx[blocksize+1]) & lmask

    return output(ct)


class CipherBlockMode():
    def __init__(self):
        self.c = IV

    def update(self):
        self.c = IV

    def cbc_enc(self, p, kx, spice):
        ek = p^self.c
        self.c = encrypt(ek, kx, spice)
        return self.c

    def cbc_dec(self, c, kx, spice):
        p = decrypt(c, kx, spice)
        ek = self.c^p
        self.c = c
        return ek

    def cfb_enc(self, p, kx, spice):
        ek = encrypt(self.c, kx, spice)
        self.c = ek^p
        return self.c

    def cfb_dec(self, c, kx, spice):
        ek = encrypt(self.c, kx, spice)
        self.c = c
        return ek^c

    def ofb_enc_dec(self, text, kx, spice):
        ek = encrypt(self.c, kx, spice)
        self.c = ek
        return ek^text



class EncDecThread(QtCore.QThread):
    update = QtCore.pyqtSignal(int)

    def __init__(self,  parent, file_in, file_out, key, spice, type, mode=None):
        super(EncDecThread, self).__init__(parent)
        self.spice = int_to_arr(spice, 8)
        self.kx = expand_key(key, len(bin(key))-2) # Расширение ключа или создание kx-таблицы
        self.type = type
        self.mode = mode
        self.filename_in = file_in
        self.filename_out = file_out


    def enc_dec(self, file_in, file_out, start, stop, hpc_func, fix_bytes):

        # если выбран неверный ключ, то досвидания
        if(fix_bytes>16):
            self.update.emit(0)
            return

        progress = 0

        for i in range(start,stop):

            bytes = file_in.read(16) # читаем из файла по 16 байт
            uint_form = int.from_bytes(bytes, byteorder='big') # переводим байты в int
            num = hpc_func(uint_form, self.kx, self.spice) # кодируем или декодируем, получаем какое-то целое число

            try:
                if(i!=(stop-1)):
                    bytes= num.to_bytes(16, byteorder='big', signed=False) # переводим это число в байты
                else:
                    bytes = num.to_bytes(fix_bytes, byteorder='big', signed=False) # удалить лишние байты при дешифровке
            except:
                # если в конце шифрования вышел num очень большим, значит был неверно выбран режим шифрования
                self.update.emit(0)
                return

            file_out.write(bytes) # записываем в новый файл

            new_progress = int(100/(stop)*(i+1))

            # посылаем сигнал для прогресс бара
            if(new_progress>progress):
                progress = new_progress
                self.update.emit(progress)

        self.update.emit(100)

    def run(self):
        self.file_in = open(self.filename_in, 'rb') # файл откуда читаем
        self.file_out = open(self.filename_out, 'wb') # файл куда записываем

        self.file_in.seek(0, 2)
        file_length = self.file_in.tell()          # количество байт информации
        length = file_length//16            # количество байт
        self.file_in.seek(0, 0)
        if(self.type=='enc'):
            hpc_encrypt = self.mode[0]

            delbytes = file_length%16 # количество байт, которые необходимо удалить из расшифрованного файла
            num = hpc_encrypt(delbytes, self.kx, self.spice) # шифруем эти байты, получаем какое-то целое число
            bytes = num.to_bytes(16, byteorder='big', signed=False) # переводим целое число в байты
            self.file_out.write(bytes) # записываем в другой файл

            self.enc_dec(self.file_in, self.file_out, 0, length+1, hpc_encrypt, 16)

        else:
            hpc_decrypt = self.mode[1]
            bytes = self.file_in.read(16) # читаем первые 16 байт - информация о том, сколько нужно удалить байтов в конце
            uint_form = int.from_bytes(bytes, byteorder='big')
            delbytes = hpc_decrypt(uint_form, self.kx, self.spice)

            self.enc_dec(self.file_in, self.file_out, 1, length, hpc_decrypt, delbytes)


        self.file_in.close()
        self.file_out.close()
