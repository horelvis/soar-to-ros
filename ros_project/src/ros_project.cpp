#include <ros/ros.h>
#include "std_msgs/String.h"
#include <dynamic_reconfigure/server.h>
#include <ros_project/mystuffConfig.h>
#include <ar_pose/ARMarkers.h>
#include <geometry_msgs/Twist.h>
#include <std_msgs/Empty.h>
#include "tf/transform_listener.h"
#include <geometry_msgs/Quaternion.h>
#include <std_srvs/Empty.h>
#include <ros/package.h>
#include <iostream>
#include <fstream>
using namespace std;
double x,y,z;
double ax,ay,az;
double xd,yd,zd;
geometry_msgs::Quaternion q;
tf::Quaternion 	qt;
std_msgs::Empty msgs;
std_srvs::Empty call;
//double error;
ros::Publisher control_vel;
ros::Publisher control_takeoff;
ros::Publisher control_landing;
ros::ServiceClient change_camera;
bool taking_off = false;
bool landing=true;
bool marker_visible=false;
int state=0;
bool state_camera =false; // 0 front 1 bottom
ros::Time begin; 
bool flag = true;
bool flag_hand = true;
int action = 0;
int a = -1;
int b = 0;
int c = 0;
bool only_once = 1;
float aux_x=0;
float aux_y=0;
float aux_z=0;
float aux_az=0;
bool hand=false;

void change_cam(){
	state_camera= !state_camera;
	change_camera.call(call);
	//ros::Duration(1).sleep();
}

void callback(const ar_pose::ARMarkers::ConstPtr& msg){
		//marker_visible=true;
		/* ---Single--- */
		//x=msg->pose.pose.position.x;
		//y=msg->pose.pose.position.y;
		//z=msg->pose.pose.position.z;	
		//q=msg->pose.pose.orientation;
		//ROS_INFO(" x: %f y: %f z: %f ",x,y,z);
		/* ---Multi--- */
		if(msg->markers.size() !=0){	// Markers size = 0 IT WONT NOT ENTER HERE
			marker_visible=true;
			a = msg->markers.size();
			b += 1;
			ROS_WARN("MARKER FOUND : %d", a);
			x =msg->markers[0].pose.pose.position.x;
			y =msg->markers[0].pose.pose.position.y;
			z =msg->markers[0].pose.pose.position.z;
			q =msg->markers[0].pose.pose.orientation;
			if(b==1)
			{
				ofstream myfile;
				myfile.open ("/home/saikishor/catkin_ws/src/marker.txt");
				myfile << "1";
				myfile.close();
			}
			ROS_INFO(" marker x: %f y: %f z: %f size: %f %f %f %f %f",x,y,z,(float)msg->markers.size(),q.x,q.y,q.z,q.w);

		}
}


