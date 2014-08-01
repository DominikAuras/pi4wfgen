#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

__all__=['pi4mod']

from numpy import sin, pi, repeat, concatenate, mod, cumsum

class pi4mod(object):
  pi4carrier = 800
  pi4tones = [pi4carrier + x * 40 * 12000 / 2048 for x in [-0.5, 0.5, 1.5, 2.5]]
  cwtone = pi4carrier - 250

  def __init__(self, sample_rate = 12000):
    self.sample_rate = sample_rate
    self.samples_per_tone = sample_rate / 6 # 2000

  def tone_phaseinc(self,f):
    return repeat(2. * pi * f / self.sample_rate, self.samples_per_tone)
    
  def phase_encode(self,seq):  
    return mod(cumsum(concatenate([self.tone_phaseinc(pi4mod.pi4tones[sym]) for sym in seq])),2*pi)
    
  def modulate(self,seq):
    return sin(self.phase_encode(seq))