#!/usr/bin/env python

import roslib; roslib.load_manifest('ardrone_project')
import rospy
import time
from ros_drone import DroneController, MainController
from PySide import QtCore, QtGui

from drone_status import DroneStatus

class control(MainController, DroneController):
	def __init__(self):
		super(control,self).__init__()
	def con(self):
		ctrl.Takeoff()
		time.sleep(2)
		ctrl.Forward()
		time.sleep(3)
		ctrl.Up()
		time.sleep(2)
		ctrl.Reverse()
		time.sleep(3)
		ctrl.Land()

if __name__ == '__main__':
	import sys
	rospy.init_node('connection', anonymous=True)
	rospy.logwarn('Connection node created and connection established')
	stf = DroneController()
	ctrl = MainController()
	keys=control()
	time.sleep(5)
	keys.con()
	time.sleep(5)
	rospy.signal_shutdown('Great Flying!')
