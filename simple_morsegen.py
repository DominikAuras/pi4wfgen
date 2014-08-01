#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

__all__=['simple_morsegen']

from numpy import sin, pi, concatenate, mod, cumsum, repeat

MORSE_TABLE = {'A': ".-",
               'B': "-...",
               'C': "-.-.",
               'D': "-..",
               'E': ".",
               'F': "..-.",
               'G': "--.",
               'H': "....",
               'I': "..",
               'J': ".---",
               'K': "-.-",
               'L': ".-..",
               'M': "--",
               'N': "-.",
               'O': "---",
               'P': ".--.",
               'Q': "--.-",
               'R': ".-.",
               'S': "...",
               'T': "-",
               'U': "..-",
               'V': "...-",
               'W': ".--",
               'X': "-..-",
               'Y': "-.--",
               'Z': "--..",
               '0': "-----",
               '1': ".----",
               '2': "..---",
               '3': "...--",
               '4': "....-",
               '5': ".....",
               '6': "-....",
               '7': "--...",
               '8': "---..",
               '9': "----.",
               '.': ".-.-.-",
               ',': "--..--",
               '?': "..--..",
               '-': "-....-",
               '/': "-..-.",
               '"': ".-..-.",
               '@': ".--.-."
               }
               
class simple_morsegen(object):
  def __init__(self, sample_rate = 12000., f_cr = 800., f_cw = 800-250, CPM = 60, WPM = 12, refword = "PARIS"):

    ## all measured in seconds
    # based on PARIS, 
    len_dit = 6. / CPM
    len_dah = 3 * len_dit
    
    refword = refword.upper()
    len_refword_dits = len_dit * (WPM * ('' +      ''.join(['.'.join(MORSE_TABLE[c]) for c in refword])).replace('-','...').count('.'))
    #                                    ^ no IWS  ^ no ICS  ^ IES
    len_spacing_unit = (60. - len_refword_dits) / (WPM * ('.'*7 + '...'.join(list(refword))).count('.'))
    #                                                     ^ IWS   ^ ICS      ^ no IES ^ no dits/dahs

    len_ies = len_dit                # inter-element spacing
    len_ics = len_spacing_unit * 3   # inter-character spacing
    len_iws = len_spacing_unit * 7   # inter-word spacing

    self.ctbl = { 
            '.' : (f_cw, len_dit),
            '-' : (f_cw, len_dah),
            '#' : (f_cr, len_ies),
            '=' : (f_cr, len_ics),
            '_' : (f_cr, len_iws)
          }
      

    self.sample_rate = sample_rate

  def _tone_phaseinc(self,f,duration):
    samples_per_tone = int(duration * self.sample_rate)
    #rem = duration * self.sample_rate - samples_per_tone
    return repeat(2. * pi * f / self.sample_rate, samples_per_tone)
    
  def _phase_encode(self,seq):
    return mod(cumsum(concatenate([self._tone_phaseinc(f,d) for f,d in seq])), 2*pi)
    
  def _encode(self,msg):
    morsecode = "_".join(['='.join(map(lambda c : '#'.join(MORSE_TABLE[c]),w)) for w in msg.upper().split()])
    return map(lambda x : self.ctbl[x], morsecode)
    
  def phase_encode(self,msg):
    return self._phase_encode(self._encode(msg))
    
  def modulate(self,msg):
    return sin(self.phase_encode(msg))
  
  
if __name__=='__main__':
  from argparse import ArgumentParser
  parser = ArgumentParser()
  parser.add_argument('msg')
  parser.add_argument('-o','--output',default='morse.wav') 
  args = parser.parse_args()

  from util import convert_to_wavfile
  phaseseq = simple_morsegen().phase_encode(args.msg)
  wf = convert_to_wavfile(sin(phaseseq))
  with open(args.output,'wb') as f:
    f.write(wf)
  
