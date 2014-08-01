#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
This is a straight-forward re-implementation of the C source code for PI4 found on
[http://rudius.net/oz2m/ngnb/pi4.htm]. Especially the convolutional encoding is
not really 'pythonic'.
"""

from itertools import chain, repeat, islice, izip

#################################################################
## The source encoder
#################################################################
chr_tbl = dict([(c,idx) for idx,c in enumerate("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ /")])

def _pi4_chr_map(x):
  ix = "{0: <8}".format(x[:8]) # pad with spaces, truncate
  return map(lambda c : chr_tbl[c], ix.upper())
  
def pi4_src_encode(x):
  # 64bit integer, MSB first, i.e. char0 * 38 * 7 + char1 * 38 * 6 ... + char7 * 38 * 0
  return sum([38L ** idx * long(c) for idx, c in enumerate(reversed(_pi4_chr_map(x)))])
  
def pi4_is_valid_msg(x):
  try:
    pi4_src_encode(x)
    return True
  except:
    return False
#################################################################


#################################################################
## The convolutional encoder
#################################################################
def _even_parity(v):
  return sum([(v >> i) & 1 for i in xrange(32)]) % 2
  
def pi4_conv_enc(x):
  Poly1 = 0xF2D05351L
  Poly2 = 0xE4613C47L
  N = 0L
  cx = []
  for j in xrange(73):
    N <<= 1
    if (x & 0x20000000000L) != 0: N |= 1
    x <<= 1
    cx += [_even_parity(N & Poly1), _even_parity(N & Poly2)]
  return cx
#################################################################
  

#################################################################
## The interleaver
#################################################################
def _int_to_bits(x,l):
  return [(x >> bi0) & 1 for bi0 in xrange(8)]
  
def _bits_to_int(x):
  return sum([b << bi for bi,b in enumerate(x)])

def _pi4_permidx():
  for i in xrange(256):
    r = _bits_to_int(reversed(_int_to_bits(i,8)))
    if r < 146: yield r
    
pi4_intl_tbl = list(islice(_pi4_permidx(),146))

def pi4_interleave(x):
  intl = [0]*146
  for i,pi in enumerate(pi4_intl_tbl):
    intl[pi] = x[i]
  return intl
#################################################################
    
    
#################################################################
## Bits to Tones Mapper
#################################################################
pi4_syncvec = [0,0,1,0,0,1,1,1,1,0,1,0,1,0,1,0,0,1,0,0,0,1,0,0,0,1,1,0,0,1,
               1,1,1,0,0,1,1,1,1,1,0,0,1,1,0,1,1,1,1,0,1,0,1,1,0,1,1,0,1,0,
               0,0,0,0,1,1,1,1,1,0,1,0,1,0,0,0,0,0,1,1,1,1,1,0,1,0,0,1,0,0,
               1,0,1,0,0,0,0,1,0,0,1,1,0,0,0,0,0,1,1,0,0,0,0,1,1,0,0,1,1,1,
               0,1,1,1,0,1,1,0,1,0,1,0,1,0,0,0,0,1,1,1,0,0,0,0,1,1]
               
def pi4_to_fsk(x):
  return [int(pi4_syncvec[i] + 2 * x[i]) for i in xrange(len(x))]
#################################################################


#################################################################
## The complete encoder
#################################################################
def pi4_encode(msg):
  """ Returns a sequence of tone indices, i.e. each sequence element is 0,1,2 or 3, representing one of the four tones. """
  src_enc = pi4_src_encode(msg)
  convenc = pi4_conv_enc(src_enc)
  intl = pi4_interleave(convenc)
  pi4fsk = pi4_to_fsk(intl)
  return pi4fsk
#################################################################
  
  
#################################################################
# Some debug utils
#################################################################
def pi4_group4syms(x):
  return [sum([b*(4**i) for i, b in enumerate(reversed(xl))]) for xl in izip(*[chain(iter(x), repeat(0,3))]*4)]
  
def pi4_pformat(x):  
  print("\n".join([" ".join(map(str,x[40*i:40*(i+1)])) for i in xrange(3)] + [" ".join(map(str,x[120:]))]))
#################################################################
  

if __name__=='__main__':
  pi4_pformat(pi4_encode("DB0LTG"))
  
  




"""
The original C code:


uint8_t Parity(uint32_t Value)
{
  uint8_t Even=0;
  uint8_t BitNo;

  for (BitNo=0;BitNo<=31;BitNo++)
    if (((Value >> BitNo) & 0x01) != 0)
      Even=1-Even;

  return Even;
}

uint8_t GetCharNo(const char *ValidChars, const char Ch)
{
  const char *ptrCh;

  ptrCh=strchr(ValidChars, Ch);
  if (ptrCh==NULL)
    return(strchr(ValidChars, ' ')-ValidChars);
  else
    return(ptrCh-ValidChars);
}

void PI4MakeSymbols(char *Msg)         // Msg = the callsign/message with relevant padding
{
  #define PI4MaxInfoLength 8
  static const char PI4Chars[]="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ /";
  static const uint8_t PI4Vector[]={0,0,1,0,0,1,1,1,1,0,1,0,1,0,1,0,0,1,0,0,0,1,0,0,0,1,1,0,0,1,
                                    1,1,1,0,0,1,1,1,1,1,0,0,1,1,0,1,1,1,1,0,1,0,1,1,0,1,1,0,1,0,
                                    0,0,0,0,1,1,1,1,1,0,1,0,1,0,0,0,0,0,1,1,1,1,1,0,1,0,0,1,0,0,
                                    1,0,1,0,0,0,0,1,0,0,1,1,0,0,0,0,0,1,1,0,0,0,0,1,1,0,0,1,1,1,
                                    0,1,1,1,0,1,1,0,1,0,1,0,1,0,0,0,0,1,1,1,0,0,0,0,1,1};

  uint8_t BitNo;
  int16_t I,J;

  // Source encoding
  uint64_t SourceEnc=0;

  for (I=0;I<PI4MaxInfoLength;I++)
    SourceEnc=SourceEnc*38+(uint64_t) GetCharNo(PI4Chars,Msg[I]);

  // Convolutional encoding
  const uint32_t Poly1=0xF2D05351;
  const uint32_t Poly2=0xE4613C47;
  uint32_t N=0;
  uint8_t ConvEnc[146]={0};

  I=0;
  for (J=0;J<73;J++)
  {
    N <<= 1;
    if ((SourceEnc & 0x20000000000LL) != 0)
      N |= 1;
    SourceEnc <<= 1;

    ConvEnc[I++]=Parity(N & Poly1);
    ConvEnc[I++]=Parity(N & Poly2);
  }

  // Interleaving
  uint8_t P=0;
  uint8_t R=0;
  uint8_t Interleaved[146]={0};

  for (I=0;I<=255;I++)
  {
    for (BitNo=0;BitNo<=7;BitNo++)
    {
      if (((I >> BitNo) & 0x01)==0x01)
        R |= 1 << (7-BitNo);
      else
        R &= ~(1 << (7-BitNo));
    }

    if ((P<146) && (R<146))
      Interleaved[R]=ConvEnc[P++];
  }

  // Merge with vector
  uint8_t Symbols[146]={0};
  
  for (I=0;I<146;I++)
    Symbols[I]=PI4Vector[I] | (Interleaved[I] << 1);
}

"""