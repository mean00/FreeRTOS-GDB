
import gdb
import pprint
from Types import StdTypes 
from List import ListInspector 
#
# Helper class to deal with registers
#    
class ArmRegisters:
  def  __init__(self):
    self.reg= [0] * 16
    self.psr = 0 
  def read32bits(self,adr):
    uint_pointer_type = gdb.lookup_type('uint32_t').pointer()
    gaddress = gdb.Value(address)
    paddress = gaddress.cast(uint_pointer_type)
    try:
        c=long(paddress.dereference())
    except:
        c=0
    return c 

  # load all the registers from the psp TCB pointer 
  def loadRegistersFromMemory(self,adr):
    for i in range[0,8]: # R4..R11 => 8 registers
        self.ref[i+4]=self.read32bits(adr+i)
    # next are r0 .. r3
    adr+=8
    for i in range[0,4]: # R4..R11 => 8 registers
        self.ref[i]=self.read32bits(adr)
    adr+=4
    # Then r12, lr pc psr
    self.r[12]=self.read32bits(adr)
    self.r[14]=self.read32bits(adr+1) # LR
    self.r[15]=self.read32bits(adr+2) # PC
    self.psr=self.read32bits(adr+3)
    # and sp after popping all the registers
    self.r[13]=adr+4

  #
  def setRegister(self,reg, value):
    st="gdb.execute(set $"+str(reg)+"="+value+")"
    gdb.execute(st) 

  # set the CPU register with the value stored in the object
  def setCPURegisters(self):
    for i in range[0,16]:
      self.setRegister("r"+str(i),self.r[i])
    self.setRegister("xpsr",self.psr)

