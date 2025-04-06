import os
import sys
import re
def read_until_nested_parenthesis(data,index,amt,target=0):
  ogindex=index
  while 1:
    index+=1
    if data[index]=="(":
      amt+=1
    elif data[index]==")":
      amt-=1
    if amt==target:
      return index,data[ogindex:index-amt]
def read_until(data,index,pattern,escapechar=None):
  original_index=index
  escaped=False
  while 1: #index<len(data) and not data[index:].startswith(pattern):
    index+=1
    if escaped: 
      index+=1
    escaped=False
    if index>=len(data) or data[index].startswith(pattern): break
    if data[index].startswith(escapechar):
      escaped=True
      index+=len(escapechar)
  return index+len(pattern),data[original_index:index].replace(escapechar,"")

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

def parse(title,args=[],type="filename"):
  if type=="filename":
    try: file=open(os.path.join(build_directory,title)).read()
    except FileNotFoundError: raise ValueError("Invalid title")
  else: file=title
  parsed=""
  index=0
  route=None
  while True:
    if file[index:index+3]=="(((":
      newindex,data=read_until_nested_parenthesis(file,index+3,3)
      index,command=read_until(file, index+3,";","((()))")
      newargs=[]
      while index<newindex:
        newargs.append(parse(read_until(file, index+3,";","((()))")[1],args,"data"))
      if command=="system":
        parsed+=systemhook(newargs)
      elif command=="route":
        if len(newargs)!=1: raise ValueError("Route takes exactly one argument")
        route=newargs[0]
      elif command=="arg":
        parsed+=findarg(args,newargs[0],newargs[1])
      else:
        parsed+=parse(command,newargs)[0]
    else:
      parsed+=file[index]
      index+=1
    if index==len(file): break
  return parsed,route

if __name__=="__main__":
  build_directory=sys.argv[1]
  if not os.path.isdir(build_directory):
    print("Argument 1 is not a valid directory")
    exit(1)
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
