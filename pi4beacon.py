#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from numpy import zeros, sin, concatenate,pi, arange

from pi4encode import *
from pi4mod import *
from simple_morsegen import *

class PI4Beacon(object):
  def __init__(self,sample_rate=12000.):
    self.sample_rate = sample_rate
    
  def pi4_only(self,pi4msg):    
    return pi4mod(sample_rate=self.sample_rate).modulate(pi4_encode(pi4msg))
  
  def pi4_cw_carrier(self,pi4msg,cwmsg):
    wf = self.pi4_only(pi4msg)
    
    cw_wf = simple_morsegen(sample_rate=self.sample_rate).modulate(cwmsg)
    # Start CW at 25s, append 0.5s pause
    pause_till_25s = zeros(int(25. * self.sample_rate) - len(wf))
    pause_0_5s = zeros(int(.5 * self.sample_rate))
    wf = concatenate([wf, pause_till_25s, cw_wf, pause_0_5s])

    # Carrier till 59.5s, append 0.5s pause
    samples = int(59.5 * self.sample_rate) - len(wf)
    if samples > 0:
      carrier_till_59_5s = sin(2. * pi * pi4mod.pi4carrier / self.sample_rate * arange(samples))
      wf = concatenate([wf, carrier_till_59_5s, pause_0_5s])
    
    return wf
    
  def pi4_cw_carrier_with_5s_prologue(self,pi4msg,cwmsg):
    wf = self.pi4_cw_carrier(pi4msg,cwmsg)
    # prepend 4.5s carrier, and 0.5s pause
    pause_0_5s = zeros(int(.5 * self.sample_rate))
    carrier_4_5s = sin(2. * pi * pi4mod.pi4carrier / self.sample_rate * arange(int(4.5 * self.sample_rate)))
    return concatenate([carrier_4_5s, pause_0_5s, wf])
    