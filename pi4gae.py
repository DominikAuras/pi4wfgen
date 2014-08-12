#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import webapp2, jinja2, os, urllib

from util import convert_to_wavfile

from pi4encode import *
from pi4beacon import *


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
    
    
def errormsg(msg):              
  template = JINJA_ENVIRONMENT.get_template('templates/error.html')
  return template.render(dict(error_message=msg))
    
    
class WaveFileDownload(webapp2.RequestHandler):
  """ Generate wave file for download. """
  def get(self):
    try:
      msg = self.request.get('pi4Message')
      cwmsg = self.request.get('cwmsg')
      mode = self.request.get_range('mode',min_value=1,max_value=4,default=1)
      
      if not pi4_is_valid_msg(msg):
        self.response.write(errormsg("Invalid PI4 input: \"" + msg + "\""))
        return
      
      
      # mode 1: 5s Carrier + PI4 + CW + Carrier
      # mode 2: PI4 + CW + Carrier
      # mode 3: PI4
      if mode == 1:
        wf = PI4Beacon().pi4_cw_carrier_with_5s_prologue(msg,cwmsg)
      elif mode == 2:
        wf = PI4Beacon().pi4_cw_carrier(msg,cwmsg)
      elif mode == 3:
        wf = PI4Beacon().pi4_cw(msg,cwmsg)
      elif mode == 4:
        wf = PI4Beacon().pi4_only(msg)
      
      fname = "pi4wave"
      
      self.response.headers['Content-Type'] = 'audio/vnd.wave'      
      self.response.headers['Content-Disposition'] = 'attachment; filename=' + str(fname).replace(' ','_') + '.wav'
      self.response.write(convert_to_wavfile(wf))
    except (TypeError, ValueError):
      self.response.write("<html><body><p>Invalid inputs</p></body></html>")
   

class MainPage(webapp2.RequestHandler):
  def get(self):
    template = JINJA_ENVIRONMENT.get_template('templates/vorlage.html')
    self.response.write(template.render())
    
  def post(self):
    """ PI4 Encode, display steps. """
    msg = self.request.get('pi4Message','')
    cwmsg = self.request.get('cwmsg','')
    
    if not pi4_is_valid_msg(msg):
      self.response.write(errormsg("Invalid PI4 input: \"" + msg + "\""))
      return
    
    src_enc = pi4_src_encode(msg)
    convenc = pi4_conv_enc(src_enc)
    intl = pi4_interleave(convenc)
    pi4fsk = pi4_to_fsk(intl)
    pi4bytes = pi4_group4syms(pi4fsk)
    
    tpl = dict(
                pi4Message = msg,
                cwmsg = cwmsg,
                pi4Message_url = urllib.quote(msg.encode('utf8')),
                cwmsg_url = urllib.quote(cwmsg.encode('utf8')),
                EightCharMsg = "{0: <8}".format(msg[:8]),
                SourceEncoding = str(src_enc),
                ConvEnc = convenc,
                Intl = intl,
                Symbols = pi4fsk,
                SymBytes = pi4bytes,
                tones = pi4mod.pi4tones,
                carrier = pi4mod.pi4carrier,
                cwtone = pi4mod.cwtone,
              )
              
    template = JINJA_ENVIRONMENT.get_template('templates/vorlage.html')
    self.response.write(template.render(tpl))
    
    
    
application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/gen', MainPage),
    ('/wav', WaveFileDownload),
], debug=True)
  