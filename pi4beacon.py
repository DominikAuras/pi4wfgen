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
  
  def pi4_cw(self,pi4msg,cwmsg):
    wf = self.pi4_only(pi4msg)
    
    cw_wf = simple_morsegen(sample_rate=self.sample_rate).modulate(cwmsg)
    # Start CW at 25s
    pause_till_25s = zeros(int(25. * self.sample_rate) - len(wf))
    return concatenate([wf, pause_till_25s, cw_wf])
  
  def pi4_cw_carrier(self,pi4msg,cwmsg):
    wf = self.pi4_cw(pi4msg,cwmsg)
    
    # append 0.5s pause
    pause_0_5s = zeros(int(.5 * self.sample_rate))
    wf = concatenate([wf, pause_0_5s])

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
    
    
if __name__ == '__main__':
  from argparse import ArgumentParser
  from util import convert_to_wavfile
  
  modes = ['pi4', 'pi4-cw', 'pi4-cw-carrier', 'prologue-pi4-cw-carrier']
  
  parser = ArgumentParser(description='Generate PI4 waveforms.')
  parser.add_argument('pi4msg', metavar="PI4MSG", help="The PI4 message. Maximum length: 8 characters.")
  parser.add_argument('-c','--cwmsg', help="The CW message.")
  parser.add_argument('-m','--mode',default='pi4',metavar='MODE',choices=modes,
                      help="Possible modes: " + ", ".join(modes) + ", default pi4")
  parser.add_argument('-s','--sample-rate', type=int, default=12000,
                      help="Sample rate, default 12000 samples per second")
  parser.add_argument('-o','--output',default='pi4wave.wav',
                      help="Output filename, default pi4wave.wav")
                      
  args = parser.parse_args()
  if 'cw' in args.mode and args.cwmsg is None:
    parser.print_help()
    print("CW message required for this mode")
    raise SystemExit
  
  beacon = PI4Beacon(sample_rate=args.sample_rate)
  if args.mode == 'pi4':
    wf = beacon.pi4_only(args.pi4msg)
  elif args.mode == 'pi4-cw':
    wf = beacon.pi4_cw(args.pi4msg,args.cwmsg)
  elif args.mode == 'pi4-cw-carrier':
    wf = beacon.pi4_cw_carrier(args.pi4msg,args.cwmsg)
  elif args.mode == 'prologue-pi4-cw-carrier':
    wf = beacon.pi4_cw_carrier_with_5s_prologue(args.pi4msg,args.cwmsg)
  else:
    raise RuntimeError
  
  with open(args.output,'wb') as f:
    f.write(convert_to_wavfile(wf))
    