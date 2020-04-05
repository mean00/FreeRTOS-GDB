# File: FreeRTOS.py
# This is the arm without ** FPU ** version of the original freeRTS GDB
# It was modified by mean00 to add 
#    * More details on TCB, display similar to info threads
#    * switchTCB command to switch threads
#  2020
# --- Original Header ---
# Author: Carl Allendorph
# Date: 05NOV2014 
#
# Description:
#   This file contains some python code that utilizes the GDB API 
# to inspect information about the FreeRTOS internal state. The 
# idea is to provide the user with the ability to inspect information 
# about the tasks, queues, mutexs, etc. 
# 

import gdb
import pprint
from Types import StdTypes 
from List import ListInspector 
from GDBCommands import ShowHandleName, ShowRegistry, ShowList
from GDBCommands import ShowQueueInfo
from ArmRegisters import aRegisters

#
# Helper class to deal with registers
#    
class Scheduler:
  
  def __init__(self):
    self.allTasks = [] 
    self._blocked = ListInspector("xSuspendedTaskList")
    self._delayed1 = ListInspector("xDelayedTaskList1")
    self._delayed2 = ListInspector("xDelayedTaskList2")
    self._readyLists = []
    readyTasksListsStr = "pxReadyTasksLists"
    # Current TCB
    self._currentTCB,tcbMethod=gdb.lookup_symbol("pxCurrentTCB")
    if( self._currentTCB != None):
        self._currentTCBv=self._currentTCB.value()
    self._currentTCBAddress= gdb.parse_and_eval("pxCurrentTCB").address
     # Ready 
    readyListsSym,methodType = gdb.lookup_symbol(readyTasksListsStr)
    if ( readyListsSym != None ): 
      readyLists = readyListsSym.value()
      minIndex, maxIndex = readyLists.type.range()
      for i in range(minIndex, maxIndex+1):
        readyList = readyLists[i]
        FRReadyList = ListInspector( readyList )
        self._readyLists.append(FRReadyList)
      self.getTasks()
    else: 
      print("Failed to Find Symbol: %s" % readyTasksListsStr)
      raise ValueError("Invalid Symbol!")

  # sort by TCB
  def sortTCB(self,e):
    return e[0]
#
# dump the tasks
#
  def ShowTaskList(self): 
     # dump them
    dex=0
    for t in self.allTasks:
        tcbPointer=t[0]
        status=t[1]
        tcbContent=t[2]
        # Current Task, info on the stack are irrelevant
        if(self._currentTCBv == tcbPointer):
            current="*"
            print("%d %s TCB: 0x%08x Name:%12s " % (dex,current, tcbPointer,tcbContent['pcTaskName'].string()))
        else:
            #where=
            current=" "
            stack=tcbContent['pxTopOfStack']
            where=""
            print("%d %s TCB: 0x%08x Name:%12s State:%s TopOfStack:0x%08x" % (dex, current, tcbPointer,tcbContent['pcTaskName'].string(), status, stack))
            self.getAdditionInfo(stack)
        dex=dex+1
#
# Get a list of created tasks + some properties
#
  def getTasks(self): 
    for i,rlist in enumerate(self._readyLists):
      if i == 0:
        items = rlist.GetElements( "TCB_t", 0 )
      else: 
        items = rlist.GetElements( "TCB_t", 1 )
      if ( len(items) > 0 ): 
        for tcb,val,ptr in items:           
          ## print(tcb, tcb.type.name, val, val.type.name)
          tem = [ptr,"Ready ",tcb,None]
          self.allTasks.append(tem)

    items = self._blocked.GetElements("TCB_t")
    for tcb,val,ptr in items:  
          tem = [ptr,"Blked ",tcb,None]
          self.allTasks.append(tem)

    items = self._delayed1.GetElements("TCB_t")
    for tcb,val,ptr in items:           
          tem = [ptr,"Delay1",tcb,None]
          self.allTasks.append(tem)

    items = self._delayed2.GetElements("TCB_t")
    for tcb,val,ptr in items:           
          tem = [ptr,"Delay1",tcb,None]
          self.allTasks.append(tem)

    self.allTasks.sort(key=self.sortTCB)
