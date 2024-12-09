from adafruit_servokit import ServoKit
import time
import numpy as np
import bezier
from enum import IntEnum
import math

class Motor(IntEnum):
    # identifies the corresponding pin location with the motor location
    FL_HIP = 1
    FL_SHOULDER = 2
    FL_ELBOW = 3

    FR_HIP = 7
    FR_SHOULDER = 8
    FR_ELBOW = 9

    BL_HIP = 4
    BL_SHOULDER = 5
    BL_ELBOW = 6

    BR_HIP = 10
    BR_SHOULDER = 11
    BR_ELBOW = 12

    FL_HIP_OFFSET = 0
    FL_SHOULDER_OFFSET = 0
    FL_ELBOW_OFFSET = 0

    FR_HIP_OFFSET = 0
    FR_SHOULDER_OFFSET = 0
    FR_ELBOW_OFFSET = 0

    BL_HIP_OFFSET = 0
    BL_SHOULDER_OFFSET = 0
    BL_ELBOW_OFFSET = 0

    BR_HIP_OFFSET = 0
    BR_SHOULDER_OFFSET = 0
    BR_ELBOW_OFFSET = 0

    @classmethod
    def to_offset(cls, motor):
        # Mapping motor to its corresponding offset
        offset_mapping = {
            cls.FL_HIP: cls.FL_HIP_OFFSET,
            cls.FL_SHOULDER: cls.FL_SHOULDER_OFFSET,
            cls.FL_ELBOW: cls.FL_ELBOW_OFFSET,
            cls.BL_HIP: cls.BL_HIP_OFFSET,
            cls.BL_SHOULDER: cls.BL_SHOULDER_OFFSET,
            cls.BL_ELBOW: cls.BL_ELBOW_OFFSET,
            cls.FR_HIP: cls.FR_HIP_OFFSET,
            cls.FR_SHOULDER: cls.FR_SHOULDER_OFFSET,
            cls.FR_ELBOW: cls.FR_ELBOW_OFFSET,
            cls.BR_HIP: cls.BR_HIP_OFFSET,
            cls.BR_SHOULDER: cls.BR_SHOULDER_OFFSET,
            cls.BR_ELBOW: cls.BR_ELBOW_OFFSET
        }
        
        # Return the offset for the specified motor
        return offset_mapping.get(motor, None)
        

