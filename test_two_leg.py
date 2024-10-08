from adafruit_servokit import ServoKit
import adafruit_motor.servo
import time

def init_pose(kit):
    kit.servo[1].angle = 105
    kit.servo[2].angle = 90
    kit.servo[3].angle = 180
    kit.servo[4].angle = 90
    kit.servo[5].angle = 90
    kit.servo[6].angle = 180
    kit.servo[7].angle = 85
    kit.servo[8].angle = 110
    kit.servo[9].angle = 36
    kit.servo[10].angle = 100
    kit.servo[11].angle = 110
    kit.servo[12].angle = 14

def rear_leg_up(kit):
    kit.servo[5].angle += 60
    kit.servo[6].angle -= 20
    kit.servo[11].angle -= 60
    kit.servo[12].angle += 20

def rear_leg_down(kit):
    kit.servo[5].angle -= 60
    kit.servo[6].angle += 20
    kit.servo[11].angle += 60
    kit.servo[12].angle -= 20

def front_leg_up(kit):
    kit.servo[2].angle += 60
    kit.servo[3].angle -= 20
    kit.servo[8].angle -= 60
    kit.servo[9].angle += 20

def front_leg_down(kit):
    kit.servo[2].angle -= 60
    kit.servo[3].angle += 20
    kit.servo[8].angle += 60
    kit.servo[9].angle -= 20


if __name__ == '__main__':
    try:
        print("---開始---")
        kit = ServoKit(channels=16)
        init_pose(kit)
        time.sleep(1)
        for channel in range(2):
            print(f"前起")
            front_leg_up(kit)
            time.sleep(0.1)
            print(f"後起")
            rear_leg_up(kit)
            time.sleep(3)
            print(f"前下")
            rear_leg_down(kit)
            print(f"後下")
            time.sleep(0.05)
            front_leg_down(kit)
            time.sleep(1)
        print("---動作結束---")
        time.sleep(1)
    except KeyboardInterrupt:
        print("-!終止!-")
    finally:
        print("回位")
        init_pose(kit)
        time.sleep(1)
        print("---結束---")