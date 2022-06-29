from PyQt5.QtCore import QThread, pyqtSignal

IV = 278939022647121645315628355772935338798

MASK_64 = (1<<64)-1
MASK_32 = (1<<32)-1
DELTA = 0x9e3779b97f4a7c15

mod = lambda x: x & MASK_64
add  = lambda a,b: mod(a+b)
sub = lambda a,b: mod(a-b)

def exp3 (b, g, n):
    r = b
    if (b == 0):
        return 0
    b = mult(r, b, g, n)
    r = mult(r, b, g, n)
    return r

def mult (a, b, g, n):
    p = 0
    while (b != 0):
        if ((b & 0x01) != 0):
            p ^= a
        a <<= 1
        if (a >= n):
            a ^= g
        b >>= 1
    return p


# ------------------- Создание S-блоков ------------------------------------

S1 = []
S2 = []

S1_SIZE = 0x2000 # размер 8192
S2_SIZE = 0x800 # размер 2048

S1_GEN = 0x2911  # mod
S2_GEN = 0xAA7 # mod

S1_MASK = S1_SIZE - 1
S2_MASK = S2_SIZE - 1

for i in range(S1_SIZE):
    b = i ^ S1_MASK
    S1.append(exp3(b, S1_GEN, S1_SIZE)&255)

for i in range(S2_SIZE):
    b = i ^ S2_MASK
    S2.append(exp3(b, S2_GEN, S2_SIZE)&255)

# -------------------- Создание P-блока -----------------------------------

PR=[]
PL=[]

for i in range(0x100):
    pval = 0
    k = 7
    for j in range(4):
        pval |= ((i >> j) & 0x1) << k;
        k+=8
    PR.append(pval)
    pval = 0
    k = 7
    for j in range(4, 8):
        pval |= ((i >> j) & 0x1) << k;
        k+=8
    PL.append(pval);

# ---------------------------------------------------------------------------

def f(A, B):
    AR = A&MASK_32
    AL = (A>>32)&MASK_32
    BR = B&MASK_32
    BL = (B>>32)&MASK_32

    DL = (AL & ~BR) | (AR & BR)
    DR = (AR & ~BR) | (AL & BR)

    s = S1[(DL>>24 | DR<<8) & 0x1FFF];   EL  = PL[s]>>7;  ER  = PR[s]>>7;
    s = S2[(DL>>16)          &  0x7FF];  EL |= PL[s]>>6;  ER |= PR[s]>>6;
    s = S1[(DL>> 8)          & 0x1FFF];  EL |= PL[s]>>5;  ER |= PR[s]>>5;
    s = S2[ DL               &  0x7FF];  EL |= PL[s]>>4;  ER |= PR[s]>>4;
    s = S2[(DR>>24 | DL<<8) &  0x7FF];   EL |= PL[s]>>3;  ER |= PR[s]>>3;
    s = S1[(DR>>16)          & 0x1FFF];  EL |= PL[s]>>2;  ER |= PR[s]>>2;
    s = S2[(DR>> 8)          &  0x7FF];  EL |= PL[s]>>1;  ER |= PR[s]>>1;
    s = S1[ DR               & 0x1FFF];  EL |= PL[s];     ER |= PR[s];


    FL = S2[(((EL>>24) & 0xFF) | ((BL>>21) &  0x700))] << 24
    FL|= S2[(((EL>>16) & 0xFF) | ((BL>>18) &  0x700))] << 16
    FL|= S1[(((EL>> 8) & 0xFF) | ((BL>>13) & 0x1F00))] <<  8
    FL|= S1[  (EL      & 0xFF) | ((BL>> 8) & 0x1F00) ]

    FR = S2[(((ER>>24) & 0xFF) | ((BL>> 5) &  0x700))] << 24
    FR|= S2[(((ER>>16) & 0xFF) | ((BL>> 2) &  0x700))] << 16
    FR|= S1[(((ER>> 8) & 0xFF) | ((BL<< 3) & 0x1F00))] <<  8
    FR|= S1[((ER & 0xFF) | ((BL<< 8) & 0x1F00))]

    return (FL<<32) | FR

# можно переписать key_init с помощью функции g
# g = lambda k1, k3, k2, deltan: f(add(add(k1,k3),deltan), k2)

def key_init(key):
    size = key.bit_length()
    n = size//64
    K = []
    k4 = key&MASK_64
    k3 = (key>>64)&MASK_64
    if (n <= 2):
        k2 = f(k3, k4)
        k1 = f(k4, k3)
    else:
        k2 = (key>>128)&MASK_64
        if(n <= 3):
            k1 = f(k4, k3)
        else:
            k1 = (key>>192)&MASK_64

    # ------- Промежуточные ключи ------------
    SK = []
    deltan = DELTA
    for i in range(0, 48):
        t1 = add(k1, k3)
        t2 = add(t1, deltan)
        f_out = f(t2, k2)
        SK.append(k4 ^ f_out)
        k4 = k3
        k3 = k2
        k2 = k1
        k1 = SK[i]
        deltan = add(deltan,DELTA)

    return SK