class Robotdog:
    def __init__(self) -> None:
        self.kit = ServoKit(channels=16)
        self.upper_leg_length = 10
        self.lower_leg_length = 10
        for i in range(1, 13):
            self.kit.servo[i].set_pulse_width_range(500,2500)

    def set_angle(self, motor_id: Motor, degrees: int):
        # print("angle adjust id: ", motor_id)
        # print("from: ", degrees, ", to: ", degrees + Motor.to_offset(motor_id))
        self.kit.servo[motor_id].angle = degrees + Motor.to_offset(motor_id)

    def rad_to_degree(self, rad):
        return rad*180/math.pi
    
    def calibrate(self):
        self.set_angle(Motor.FL_HIP, 90)
        self.set_angle(Motor.FL_SHOULDER, 0)
        self.set_angle(Motor.FL_ELBOW, 160)
        self.set_angle(Motor.FR_HIP, 90)
        self.set_angle(Motor.FR_SHOULDER, 180)
        self.set_angle(Motor.FR_ELBOW, 20)

        self.set_angle(Motor.BL_HIP, 90)
        self.set_angle(Motor.BL_SHOULDER, 0)
        self.set_angle(Motor.BL_ELBOW, 160)
        self.set_angle(Motor.BR_HIP, 90)
        self.set_angle(Motor.BR_SHOULDER, 180)
        self.set_angle(Motor.BR_ELBOW, 20)

    def calibrate_by_inverse_positioning(self):
        x, y, z = (0, -15, 0)
        self.inverse_positioning(Motor.FL_SHOULDER,Motor.FL_ELBOW,x,y,z=z,hip=Motor.FL_HIP,right=False)
        self.inverse_positioning(Motor.FR_SHOULDER,Motor.FR_ELBOW,x,y,z=z,hip=Motor.FR_HIP,right=True)
        self.inverse_positioning(Motor.BL_SHOULDER,Motor.BL_ELBOW,x,y,z=z,hip=Motor.BL_HIP,right=False)
        self.inverse_positioning(Motor.BR_SHOULDER,Motor.BR_ELBOW,x,y,z=z,hip=Motor.BR_HIP,right=True)


    def inverse_positioning(self, shoulder, elbow, x, y, z=0, hip=None, right=True):
        '''
        Positions the end effector at a given position based on cartesian coordinates in 
        centimeter units and with respect to the should motor of the
        :param shoulder: motor id used for the shoulder
        :param elbow: motor id used for the elbow
        :param x: cartesian x with respect to shoulder motor (forward/back)
        :param y: cartesian y with respect to shoulder motor (up/down)
        :param z: cartesian z with respect to shoulder motor (left/right)
        :param hip: motor id used for the hip
        :param right: a boolean that flips the logic for left and right side to properly map "forward direction"
        :return: a list containing the appropriate angle for the shoulder and elbow
        '''
        L=0
        # 距離
        y_prime = -math.sqrt((z+L)**2 + y**2)
        thetaz = math.atan2(z+L,abs(y))-math.atan2(L,abs(y_prime))

        elbow_offset = 0
        shoulder_offset = 0
        a1 = self.upper_leg_length
        a2 = self.lower_leg_length

        c2 = (x**2+y_prime**2-a1**2-a2**2)/(2*a1*a2)
        s2 = math.sqrt(1-c2**2)
        theta2 = math.atan2(s2,c2)
        c2 = math.cos(theta2)
        s2 = math.sin(theta2)

        c1 = (x*(a1+(a2*c2)) + y_prime*(a2*s2))/(x**2+y_prime**2)
        s1 = (y_prime*(a1+(a2*c2)) - x*(a2*s2))/(x**2+y_prime**2)
        theta1 = math.atan2(s1,c1)
        # generate positions with respect to robot motors
        theta_shoulder = -theta1
        theta_elbow = theta_shoulder - theta2
        theta_hip = 0
        if right:
            theta_shoulder = self.rad_to_degree(theta_shoulder) + shoulder_offset
            theta_elbow = self.rad_to_degree(theta_elbow) + elbow_offset
            if hip:
                theta_hip = 90 - self.rad_to_degree(thetaz)
        else:
            theta_shoulder = 180 - self.rad_to_degree(theta_shoulder) - shoulder_offset
            theta_elbow = 180 - self.rad_to_degree(theta_elbow) - elbow_offset
            if hip:
                theta_hip = 90 + self.rad_to_degree(thetaz)
        print("Moving leg: ", shoulder, elbow)
        print("to: ( ", x, y, z, ")")
        print("theta shoulder:",theta_shoulder,"\ttheta_elbow:",theta_elbow)
        self.set_angle(shoulder, theta_shoulder)
        self.set_angle(elbow, theta_elbow)
        if hip:
            self.set_angle(hip, theta_hip)
        return [theta_shoulder, theta_elbow]

    def leg_position(self, leg_id, x, y, z=0):
        """
        wrapper for inverse position that makes it easier to control each leg for making fixed paths
        :param led_id: string for the leg to be manipulated
        :param x: cartesian x with respect to shoulder motor (forward/back)
        :param y: cartesian y with respect to shoulder motor (up/down)
        :param z: cartesian z with respect to shoulder motor (left/right)
        """
        if leg_id == 'FL':
            self.inverse_positioning(Motor.FL_SHOULDER, Motor.FL_ELBOW, x, y, z=z, hip=Motor.FL_HIP, right=False)
        if leg_id == 'FR':
            self.inverse_positioning(Motor.FR_SHOULDER, Motor.FR_ELBOW, x, y, z=z, hip=Motor.FR_HIP, right=True)
        if leg_id == 'BL':
            self.inverse_positioning(Motor.BL_SHOULDER, Motor.BL_ELBOW, x, y, right=False)
        if leg_id == 'BR':
            self.inverse_positioning(Motor.BR_SHOULDER, Motor.BR_ELBOW, x, y, right=True)
    
    def move(self, controller=None):
        """
        Walks around based on the controller inputted momentum
        :param controller: the controller that is called to determine the robot momentum
        :returns: None, enters an infinite loop 
        """
        momentum = np.asarray([0,0,1,0],dtype=np.float32)  # 前三個值 x(前後), z(左右), y(上下) 為步伐大小的縮放值, 第四個值不為 0 時結束動作
        index = 0
        
        # Generate footstep
        s_vals = np.linspace(0.0, 1.0, 20)  # from 0 to 1, sperate to 20 point
        step_nodes = np.asfortranarray([  # define the curve using these four points -> bezier curve
            [-1.0, -1.0, 1.0, 1.0],
            [-1.0, -1.0, 1.0, 1.0],
            [-15.0, -10, -10, -15.0],
        ])
        curve = bezier.Curve(step_nodes, degree=3)
        step = curve.evaluate_multi(s_vals)
        slide_nodes = np.asfortranarray([
            [1.0, -1.0],
            [1.0, -1.0],
            [-15.0, -15],
        ])
        curve = bezier.Curve(slide_nodes, degree=1)
        slide = curve.evaluate_multi(s_vals)

        motion = np.concatenate((step,slide), axis=1)

        close = False
        while not close:
            momentum = controller(momentum)
            tragectory = motion * momentum[:3, None]
            if momentum[3]:
                close = True
            x,z,y = tragectory
            # 
            i1 = index%40
            i2 = (index+20)%40 
            # Apply movement based movement
            print(x[i1], y[i1], z[i1])
            self.inverse_positioning(Motor.FL_SHOULDER,Motor.FL_ELBOW,x[i1],y[i1],z=z[i1],hip=Motor.FR_HIP,right=False)
            time.sleep(0.5)
            index += 1

def controller(momentum):
    momentum[:3] = [4, 0, 1]
    return momentum


if __name__ == '__main__':
    robotdog = Robotdog()
    
    print("Calibrating robot dog to default position...")
    robotdog.calibrate()
    action = input("press 'Enter' to -> Standup")
    robotdog.calibrate_by_inverse_positioning()
    action = input("press 'Enter' to start ->")

    momentum = np.asarray([1, 0, 1, 0], dtype=np.float32)  # 最後一個值為 0 表示不關閉

    print("Starting robot dog movement. Press Ctrl+C to stop.")
    try:
        robotdog.move(controller)  # 使用 lambda 傳遞 momentum 給 controller
    except KeyboardInterrupt:
        print("\nCtrl+C detected! Sending stop signal to robot dog...")

        momentum[3] = 1
        time.sleep(1)
        robotdog.calibrate()
        print("Movement stopped by user. Exiting program.")