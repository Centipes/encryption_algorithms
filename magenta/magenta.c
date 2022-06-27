#include <stdio.h>
#include <inttypes.h>
#include <string.h>

#include "magenta.h"

const uint8_t f[] = {
  1u,   2u,   4u,   8u,  16u,  32u,  64u, 128u,
101u, 202u, 241u, 135u, 107u, 214u, 201u, 247u,
139u, 115u, 230u, 169u,  55u, 110u, 220u, 221u,
223u, 219u, 211u, 195u, 227u, 163u,  35u,  70u,
140u, 125u, 250u, 145u,  71u, 142u, 121u, 242u,
129u, 103u, 206u, 249u, 151u,  75u, 150u,  73u,
146u,  65u, 130u,  97u, 194u, 225u, 167u,  43u,
 86u, 172u,  61u, 122u, 244u, 141u, 127u, 254u,
153u,  87u, 174u,  57u, 114u, 228u, 173u,  63u,
126u, 252u, 157u,  95u, 190u,  25u,  50u, 100u,
200u, 245u, 143u, 123u, 246u, 137u, 119u, 238u,
185u,  23u,  46u,  92u, 184u,  21u,  42u,  84u,
168u,  53u, 106u, 212u, 205u, 255u, 155u,  83u,
166u,  41u,  82u, 164u,  45u,  90u, 180u,  13u,
 26u,  52u, 104u, 208u, 197u, 239u, 187u,  19u,
 38u,  76u, 152u,  85u, 170u,  49u,  98u, 196u,
237u, 191u,  27u,  54u, 108u, 216u, 213u, 207u,
251u, 147u,  67u, 134u, 105u, 210u, 193u, 231u,
171u,  51u, 102u, 204u, 253u, 159u,  91u, 182u,
  9u,  18u,  36u,  72u, 144u,  69u, 138u, 113u,
226u, 161u,  39u,  78u, 156u,  93u, 186u,  17u,
 34u,  68u, 136u, 117u, 234u, 177u,   7u,  14u,
 28u,  56u, 112u, 224u, 165u,  47u,  94u, 188u,
 29u,  58u, 116u, 232u, 181u,  15u,  30u,  60u,
120u, 240u, 133u, 111u, 222u, 217u, 215u, 203u,
243u, 131u,  99u, 198u, 233u, 183u,  11u,  22u,
 44u,  88u, 176u,   5u,  10u,  20u,  40u,  80u,
160u,  37u,  74u, 148u,  77u, 154u,  81u, 162u,
 33u,  66u, 132u, 109u, 218u, 209u, 199u, 235u,
179u,   3u,   6u,  12u,  24u,  48u,  96u, 192u,
229u, 175u,  59u, 118u, 236u, 189u,  31u,  62u,
124u, 248u, 149u,  79u, 158u,  89u, 178u,   0u
};


uint8_t A(uint8_t x, uint8_t y){
   return f[x^f[y]];
}

void S(uint8_t *RK, uint8_t *a_out){
    uint8_t shiffle_a[16];
    for (int i=0; i<8; i++){
        shiffle_a[i] = RK[i]^a_out[i*2];
        shiffle_a[i+8] = RK[i+8]^a_out[1+i*2];
      }
    memcpy(a_out, shiffle_a, 16*sizeof(uint8_t));
}


void T(uint8_t *a) {
    int h = 16;
    uint8_t x, y, jh;
    for (int r=0; r<4; r++) {
      for (int i=0; i<16; i+=h){
        jh = h/2;
        for (int j=i; j<(i+jh); j++){
          x = a[j];
          y = a[j + jh];
          a[j] = A(x,y);
          a[j + jh] = A(y,x);
        }

     }
      h/=2;
   }
}


uint64_t C(uint8_t *a){
  uint8_t a_t[16];
  memcpy(a_t, a, 16*sizeof(uint8_t));
  T(a_t);
  for (int i=0; i<2; i++){
      S(a, a_t);
      T(a_t);
  }

  uint64_t x = a_t[0];
  for (int i=2; i<16; i+=2){
    x = ((x<<8)|a_t[i]);
  }

  return x;
}

uint64_t F(uint64_t R, uint64_t K){
    uint8_t a[16];
    for (int i=0; i<8; i++){
      a[7-i] = (R>>(i*8))&255;
      a[15-i] = (K>>(i*8))&255;
    }
    return C(a);

}

void ADDCALL feistel(uint64_t *L_in, uint64_t *R_in, uint64_t *keys, int keys_size){
    uint64_t x;
    for (int i=0; i< keys_size; i++){
        x = F(*R_in, keys[i]);
        x = x^(*L_in);
        *L_in = *R_in;
        *R_in = x;
    }
}