def encrypt(input, SK):
    R = input&MASK_64
    L = (input>>64)&MASK_64
    # SK = key_init(key)
    k = 0
    for i in range(16):
        Rn = add(R,SK[k])
        f_out = f(Rn, SK[k+1])
        Rn = add(Rn, SK[k+2])
        R = L ^ f_out
        L = Rn
        k+=3

    return (R<<64) | L

def decrypt(input, SK):
    R = input&MASK_64
    L = (input>>64)&MASK_64
    # SK = key_init(key)
    k = len(SK)-1
    for i in range(16):
        Rn = sub(R, SK[k])
        f_out = f(Rn, SK[k-1])
        Rn = sub(Rn, SK[k-2])
        R = L ^ f_out
        L = Rn
        k-=3

    return (R<<64) | L


class CipherBlockMode():
    def __init__(self):
        self.c = IV
        self.cipher_block_mode_dir = {
            "ECB": (encrypt, decrypt),
            "CBC": (self.cbc_enc, self.cbc_dec),
            "CFB": (self.cfb_enc, self.cfb_dec),
            "OFB" : (self.ofb_enc_dec, self.ofb_enc_dec)}

    def update(self):
        self.c = IV

    def cbc_enc(self, p, k):
        ek = p^self.c
        self.c = encrypt(ek, k)
        return self.c

    def cbc_dec(self, c, k):
        p = decrypt(c, k)
        ek = self.c^p
        self.c = c
        return ek

    def cfb_enc(self, p, k):
        ek = encrypt(self.c, k)
        self.c = ek^p
        return self.c

    def cfb_dec(self, c, k):
        ek = encrypt(self.c, k)
        self.c = c
        return ek^c

    def ofb_enc_dec(self, text, k):
        ek = encrypt(self.c, k)
        self.c = ek
        return ek^text

CBM = CipherBlockMode()

class CryptoThread(QThread):
    update = pyqtSignal(int)

    def __init__(self, key, type, file_in, file_out = 'out', mode='ECB', parent = None):
        super(CryptoThread, self).__init__(parent)

        if(isinstance(key, str)):
            key = key.encode("utf-8")
            key = int.from_bytes(key, byteorder='big')

        self.SK = key_init(key)

        assert type == 'enc' or type == 'dec', "the type of operation must be 'enc' or 'dec'"
        self.type = type

        self.filename_in = file_in
        self.filename_out = file_out

        self.mode = CBM.cipher_block_mode_dir[mode]

    def enc_dec(self, f_in, f_out, s, e, loki97_func, fix_bytes):

        if(fix_bytes>16):
            self.update.emit(0)
            return

        progress = 0

        for i in range(s, e):

            bytes = f_in.read(16)                                                  # читаем из файла по 16 байт
            uint_form = int.from_bytes(bytes, byteorder='big')                     # переводим байты в int
            num = loki97_func(uint_form, self.SK)                                  # кодируем или декодируем, получаем какое-то целое число

            try:
                if(i!=(e-1)):
                    bytes= num.to_bytes(16, byteorder='big', signed=False)         # переводим это число в байты
                else:
                    bytes = num.to_bytes(fix_bytes, byteorder='big', signed=False) # удалить лишние байты при дешифровке
            except:                          # если в конце шифрования вышел num очень большим, значит был неверно выбран режим шифрования
                self.update.emit(0)
                return

            f_out.write(bytes)               # записываем в новый файл

            new_progress = int(100/(e)*(i+1))

            if(new_progress>progress):       # посылаем сигнал для прогресс бара
                progress = new_progress
                self.update.emit(progress)

        self.update.emit(100)

    def run(self):
        CBM.update()           # обновить вектор инициализации
        file_in = open(self.filename_in, 'rb')
        file_out = open(self.filename_out, 'wb')

        file_in.seek(0, 2)
        file_len = file_in.tell()
        length = file_len//16       # количество байт информации
        file_in.seek(0, 0)

        if(self.type=='enc'):
            loki97_encrypt = self.mode[0]

            delbytes = (file_len)%16                 # количество байт, которые необходимо удалить из расшифрованного файла
            num = loki97_encrypt(delbytes, self.SK)  # шифруем эти байты, получаем какое-то целое число
            bytes = num.to_bytes(16, byteorder='big', signed=False) # переводим целое число в байты
            file_out.write(bytes)                    # записываем в другой файл

            self.enc_dec(file_in, file_out, 0, length+1, loki97_encrypt, 16)

        else:
            loki97_decrypt = self.mode[1]
            bytes = file_in.read(16)    # читаем первые 16 байт - информация о том, сколько нужно удалить байтов в конце
            num = int.from_bytes(bytes, byteorder='big')
            delbytes = loki97_decrypt(num, self.SK)
            self.enc_dec(file_in, file_out, 1, length, loki97_decrypt, delbytes)


        file_in.close()
        file_out.close()
