armFreeRTOS-GDB
================

Intro by mean00:

This is a modified version of FreeRTOS-GDB (https://github.com/autolycus/FreeRTOS-GDB) for my needs
Bottom line, i use a blackmagic clone debugger and it does not support FreeRTOS
I just want to have backtrack for all the tasks on the system
to see what they are doing and why they are stuck

The aim is to be similar to the "info thread" "thread x" commands of gdb

Diclaimer : I probably broke the other functions + i'm not a python developper





##Requirements: 

1. You need to have the python API enabled in your version of GDB. This is a 
    compile time option when building GDB. You should be able to do something
	  like this: 
```
	gdb> python print "Hello World" 
```

and get predictable results. If it throws an error - then you don't have 
python compiled in your version of GDB.

2. Need to be using FreeRTOS 8.0+. This code could probably be used with FreeRTOS
    version 7.0 or previous versions, but the current code doesn't support it.

3. You need to use the Handle Registry for Queue info to be any use.
    Note that this only works for Queue based objects and not 
    for EventGroups 

4. You need to put the FreeRTOS-GDB/src directory on your python path: 
```
	$> export PYTHONPATH=~/src/FreeRTOS-GDB/src/
```
5. It only works for cortex M0/Mxxx WITHOUT FPU. There is an extra register saved if a FPU is there which will break the decoding

How To Use: 
```
$> gdb ./bin/program.elf 
(gdb) c 
Program runs on embedded device, sets up tasks, and queues 
<Break>
(gdb) source ~/FreeRTOS-GDB/src/FreeRTOS.py 
(gdb) show Task-List 
0   TCB: 0x20001160 Name:    MainTask State:Delay1 TopOfStack:0x200010f0
                 LR=0x8005fa7 PC=0x8006078 SP=0x20001130 function=vTaskDelay
1   TCB: 0x20001348 Name:      dummy1 State:Delay1 TopOfStack:0x200012f0
                 LR=0x8005fa7 PC=0x8006078 SP=0x20001330 function=vTaskDelay
2   TCB: 0x20001530 Name:      dummy2 State:Delay1 TopOfStack:0x200014d8
                 LR=0x8005fa7 PC=0x8006078 SP=0x20001518 function=vTaskDelay
3 * TCB: 0x20001988 Name:        IDLE 

        
```
The task marked with a "*" is the running one
If you want to switch to another one, just 
```
(gdb)switchTCB 2
switch TCB 2 
Updating current TCB to 20001530
(gdb)show Task-List
0   TCB: 0x20001160 Name:    MainTask State:Delay1 TopOfStack:0x200010f0
                 LR=0x8005fa7 PC=0x8006078 SP=0x20001130 function=vTaskDelay
1   TCB: 0x20001348 Name:      dummy1 State:Delay1 TopOfStack:0x200012f0
                 LR=0x8005fa7 PC=0x8006078 SP=0x20001330 function=vTaskDelay
2 * TCB: 0x20001530 Name:      dummy2 
3   TCB: 0x20001988 Name:        IDLE State:Ready  TopOfStack:0x20001938
                 LR=0x8006361 PC=0x8005c22 SP=0x20001978 function=prvCheckTasksWaitingTermination
```
Now you can use backtrack, up , down etc.. on the 2nd task.

Again, i'm not a python developper, the code is a hack but it does what i needed
It might be helpful for others