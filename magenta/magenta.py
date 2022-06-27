import hashlib
import time
from PyQt5 import QtCore
from ctypes import *
from ctypes.util import find_library

libmagenta = CDLL("./magenta.dll")
c_feistel = libmagenta.feistel
c_feistel.restype = c_uint64

KDF_KEY_SALT = 203
KDF_IV_SALT = 250
KDF_ITER_COUNT = 120000

MASK_128 = (1<<128)-1
MASK_64 = (1<<64) - 1
V = lambda x: ((x<<64) & MASK_128)|(x>>64)

def round_keys(n, key) -> tuple:
    k1 = key & MASK_64
    k2 = (key>>64) & MASK_64

    if(n == 128):
        return (k1, k1, k2, k2, k1, k1)

    k3 = (key>>128) & MASK_64
    if(n == 192):
        return (k1, k2, k3, k3, k2, k1)

    k4 = (key>>192) & MASK_64
    return (k1, k2, k3, k4, k4, k3, k2, k1)


def feistel_network(X, keys) -> int:
    R = c_uint64(X&MASK_64)
    Rp = pointer(R)

    L = c_uint64((X>>64)&MASK_64)
    Lp = pointer(L)

    segment_key = c_uint64 * len(keys)
    arr_keys = segment_key(*keys)
    c_feistel(Lp, Rp, arr_keys, len(keys))

    return (L.value << 64)|R.value

def derive_key(password, salt, bytes=16):
    password = password.encode()
    salt = salt.to_bytes(16, byteorder='big', signed=False)
    keys = hashlib.pbkdf2_hmac('sha512', password, salt, KDF_ITER_COUNT, bytes)
    return int(keys.hex(), 16)

class ICipherBlockModes():

    def __init__(self, password):
        self.c = derive_key(password, KDF_IV_SALT)

    def cbm_enc(self, *args):
        pass
    def cbm_dec(self, *args):
        pass

class CBC(ICipherBlockModes):

    def cbm_enc(self, p, roundk):
        ek = p^self.c
        self.c = feistel_network(ek, roundk)
        return self.c

    def cbm_dec(self, c, roundk):
        p = V(feistel_network(V(c), roundk))
        ek = self.c^p
        self.c = c
        return ek

class CFB(ICipherBlockModes):

    def cbm_enc(self, p, roundk):
        ek = feistel_network(self.c, roundk)
        self.c = ek^p
        return self.c

    def cbm_dec(self, c, roundk):
        ek = feistel_network(self.c, roundk)
        self.c = c
        return ek^c

class OFB(ICipherBlockModes):

    def cbm(self, text, roundk):
        ek = feistel_network(self.c, roundk)
        self.c = ek
        return ek^text

    cbm_enc = lambda self, p, roundk: self.cbm(p, roundk)
    cbm_dec = lambda self, c, roundk: self.cbm(c, roundk)


class CTR(ICipherBlockModes):

    def cbm(self, text, roundk):
        ek = feistel_network(self.c, roundk)
        self.c+=1
        return ek^text

    cbm_enc = lambda self, p, roundk: self.cbm(p, roundk)
    cbm_dec = lambda self, c, roundk: self.cbm(c, roundk)


def cipher_block_mode(magenta_func):
    def wrapper(self, text, roundk):
        if(not self.block_mode):
            return magenta_func(self, text, roundk)

        if(self.suffix=="enc"):
            return self.block_mode.cbm_enc(text, roundk)

        return self.block_mode.cbm_dec(text, roundk)

    return wrapper

CBM = {'ECB': lambda p: None, 'CBC': lambda p: CBC(p), 'CFB': lambda p: CFB(p), 'OFB': lambda p: OFB(p), 'CTR': lambda p: CTR(p)}

class CryptoThread(QtCore.QThread):
    update = QtCore.pyqtSignal(tuple)

    def __init__(self, bits, key, type, file_in, file_out='out', mode='ECB', parent=None):
        super(CryptoThread, self).__init__(parent)

        self.fname_from = file_in
        self.fname_to = file_out

        assert bits == 128 or bits == 192 or bits == 256, 'the key size must be 128, 192 or 256 bits'
        self.bits = bits
        self.key = derive_key(key, KDF_KEY_SALT, self.bits//8)

        assert type == 'enc' or type == 'dec', "the type of operation must be 'enc' or 'dec'"
        self.suffix = type
        self.block_mode = CBM[mode](key)

        self.running = True
        self.byte = 16

    @cipher_block_mode
    def magenta_enc(self, p, roundk):
        return feistel_network(p, roundk)

    @cipher_block_mode
    def magenta_dec(self, p, roundk):
        return V(feistel_network(V(p), roundk))

    def stop(self):
        self.running = False

    def enc_dec(self, roundk, file_from, file_to, magenta_func, num, lenb, delbytes=16):

        if(delbytes>16):
            self.update.emit((0, 0))
            return False

        progress = 0
        progress_bytes = (1-num)*delbytes

        for i in range(num,lenb):
            if(not self.running):
                return False

            bytes = file_from.read(self.byte)

            uint_form = int.from_bytes(bytes, byteorder='big')
            ed = magenta_func(uint_form, roundk)

            if(i==(lenb-1)):
                self.byte = delbytes
            try:
                bytes = ed.to_bytes(self.byte, byteorder='big', signed=False) # удалить лишние байты
            except:
                self.update.emit((progress, 0)) ## (int(100/(lenb+1)*(i-1))
                return False

            file_to.write(bytes) # запись

            real_progress = int(100/(lenb)*(i+1))
            progress_bytes += self.byte

            if(real_progress>progress):
                progress = real_progress
                self.update.emit((progress, progress_bytes))
                progress_bytes = 0

        return True

    def run(self):

        file_from = open(self.fname_from, 'rb') # открытый текст
        file_to = open(self.fname_to, 'wb') # новый файл

        start = time.time()
        self.time = 0

        file_from.seek(0, 2)
        length = file_from.tell()
        lenb = length//self.byte

        roundk = round_keys(self.bits, self.key)
        file_from.seek(0, 0)

        if(self.suffix == "enc"):
            delbytes = (length)%self.byte
            enc_delbytes = self.magenta_enc(delbytes, roundk)
            bytes = enc_delbytes.to_bytes(self.byte, byteorder='big', signed=False)
            file_to.write(bytes)

            self.retval = self.enc_dec(roundk, file_from, file_to, self.magenta_enc, 0, lenb+1, 16)
        else:
            bytes = file_from.read(self.byte)
            uint_form = int.from_bytes(bytes, byteorder='big')
            delbytes = self.magenta_dec(uint_form, roundk)

            self.retval = self.enc_dec(roundk, file_from, file_to, self.magenta_dec, 1, lenb, delbytes)

        self.time = time.time()-start

        file_from.close()
        file_to.close()
