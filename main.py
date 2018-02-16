#!/usr/bin/env python

import sys
import os
import optparse
import logging
import random
import time
import subprocess
import io
import signal 
import re

keymap = {"a":"", "z":"", "e":"", "r":"", "t":"", "y":"", "u":"", "i":"", "o":"", "p":"", "q":"", "s":"", "d":"", "f":"", "g":"", "h":"", "j":"", "k":"", "l":"", "m":"", "w":"", "x":"", "c":"", "v":"", "b":"", "n":"", "Ctrl":"", "Alt":"", "F4":"", "Tab":""}
azerty = ["a", "z", "e", "r", "t", "y", "u", "i", "o", "p", "q", "s", "d", "f", "g", "h", "j", "k", "l", "m", "w", "x", "c", "v", "b", "n", "Ctrl", "Alt", "F4", "Tab"]

cneeProcess = {}


def signalHandler(signum, frame):
    print 'Signal handler called with signal', signum
    cneeProcess.terminate() 
    raise IOError("")


def recordKeymap():
  
  # Ask the user to stop typing and then read all lines from the pipe created
  print 'Beginning to record your keymap. Please stop typing for a couple of seconds then press Enter when you\'re ready to begin.'  
  
  # Wait a bit before spawning Cnee
  time.sleep(0.5)
  cneeProcess = subprocess.Popen(["cnee", "--record", "--keyboard", "--err-file", "/dev/null"], stdout=subprocess.PIPE)
  
  # Wait for input
  raw_input() 
  
  # Go through the output until we reach some lines corresponding to keys pressed
  line = ""
  while re.match(r"[0-9]+,[0-9]+,[0-9]+,[0-9]+,[0-9]+,[0-9]+,", line) == None:
    line = cneeProcess.stdout.readline()
  
  # The first line corresponding to a key should be Enter
  matches   = re.match(r"[0-9]+,[0-9]+,[0-9]+,[0-9]+,[0-9]+,([0-9]+),", line)
  keyEnter  = matches.group(1)

  # Iterate through the keys we want to catch
  for key in azerty :
    print "Please press {} then press Enter".format(key)
    raw_input() 
    time.sleep(0.1)
    
    # Once the user has hit the key, read the lines that have been written by cnee during the operation
    
    line  = cneeProcess.stdout.readline() 
    match = keyEnter 

    while match == keyEnter:
      matches = re.match(r"[0-9]+,[0-9]+,[0-9]+,[0-9]+,[0-9]+,([0-9]+),", line)
      match   = matches.group(1)

    keymap[key] = matches.group(1) 

    # Read the following lines to set the cursor at the end of the stream
    cneeProcess.stdout.readline()
    cneeProcess.stdout.readline()
    cneeProcess.stdout.readline()
    cneeProcess.stdout.readline()
    cneeProcess.stdout.readline()
    cneeProcess.stdout.readline()
    cneeProcess.stdout.readline()

  return 1 
# end recordKeymap



def parser(unparsed_args):
  parser = optparse.OptionParser(
    usage = "%prog [options]",
    description = "Transmit image over the air to the esp8266 module with OTA support."
  )

  # destination ip and port
  group = optparse.OptionGroup(parser, "Destination")
  group.add_option("-i", "--ip",
    dest = "esp_ip",
    action = "store",
    help = "ESP8266 IP Address.",
    default = False
  )
  group.add_option("-I", "--host_ip",
    dest = "host_ip",
    action = "store",
    help = "Host IP Address.",
    default = "0.0.0.0"
  )
  group.add_option("-p", "--port",
    dest = "esp_port",
    type = "int",
    help = "ESP8266 ota Port. Default 8266",
    default = 8266
  )
  group.add_option("-P", "--host_port",
    dest = "host_port",
    type = "int",
    help = "Host server ota Port. Default random 10000-60000",
    default = random.randint(10000,60000)
  )
  parser.add_option_group(group)

  # auth
  group = optparse.OptionGroup(parser, "Authentication")
  group.add_option("-a", "--auth",
    dest = "auth",
    help = "Set authentication password.",
    action = "store",
    default = ""
  )
  parser.add_option_group(group)

  # image
  group = optparse.OptionGroup(parser, "Image")
  group.add_option("-f", "--file",
    dest = "image",
    help = "Image file.",
    metavar="FILE",
    default = None
  )
  group.add_option("-s", "--spiffs",
    dest = "spiffs",
    action = "store_true",
    help = "Use this option to transmit a SPIFFS image and do not flash the module.",
    default = False
  )
  parser.add_option_group(group)

  # output group
  group = optparse.OptionGroup(parser, "Output")
  group.add_option("-d", "--debug",
    dest = "debug",
    help = "Show debug output. And override loglevel with debug.",
    action = "store_true",
    default = False
  )
  group.add_option("-r", "--progress",
    dest = "progress",
    help = "Show progress output. Does not work for ArduinoIDE",
    action = "store_true",
    default = False
  )
  parser.add_option_group(group)

  (options, args) = parser.parse_args(unparsed_args)

  return options
# end parser


def main(args):
  options = parser(args)
  loglevel = logging.WARNING
  if (options.debug):
    loglevel = logging.DEBUG

  signal.signal(signal.SIGALRM, signalHandler)
  signal.signal(signal.SIGINT, signalHandler)
  signal.signal(signal.SIGTERM, signalHandler)


  #logging.basicConfig(level = loglevel, format = '%(asctime)-8s [%(levelname)s]: %(message)s', datefmt = '%H:%M:%S')
  #logging.debug("Options: %s", str(options))
  #logging.critical("Not enough arguments.")


  return recordKeymap()


if __name__ == '__main__':
  sys.exit(main(sys.argv))
