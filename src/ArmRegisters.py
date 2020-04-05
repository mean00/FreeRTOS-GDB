
import gdb
import pprint
from Types import StdTypes 
from List import ListInspector 
#
# Helper class to deal with registers
#    
class aRegisters:
  def  __init__(self):
    self.reg= [0] * 16
    self.psr = 0 
    #print("**Create **")
  def read32bits(self,adr):
    #print("**Read32 ** :%x" % adr)
    uint_pointer_type = gdb.lookup_type('uint32_t').pointer()
    gaddress = gdb.Value(adr)
    paddress = gaddress.cast(uint_pointer_type)
    try:
        c=long(paddress.dereference())
    #    print("=> %x" % c)
    except:
        print("** Error **")
        c=0
    return c 
#
#
  def write32bits(self,adr,value):
    adr=long(adr)
    value=long(value)
    #print(adr)
    #print(value)
    st="set {int}"+hex(adr)+" = " +hex(value)
    #print(st)
    gdb.execute(st) 


  #
  # Dump registers to given address
  # You have to move the stack yourself !
  #
  def saveRegisterToMemory(self,adr):
    for i in range(0,8): # R4..R11 => 8 registers
        self.write32bits(adr+i*4,self.reg[(i+4)])
    # next are r0 .. r3
    adr+=8*4
    for i in range(0,4): # R4..R11 => 8 registers
        self.write32bits(adr+i*4,self.reg[i])
    adr+=4*4
    # Then r12, lr pc psr
    self.write32bits(adr,self.reg[12])
    self.write32bits(adr+1*4,self.reg[14])
    self.write32bits(adr+2*4,self.reg[15])
    self.write32bits(adr+3*4,self.psr)

  # load all the registers from the psp TCB pointer 
  def loadRegistersFromMemory(self,adr):
    #print('****')
    for i in range(0,8): # R4..R11 => 8 registers
        #print("0")
        r=self.read32bits(adr+i)
        #print("1")
        self.reg[i+4]=r
    # next are r0 .. r3
    adr+=8
    for i in range(0,4): # R4..R11 => 8 registers
        self.reg[i]=self.read32bits(adr+i)
    adr+=4
    # Then r12, lr pc psr
    self.reg[12]=self.read32bits(adr)
    self.reg[14]=self.read32bits(adr+1) # LR
    self.reg[15]=self.read32bits(adr+2) # PC
    self.psr=self.read32bits(adr+3)
    # and sp after popping all the registers
    self.reg[13]=long(adr+4)
    #for i in range(0,16):
    #    print("%d : 0x%x" % (i,self.reg[i]))
  #
  def setRegister(self,reg, value):
    #print(reg)
    #print(value)
    st="set $"+str(reg)+"="+hex(value)
    #print(st)
    gdb.execute(st) 

  # set the CPU register with the value stored in the object
  def setCPURegisters(self):
    for i in range(0,16):
      r="r"+str(i)
      self.setRegister(r,self.reg[i])
    self.setRegister("xpsr",self.psr)
  # read the CPU register and update our internal copy with them
  def getCPURegisters(self):
    for i in range(0,16):
      r="r"+str(i)
      self.reg[i]=long(gdb.selected_frame().read_register(r) )
      self.reg[i]=self.reg[i] & 0xffffffff # unsigned hack
    self.psr=long(gdb.selected_frame().read_register("xpsr"))
    #print("Read registers")
    #for i in range(0,16):
        #print("%d: 0x%x" % (i,self.reg[i]))

