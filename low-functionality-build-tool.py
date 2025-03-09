import os
import sys
import re

def read_until(data,index,pattern):
  original_index=index
  while index<len(data) and not data[index:].startswith(pattern):
    index+=1
  return index+len(pattern),data[original_index:index]

def systemhook(args):
  raise ValueError("Invalid system hook")

def findarg(args,target,placeholder):
  new_args=[]
  for i in args:
    if "="  in i:
      new_args.append([i.split("=")[0],"=".join(i.split("=")[1:])])
    else:
      new_args.append(["",i])
  try:
    return new_args[int(target)][1]
  except IndexError:
    return placeholder
  except ValueError:
    for i in new_args:
      if i[0]==target:
        return i[1]
  return placeholder

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
      elif command=="arg":
        parsed+=findarg(args,newargs[0],newargs[1])
      else:
        parsed+=parse(command,args)[0]
    else:
      parsed+=file[index]
      index+=1
    if index==len(file): break
  return parsed,route

if __name__=="__main__":
  build_directory=sys.argv[1]
  if not os.path.isdir(build_directory):
    print("Argument 1 is not a valid directory")
    exit()
  if len(sys.argv)>2:
    outdir=sys.argv[2]
  else:
    outdir="out"
  os.makedirs(outdir,exist_ok=True)
  for file in os.listdir(build_directory):
    parsed=parse(file)
    if parsed[1] is not None:
      os.makedirs(os.path.join(outdir,os.path.dirname(parsed[1])),exist_ok=True)
      open(os.path.join(outdir,parsed[1]),"w").write(parsed[0])