#
#
#
  def GetSymbolForAddress(self,adr):
     block = gdb.block_for_pc(adr)
     try:
        while block and not block.function:
           block = block.superblock
        return block.function.print_name
     except:
       print("*Error *")
       return "???"
#
#
#
  def Read32(self,address):
    uint_pointer_type = gdb.lookup_type('uint32_t').pointer()
    gaddress = gdb.Value(address)
    paddress = gaddress.cast(uint_pointer_type)
    try:
        c=long(paddress.dereference())
    except:
        print("*Error *")
        c=0
    return c 

#
#
#
  def getAdditionInfo(self, topStack):
    # Now retrieve actual stack pointer, PC and LR
    # The layout is 
    # Top Base : 8*4 = R4...R11
    #            4*4 = R0...R3
    #            1*4 = R12
    #            1*4 = LR
    #            1*4 = PC
    #            1*4 = PSR
    #print("base 0x%x" % (topStack))
    importantRegisters=topStack+(13) # skip registers
    LR=self.Read32(importantRegisters)
    PC=self.Read32(importantRegisters+1)
    # This is the address of the user stack, i.e. after the 16 registers saved by FreeRTOS
    actualStack=topStack+16
    print("\t\t LR=0x%x PC=0x%x SP=0x%x function=%s" % (LR, PC, actualStack,self.GetSymbolForAddress(PC)))
#
#
#
  def switchTCB(self,task):
    print("switch TCB %d " % task)
    # Dereference address to get stack
    if(task>=len(self.allTasks)):
        print("out of range")
        return

    # First save the current task
    old=aRegisters()
    old.getCPURegisters()
    found=None
    # Search the current TCB
    for t in self.allTasks:
        if(t[0]==self._currentTCBv):
            # got it
            found=t[2]
    if( found is None):
        print("Cannot locate current TCB")
        return
    #
    # Rewind by 4*4*4 bytes = 64 bytes / 16 registers
    sp=old.reg[13]
    sp-=64    
    # store them
    old.saveRegisterToMemory(sp) 
    # update xtopStack with new value
    old.write32bits(self._currentTCBv,old.reg[13]-64)
    t=self.allTasks[task]
    # [0] => TCB pointer
    # [1] => State
    # [2] => TCB structure 
    if(t[0]==self._currentTCBv):
        print("task already selected")
        return
    tcbContent=t[2]
    stack=tcbContent['pxTopOfStack']
    # 1-load registers
    regs=aRegisters()
    regs.loadRegistersFromMemory(stack) # regs now contains the address
    regs.setCPURegisters()   # set the actual registers

    # update pxCurrentTCB
    print("Updating current TCB to %x" % t[0])
    regs.write32bits( self._currentTCBAddress,t[0]) 
#
#
#
#
class ShowTaskList(gdb.Command):
  """ Generate a print out of the current tasks and their states.
  """
  def __init__(self):
    super(ShowTaskList, self).__init__(
      "show Task-List", 
      gdb.COMMAND_SUPPORT
      )

  def invoke(self, arg, from_tty):
    sched = Scheduler()
    sched.ShowTaskList()

#
#
#
#
class SwitchTCB(gdb.Command):
  """ Switch to the TCB address given as parameter (hex address i.e 0x1234)
  """
  def __init__(self):
    super(SwitchTCB, self).__init__(
      "switchTCB", 
      gdb.COMMAND_SUPPORT
      )

  def invoke(self, arg, from_tty):
    argv = gdb.string_to_argv(arg)
    if(len(argv)!=1):
        print("Please give Task index as paramter\n");
        return
    sched = Scheduler()
    task=int(argv[0])
    sched.switchTCB(task)
    #
ShowRegistry()
ShowList()
ShowTaskList()
ShowHandleName()
ShowQueueInfo()
SwitchTCB()

