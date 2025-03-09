import os
import sys
import re

def read_until(data,index,pattern):
  original_index=index
  while index<len(data) and not data[index:].startswith(pattern):
    index+=1
  return index,data[original_index:index]

def systemhook(args):
  raise ValueError("Invalid system hook")

def parse(title,args=[]):
  try: file=open(os.path.join(build_directory,title)).read()
  except FileNotFoundError: raise ValueError("Invalid title")
  parsed=""
  index=0
  route=None
  while True:
    if file[index:index+3]=="(((":
      index,data=read_until(file,index+3,")))")
      splitted=data.split(";")
      command=splitted[0]
      newargs=splitted[1:]
      if command=="system":
        parsed+=systemhook(newargs)
      elif command=="route":
        if len(newargs)!=1: raise ValueError("Route takes exactly one argument")
        route=newargs[0]
      else:
        parsed+=parse(command,args)[0]
    else:
      parsed+=file[index]
      index+=1
  return parsed,route

if __name__=="__main__":
  build_directory=sys.argv[1]
  if not os.path.isdir(build_directory):
    print("Argument 1 is not a valid directory")
    exit()
  os.mkdir("output")
  for file in os.listdir(build_directory):
    parsed=parse(file)
    if parsed[1] is not None:
      os.makedirs(os.path.join("output",os.path.dirname(parsed[1])))
      open(os.path.join("output",parsed[1]),"w").write(parsed[0])
      
