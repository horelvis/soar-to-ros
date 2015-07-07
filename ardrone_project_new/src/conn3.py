#!/usr/bin/env python

import roslib; roslib.load_manifest('ardrone_project')
import rospy
import time
import sys
from ros_drone import DroneController, MainController
from PySide import QtCore, QtGui
import ros_drone

PATH_TO_SOAR = "/home/saikishor/SoarSuite/bin"
sys.path.append(PATH_TO_SOAR)
import Python_sml_ClientInterface as sml

SOAR_GP_PATH = "/home/saikishor/SOAR/droo/drone.soar"

class SOARInterface(MainController):
	def __init__(self):
		super(SOARInterface,self).__init__()
		self.command = 0
		print "******************************\n******************************\nNew goal\n******************************\n******************************\n"
		self.first_time = time.time()
		self.kernel = self.create_kernel()
		self.agent = self.create_agent(self.kernel)
		self.agent_load_productions(self.agent,SOAR_GP_PATH)
		self.agent.SpawnDebugger()
		# p_cmd = 'learn --on'
		# res = agent.ExecuteCommandLine(p_cmd)
		# res = kernel.ExecuteCommandLine(p_cmd, agent.GetAgentName)
		self.kernel.CheckForIncomingCommands()
		p_cmd = 'watch --learning 2'
		res = self.agent.ExecuteCommandLine(p_cmd)
		print str(res)

	def __del__(self):
		self.kernel.DestroyAgent(agent)
		self.kernel.Shutdown()
		del self.kernelCommit

	def define_prohibitions(self): #TODISCOVER WTF IS THIS
		pass

	def create_kernel(self):
		self.kernel = sml.Kernel.CreateKernelInCurrentThread()
		if not self.kernel or self.kernel.HadError():
			print self.kernel.GetLastErrorDescription()
			exit(1)
		return self.kernel

	def create_agent(self, kernel):
		agent = self.kernel.CreateAgent("agent")
		if not agent:
			print self.kernel.GetLastErrorDescription()
			exit(1)
		return agent

	def agent_load_productions(self, agent, path):
		agent.LoadProductions(path)
		if agent.HadError():
			print agent.GetLastErrorDescription()
			exit(1)

	def nextAction(self):
		self.agent.Commit()  
		self.agent.RunSelfTilOutput()
		self.agent.Commands()
		numberCommands = self.agent.GetNumberCommands()
		print "Number of commands received by the agent: %s" % (numberCommands)
		i=0
		if numberCommands == 0:
			print 'KABOOOOOOOOOOOOOOOOOOM!!!!!!!!!!!!!!!'
			return 'aborted'
		else:
			while i<numberCommands:
				self.command = self.agent.GetCommand(i)
				command_name = self.command.GetCommandName()
				print "The name of the command %d/%d is %s" % (i+1,numberCommands,command_name)
				i+=1
				return  command_name

	def sendOK(self):
		self.command.AddStatusComplete()

	def senderror(self):
		self.command.AddStatusError()
		
if __name__ == '__main__':
	import sys
	rospy.init_node('connection', anonymous=True)
	rospy.logwarn('Connection node created and connection established')
	soar_interface = SOARInterface()
	rospy.logwarn('aw1')
	stf = DroneController()
	ctrl = MainController()
	rospy.logwarn('aw1')
	rospy.logwarn('aw2')
	goal_achieved = False
	rospy.logwarn('aw3')
	while not goal_achieved:
		command_name = soar_interface.nextAction()
		out = "NULL"
		if command_name == "takeoff":
			out = ctrl.Takeoff() #to take-off from land

		elif command_name == "land":
			out = ctrl.Land()  #to land from air

		elif command_name == "forward": #to Person
			out = ctrl.Forward()

		elif command_name == "left":
			out = ctrl.Left()

		elif command_name == "right":
			out = ctrl.Right()

		elif command_name == "reverse":                    
			out = ctrl.Reverse()

		elif command_name == "up":
			out = ctrl.Up()

		elif command_name == "down":          
			out = ctrl.Down()

		elif command_name == "achieved":
			goal_achieved = True
			out = "succeeded"
		else:
			print "ERROR: The Command %s doesn't exist" % (command_name)
			soar_interface.sendOK()

		print "SM return: %s \n\n" % (out) 
		if out=="succeeded": 
			soar_interface.sendOK()
		elif out=="aborted":
			soar_interface.senderror()
		else:
			print "gpsrSoar interface: unknown ERROR"
			exit(1)

	soar_interface.sendOK()

	rospy.signal_shutdown('Great Flying!')
