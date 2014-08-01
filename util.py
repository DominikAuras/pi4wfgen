#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from numpy import concatenate, zeros

def convert_to_wavfile(wf,sample_rate=12000):
  from contextlib import closing
  import wave, StringIO, struct
  from numpy import array
  
  # Annahme: wf in [-1,1], numpy array

  tmp = StringIO.StringIO('')
  with closing(wave.open(tmp,'w')) as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2) # in bytes
    wav.setframerate(sample_rate)
    wav.writeframes((32767 * wf).astype('<i2').tostring())
  
  return tmp.getvalue()