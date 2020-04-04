# File: FreeRTOS.py
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
    

class Scheduler:
  
  def __init__(self): 
    
    self._blocked = ListInspector("xSuspendedTaskList")
    self._delayed1 = ListInspector("xDelayedTaskList1")
    self._delayed2 = ListInspector("xDelayedTaskList2")
    self._readyLists = []
    readyTasksListsStr = "pxReadyTasksLists"
    # Current TCB
    self._currentTCB,tcbMethod=gdb.lookup_symbol("pxCurrentTCB")
    if( self._currentTCB != None):
        self._currentTCBv=self._currentTCB.value()
     # Ready 
    readyListsSym,methodType = gdb.lookup_symbol(readyTasksListsStr)
    if ( readyListsSym != None ): 
      readyLists = readyListsSym.value()
      minIndex, maxIndex = readyLists.type.range()
      for i in range(minIndex, maxIndex+1):
        readyList = readyLists[i]
        FRReadyList = ListInspector( readyList )
        self._readyLists.append(FRReadyList)
    else: 
      print("Failed to Find Symbol: %s" % readyTasksListsStr)
      raise ValueError("Invalid Symbol!")

  def ShowTaskList(self): 
    self.PrintTableHeader()
    print("Running Task")
    print("-------------")
    print("Current TCB=0x%x" % self._currentTCBv)
    self.PrintTaskFormatted(self._currentTCBv)
    # Other tasks
    for i,rlist in enumerate(self._readyLists):
      if i == 0:
        items = rlist.GetElements( "TCB_t", 0 )
      else: 
        items = rlist.GetElements( "TCB_t", 1 )
      if ( len(items) > 0 ): 
        print("Ready List {%d}: Num Tasks: %d" % (i, len(items)))
        print("-----------------------------------")
        for tcb,val in items:           
          ## print(tcb, tcb.type.name, val, val.type.name)
          self.PrintTaskFormatted(tcb)

    items = self._blocked.GetElements("TCB_t")
    print("Blocked List: Num Tasks: %d" % len(items))
    print("-----------------------------------")
    for tcb,val in items:           
      self.PrintTaskFormatted(tcb)

    items = self._delayed1.GetElements("TCB_t")
    print("Delayed {1}: Num Tasks: %d" % len(items))
    print("-----------------------------------")
    for tcb,val in items:           
      self.PrintTaskFormatted(tcb, val)

    items = self._delayed2.GetElements("TCB_t")
    print("Delayed {2}: Num Tasks: %d" % len(items))
    print("-----------------------------------")
    for tcb,val in items:           
      self.PrintTaskFormatted(tcb, val)


  def PrintTableHeader(self):
    print("%16s %3s %4s" % ("Name", "PRI", "STCK"))

  def read32bitsAddresss(self,address):
    uint_pointer_type = gdb.lookup_type('uint32_t').pointer()
    gaddress = gdb.Value(address)
    paddress = gaddress.cast(uint_pointer_type)
    try:
        c=long(paddress.dereference())
    except:
        c=0
    return c 
  def GetSymbolForAddress(self, adr):
      block = gdb.block_for_pc(adr)
      try:
         while block and not block.function:
            block = block.superblock
         return block.function.print_name
      except:
        return "???"

  def PrintTaskFormatted(self, task, itemVal = None):
    ## print("TASK %s TCB address: 0x%x\n" % (str(task), task.address))
    #print("Task")
    #print(task)
    topStack=task['pxTopOfStack']
    stackBase = task['pxStack']
    highWater = topStack - stackBase
    taskName = task['pcTaskName'].string()
    taskPriority = task['uxPriority']
    if ( itemVal != None ):
      print("%16s Pri:%3s High:%4s stack:0x%x val:%5s"  % (taskName, taskPriority, highWater, topStack, itemVal))
    else:
      print("%16s Pri:%3s High:%4s stack:0x%x " % (taskName, taskPriority, highWater,topStack))
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
    LR=self.read32bitsAddresss(importantRegisters)
    PC=self.read32bitsAddresss(importantRegisters+1)
    actualStack=topStack+16
    print("\t\t LR=0x%x PC=0x%x SP=0x%x" % (LR, PC, actualStack))
    print("\t\t %s" %   self.GetSymbolForAddress(PC))
    print("\t\t\t %s" %   self.GetSymbolForAddress(LR))
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




ShowRegistry()
ShowList()
ShowTaskList()
ShowHandleName()
ShowQueueInfo()

