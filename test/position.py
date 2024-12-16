from adafruit_servokit import ServoKit
import time
from enum import IntEnum

class Motor(IntEnum):
    # identifies the corresponding pin location with the motor location
    FL_HIP = 1
    FL_SHOULDER = 2
    FL_ELBOW = 3
    BL_HIP = 4
    BL_SHOULDER = 5
    BL_ELBOW = 6
    FR_HIP = 7
    FR_SHOULDER = 8
    FR_ELBOW = 9
    BR_HIP = 10
    BR_SHOULDER = 11
    BR_ELBOW = 12

class Robotdog:
    def __init__(self) -> None:
        self.kit = ServoKit(channels=16)
        self.upper_leg_length = 10
        self.lower_leg_length = 10
        for i in range(1, 13):
            self.kit.servo[i].set_pulse_width_range(500,2500)

    def set_angle(self, motor_id: Motor, degrees: int):
        self.kit.servo[motor_id].angle = degrees

    def pos1(self):
        self.set_angle(Motor.FL_HIP, 90)
        self.set_angle(Motor.FL_SHOULDER, 90)
        self.set_angle(Motor.FL_ELBOW, 180)
        self.set_angle(Motor.FR_HIP, 90)
        self.set_angle(Motor.FR_SHOULDER, 90)
        self.set_angle(Motor.FR_ELBOW, 0)
        self.set_angle(Motor.BL_HIP, 90)
        self.set_angle(Motor.BL_SHOULDER, 90)
        self.set_angle(Motor.BL_ELBOW, 180)
        self.set_angle(Motor.BR_HIP, 90)
        self.set_angle(Motor.BR_SHOULDER, 90)
        self.set_angle(Motor.BR_ELBOW, 0)

    def pos2(self):
        self.set_angle(Motor.FL_HIP, 90)
        self.set_angle(Motor.FL_SHOULDER, 0)
        self.set_angle(Motor.FL_ELBOW, 90)
        self.set_angle(Motor.FR_HIP, 90)
        self.set_angle(Motor.FR_SHOULDER, 180)
        self.set_angle(Motor.FR_ELBOW, 90)
        self.set_angle(Motor.BL_HIP, 90)
        self.set_angle(Motor.BL_SHOULDER, 0)
        self.set_angle(Motor.BL_ELBOW, 90)
        self.set_angle(Motor.BR_HIP, 90)
        self.set_angle(Motor.BR_SHOULDER, 180)
        self.set_angle(Motor.BR_ELBOW, 90)


if __name__ == '__main__':
    try:
        print("---開始---")
        robotdog = Robotdog()
        robotdog.pos1()
        
        # 設置初始狀態
        is_pos1 = True
        
        while True:
            action = input("按下 Enter 鍵來切換姿勢，或按 Ctrl+C 終止程式：")
            
            if is_standing:
                print("pos2")
                robotdog.pos2()
            else:
                print("pos1")
                robotdog.pos1()
                
            is_standing = not is_standing

    except KeyboardInterrupt:
        print("-!終止!-")
    finally:
        print("回位")
        robotdog.pos1()
        time.sleep(1)
        print("---結束---")