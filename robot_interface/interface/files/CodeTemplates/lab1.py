import numpy as np
from Arm_Lib_New import Arm_Device1
import time
Arm = Arm_Device1()
time.sleep(.1)

#send home 
Arm.Arm_serial_servo_write6_array([90,90,90,90,90,90],4000)

#read home angles

#read servo home position coordinates

#send servos 2-4 independently to 0 and 180 deg and read position coordinates

#send home

#send servo 4 to 0 and 90 deg and and read position coordinates

#send servo 1 to 90 and 180 deg and read position coordinates

#Part 2 - Pick and place
# follow directions in lab manual to perform the following task
#start in home position
#open gripper (servo 6) to 180 deg
#close gripper (servo 6) to XXX degrees
#return home
#place block in position 2
#open grippers
#return home
#record final servo andles and position coordinates necessary to perform this task