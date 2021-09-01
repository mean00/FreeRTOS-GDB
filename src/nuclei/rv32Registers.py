#
  # The stack layout is 
  #  Total 36 registers
  #  00: MEPC
#    01: x1
#    28: x28
#    29: MSTATUS
# SP is register 36
#
import gdb
import pprint
from Types import StdTypes 
from List import ListInspector 
#
# Helper class to deal with registers
#    
class aRegisters:
  def  __init__(self):
  #__________________
    #print("00\n")
    self.reg= [0] * 37
    #print("**Create **")
  def read32bits(self,adr):
  #__________________
    #print("**Read32 ** :%x" % adr)
    uint_pointer_type = gdb.lookup_type('uint32_t').pointer()
    gaddress = gdb.Value(adr)
    paddress = gaddress.cast(uint_pointer_type)
    try:
        c=int(paddress.dereference())
    #    print("=> %x" % c)
    except:
        print("** Error **")
        c=0
    return c 
#
  def dumpRegisters(self):
    for i in range(0,36):
      print("Register %d 0x%x  " % (i,self.reg[i]))
 
#
  def write32bits(self,adr,value):
  #__________________
    adr=int(adr)
    value=int(value)
    #print(adr)
    #print(value)
    st="set {int}"+hex(adr)+" = " +hex(value)
    #print(st)
    gdb.execute(st) 


  #
  # Dump registers to given address
  # You have to move the stack yourself !
  #
  # The stack layout is 
  #  Total 36 registers
  #     0: MEPC
  #     1: x1  
  #     2: x2
  # ....
  #    28: x28
  #    29: MSTATUS

  def saveRegisterToMemory(self,adr):
  #__________________
    #print("Saving regiseter to 0x%x\n" % (adr))
    self.write32bits(adr,self.reg[(0)]) # MEPC
    for i in range(1,29): # skip x0
        self.write32bits(adr+i*4,self.reg[(i)])
    self.write32bits(adr+30*4,self.reg[(30)]) # MSTATUS
  # load all the registers from the psp TCB pointer 
  def loadRegistersFromMemory(self,adr):
  #__________________
    #print('****')
    #print(" load register from 0x%x\n" % (adr))
    for i in range(0,30): # R4..R11 => 8 registers
        self.reg[i]=self.read32bits(adr+i) # NOT *4!
    self.reg[36]=adr+30
    #self.dumpRegisters()
#
#
#
  def setRegister(self,reg, value):
  #__________________
    #print("S\n")
    #print(reg)
    #print(value)
    st="set $"+str(reg)+"="+hex(value)
    #print(st)
    gdb.execute(st) 
    #print("S\n")

  # set the CPU register with the value stored in the object
  def setCPURegisters(self):
  #__________________
    #print("E\n")
    for i in range(1,29):
      r="x"+str(i)
      self.setRegister(r,self.reg[i])
   # Now MSTATUS etcx..
    self.setRegister("mstatus",self.reg[29])
    self.setRegister("mepc",self.reg[0])
    self.setRegister("sp",self.reg[36])
    #self.setRegister("msubm",self.reg[34])
    #self.setRegister("mcause",self.reg[35])
    #print("E\n")

  # read the CPU register and update our internal copy with them
  def getCPURegisters(self):
  #__________________
    #print("GA\n")
    for i in range(1,29):
      r="x"+str(i)
    #  print("G"+r+"\n")
      self.reg[i]=int(gdb.selected_frame().read_register(r) )
      self.reg[i]=self.reg[i] & 0xffffffff # unsigned hack
    # Now do mstatus mpec msubm mcause
    self.reg[29]=int(gdb.selected_frame().read_register("mstatus"))
    self.reg[0]=int(gdb.selected_frame().read_register("mepc"))
    #self.reg[34]=int(gdb.selected_frame().read_register("msubm"))
    #self.reg[35]=int(gdb.selected_frame().read_register("mcause"))
    self.reg[36]=int(gdb.selected_frame().read_register("sp"))
    #print("G\n")

  def returnFromException(self):
    mepc =int(gdb.selected_frame().read_register("mepc") )
    sp =int(gdb.selected_frame().read_register("sp") )
    self.setRegister("pc",mepc)
    self.setRegister("sp",sp+36*4)
 