/*
//void change_pattern(){
//	ros::param::set("/ar_pose/marker_pattern",ros::package::getPath("ar_pose")+"/data/4x4/4x4_95.patt");
//}
void set_velocity(float x,float y,float z, float ax,float ay,float az){
   geometry_msgs::Twist vel;
   vel.linear.x = x;
   vel.linear.y=  y;
   vel.linear.z= z;
   vel.angular.x=ax;
   vel.angular.y=ay;
   vel.angular.z=az;
   control_vel.publish(vel);
}

void update_control_law(){
	geometry_msgs::Twist vel;

	if(taking_off&&!landing){
	
		if(state == 0 && marker_visible){	
			tf::quaternionMsgToTF(q,qt);
			tf::Matrix3x3(qt).getRPY(ax,ay,az);

			set_velocity(-0.1*y,-0.1*x,0.1*(1-z),0,0,-0.1*az);
			ROS_INFO("I heard the marker 0: %f %f %f %f ",x,y,z,az);
	   	
			if(x<0.1 && x>-0.1 && y <0.1 && y>-0.1 && az<0.1 && az>-0.1 && z<1.1 && z>0.9){
				begin = ros::Time::now();
				state++;
				ROS_INFO("Aligned!"); 
			}else ROS_INFO("Aligning");
		
 		
	  	}else if(state==1){
				ROS_INFO("in state 1: Waiting 5 sec");	
				set_velocity(-0.1*y,-0.1*x,0.1*(1-z),0,0,-0.1*az);
				if((ros::Time::now()-begin).toSec()>=5){
					 state++;
				   change_cam();
					 begin = ros::Time::now();
					 ROS_INFO("LOOK FOR NEW MARKER");
					 marker_visible=false;	
				}
	  	}else if(state==2){
				ROS_INFO("In state 2:Looking for new marker");	
				if((ros::Time::now()-begin).toSec()>=1){			
					set_velocity(0,0,0,0,0,0.6);		//Rotating
					if(marker_visible){
				 		state++;
			   	 	ROS_INFO("Marker Visible Again");
					}
				}else{
					 set_velocity(0,0,0,0,0,0);	
					 marker_visible=false;				
				}
	  	}else if(state==3){
			//align with the maker
	  		ROS_INFO("In state 3: Align and go to the marker");
	  		tf::quaternionMsgToTF(q,qt);
			tf::Matrix3x3(qt).getRPY(ax,ay,az);
			ROS_INFO("Aligning on x");
			if(x<0.1 && x>-0.1){
				ROS_INFO("Aligning on y");
				if (y<0.1 && y>-0.1){
					ROS_INFO("Aligned - go there");
					if(!hand)	state++;
				}		
			}
			set_velocity(0,0,-0.3*y,0,0,-0.3*x);

	 	 }else if(state==4){
			// go there

			tf::quaternionMsgToTF(q,qt);
			tf::Matrix3x3(qt).getRPY(ax,ay,az);
			if (only_once==true){
				aux_x=0.4;
				aux_y=0;
				aux_z=0;
				aux_az=0;
				only_once = false;
			}
			
			if (z>0.9 && z<1.1){
				ROS_INFO("Final Aligning");
				aux_y=-0.1*x;	
				aux_x=-0.1*(1-z);
				aux_z=-0.1*y;
				aux_az=-0.1*az;//-0.1*az;
				if(x<0.1 && x>-0.1 && y <0.1 && y>-0.1 && az<0.1 && az>-0.1 && z<1.1 && z>0.9){
					ROS_INFO("Aligned");
					begin = ros::Time::now();
					if(!hand)state ++;
				}
			}

			set_velocity(aux_x,aux_y,aux_z,0,0,aux_az);
			ROS_INFO("I heard the marker 0: %f %f %f %f ",x,y,z,az);
		}else if(state==5){
			tf::quaternionMsgToTF(q,qt);
			tf::Matrix3x3(qt).getRPY(ax,ay,az);
			set_velocity(-0.1*(1-z),-0.1*x,-0.1*y,0,0,-0.1*az);
			if((ros::Time::now()-begin).toSec()>=5){
				control_landing.publish(msgs);
				ROS_INFO("Ready to land");				
				ROS_INFO("I heard the marker 0: %f %f %f %f",x,y,z,az);
				if(!hand)state++;
			}else ROS_INFO("Waiting 5 sec");
	
		}
		else if(state == 6){
			ROS_INFO("THE END");
		}

	}
}




void callback2(ar_node::mystuffConfig &config, uint32_t level ){

	geometry_msgs::Twist vel;
	if(!taking_off && config.take_off){
		std_msgs::Empty take;
		state=0;
		//vel.linear.z =1;
		control_takeoff.publish(take);
		begin = ros::Time::now();
		

		//control_vel.publish(vel);
		if(!state_camera) change_cam();		
	}

	if(!landing && config.land) {
		std_msgs::Empty land;
		control_landing.publish(land);
		ROS_INFO("LANDING");

	}
	taking_off=config.take_off;
	landing=config.land;
	ROS_INFO("Desired position: %d %d ",taking_off,landing);	
}

void callback_hand(leap_motion::leaphands msg){
	std_msgs::Empty take;
	std_msgs::Empty land;
	ROS_INFO("Action: %i", msg.action);
	action = msg.action;
	hand=true;
	if (action==1 && state ==0){
		control_takeoff.publish(take);
		taking_off = true;
		landing = false;
		state = 0;
		if(!state_camera) change_cam();		
		ROS_INFO("TAKING_OFF");
	}else if(action == 3&& state!=4){
		state++;
	}else if (action==4 && taking_off==true){
		control_landing.publish(land);
		state++;
		taking_off = false;
		landing = true;
		ROS_INFO("Landing");
	}
	//if (action==4 && state==5){
	//	state++;
	//}
	ROS_INFO("Action: %i", action);
}
*/

int main(int argc,char **argv){	
	// Initialize the ROS system
	ros::init(argc,argv, "ros_project");
	ofstream myfile;
	myfile.open ("/home/saikishor/catkin_ws/src/marker.txt");
	myfile << "0";
	myfile.close();
	ros::NodeHandle nh;
	ros::Subscriber sub = nh.subscribe("ar_pose_marker",1000,callback);
	change_camera = nh.serviceClient<std_srvs::Empty>("/ardrone/togglecam");
	//ros::Subscriber sub_hand =nh.subscribe("hands",1000,callback_hand);
	ros::Rate loop_rate(100);
		//update_control_law();
	//	error = sqrt((xd-x)*(xd-x)+(yd-y)*(yd-y)+(zd-z)*(zd-z));	
	//	ROS_INFO("Error: %f",error);
	change_cam();
	while(ros::ok()){
		ros::spinOnce();
		loop_rate.sleep();
	}
}
