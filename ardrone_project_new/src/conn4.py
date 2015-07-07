#!/usr/bin/env python

import roslib; roslib.load_manifest('ardrone_project')
import rospy
import time
from ros_drone import DroneController, MainController
from PySide import QtCore, QtGui
import ros_drone
import sys

PATH_TO_SOAR = "/home/saikishor/SoarSuite/bin"
sys.path.append(PATH_TO_SOAR)
import Python_sml_ClientInterface as sml

#path = PATH_TO_SOAR
#sys.path.append(path)

SOAR_GP_PATH = "/home/saikishor/SOAR/droo2/drone.soar"

out = "NULL"

class SOARInterface(MainController):
	def __init__(self):
		super(SOARInterface,self).__init__()

	def action(self, comm):
		command_name = comm
		global out
		if command_name == "takeoff":
			out = ctrl.Takeoff() #to take-off from land
			rospy.logwarn('takeoff')

		elif command_name == "land":
			out = ctrl.Land()  #to land from air
			rospy.logwarn('land')

		elif command_name == "forward": #to Person
			out = ctrl.Forward()
			rospy.logwarn('forward')

		elif command_name == "left":
			out = ctrl.Left()
			rospy.logwarn('left')

		elif command_name == "right":
			out = ctrl.Right()
			rospy.logwarn('right')

		elif command_name == "reverse":                    
			out = ctrl.Reverse()
			rospy.logwarn('reverse')

		elif command_name == "up":
			out = ctrl.Up()
			rospy.logwarn('up')

		elif command_name == "down":          
			out = ctrl.Down()
			rospy.logwarn('down')

		elif command_name == "achieved":
			goal_achieved = True
			out = "succeeded"
			rospy.logwarn('goal_achieved')
		else:
			rospy.logwarn(command_name)
			command.AddStatusComplete()
		rospy.logwarn(out)

	def sendOK(self):
		return "succeeded"


def define_prohibitions(): #TODISCOVER WTF IS THIS
	pass

def create_kernel():
	kernel = sml.Kernel.CreateKernelInCurrentThread()
	if not kernel or kernel.HadError():
		print kernel.GetLastErrorDescription()
		exit(1)
	return kernel

def create_agent(kernel, name):
	agent = kernel.CreateAgent("agent")
	if not agent:
		print kernel.GetLastErrorDescription()
		exit(1)
	return agent

def agent_load_productions(agent, path):
	agent.LoadProductions(path)
	if agent.HadError():
		print agent.GetLastErrorDescription()
		exit(1)

if __name__ == '__main__':
	import sys
	rospy.init_node('connection', anonymous=True)
	rospy.logwarn('Connection node created and connection established')
	soar_interface = SOARInterface()
	stf = DroneController()
	ctrl = MainController()
	rospy.logwarn(SOAR_GP_PATH)

	print "******************************\n******************************\nNew goal\n******************************\n******************************\n"
	first_time = time.time()
	kernel = create_kernel()
	agent = create_agent(kernel, "agent")
	agent_load_productions(agent,SOAR_GP_PATH)
	agent.SpawnDebugger()

	# p_cmd = 'learn --on'
	# res = agent.ExecuteCommandLine(p_cmd)
	# res = kernel.ExecuteCommandLine(p_cmd, agent.GetAgentName)
	kernel.CheckForIncomingCommands()
	p_cmd = 'watch --learning 2'
	res = agent.ExecuteCommandLine(p_cmd)
	print str(res)

	goal_achieved = False
	time.sleep(10)
	while not goal_achieved:
		agent.Commit()  
		agent.RunSelfTilOutput()
		agent.Commands()
		numberCommands = agent.GetNumberCommands()
		print "Number of commands received by the agent: %s" % (numberCommands)
		rospy.logwarn("number of commands received: ")
		rospy.logwarn(numberCommands)
		i=0
		out="NULL"
		if numberCommands == 0:
			print 'KABOOOOOOOOOOOOOOOOOOM!!!!!!!!!!!!!!!'
			rospy.logwarn('didnot receive any command')
		else:
			while i<numberCommands:
				command = agent.GetCommand(i)
				command_name = command.GetCommandName()
				print "The name of the command %d/%d is %s" % (i+1,numberCommands,command_name)
				rospy.logwarn(command_name)
				soar_interface.action(command_name)
				if command_name == "achieved":
					goal_achieved = True
					rospy.logwarn('goal achieved!!! congrats')
				i+=1
				rospy.logwarn(out)
				print "SM return: %s \n\n" % (out) 
				if out=="succeeded": 
					command.AddStatusComplete()
					rospy.logwarn("AddStatusComplete sent")
				elif out=="aborted":
					command.AddStatusError()
				else:
					print "gpsrSoar interface: unknown ERROR"
					exit(1)
	command.AddStatusComplete()

	kernel.DestroyAgent(agent)
	kernel.Shutdown()
	#del kernelCommit

	rospy.signal_shutdown('Great Flying!')


