from __future__ import print_function
from flask import Flask, jsonify, request, redirect, render_template, Response
from redis import Redis
import time
import requests
import os, sys
import dynamixel_sdk

app = Flask(__name__)
redis = Redis(host='redis', port=6379)


def motor():
    if os.name == 'nt':
        import msvcrt
        def getch():
            return msvcrt.getch().decode()
    else:
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        def getch():
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch

    # Control table address
    ADDR_MX_TORQUE_ENABLE = 24  # 64               # Control table address is different in Dynamixel model
    ADDR_MX_GOAL_POSITION = 30  # 116
    ADDR_MX_PRESENT_POSITION = 36  # 132

    # Protocol version
    PROTOCOL_VERSION = 1.0  # See which protocol version is used in the Dynamixel

    # Default setting
    DXL_ID = 1  # Dynamixel ID : 1
    BAUDRATE = 1000000  # Dynamixel default baudrate : 57600
    DEVICENAME = '/dev/ttyUSB0'  # Check which port is being used on your controller
    # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"

    TORQUE_ENABLE = 1  # Value for enabling the torque
    TORQUE_DISABLE = 0  # Value for disabling the torque
    DXL_MINIMUM_POSITION_VALUE = 10  # Dynamixel will rotate between this value
    DXL_MAXIMUM_POSITION_VALUE = 1023  # 4000            # and this value (note that the Dynamixel would not move when the position value is out of movable range. Check e-manual about the range of the Dynamixel you use.)
    DXL_MOVING_STATUS_THRESHOLD = 20  # Dynamixel moving status threshold

    index = 0
    dxl_goal_position = [DXL_MINIMUM_POSITION_VALUE, DXL_MAXIMUM_POSITION_VALUE]  # Goal position
    portHandler = dynamixel_sdk.PortHandler(DEVICENAME)
    packetHandler = dynamixel_sdk.PacketHandler(PROTOCOL_VERSION)
    if portHandler.openPort():
        print("Succeeded to open the port")
    else:
        print("Failed to open the port")
        print("Press any key to terminate...")
        getch()
        quit()
    if portHandler.setBaudRate(BAUDRATE):
        print("Succeeded to change the baudrate")
    else:
        print("Failed to change the baudrate")
        print("Press any key to terminate...")
        getch()
        quit()

    # Enable Dynamixel Torque
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_MX_TORQUE_ENABLE, TORQUE_ENABLE)
    if dxl_comm_result != dynamixel_sdk.COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
    else:
        print("Dynamixel has been successfully connected")

    while 1:
        print("Press any key to continue! (or press ESC to quit!)")
        if getch() == chr(0x1b):
            break

        # Write goal position
        dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, DXL_ID, ADDR_MX_GOAL_POSITION,
                                                                  dxl_goal_position[index])
        if dxl_comm_result != dynamixel_sdk.COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))

        while 1:
            # Read present position
            dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read2ByteTxRx(portHandler, DXL_ID,
                                                                                           ADDR_MX_PRESENT_POSITION)
            if dxl_comm_result != dynamixel_sdk.COMM_SUCCESS:
                print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
                print("%s" % packetHandler.getRxPacketError(dxl_error))

            print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (DXL_ID, dxl_goal_position[index], dxl_present_position))

            if not abs(dxl_goal_position[index] - dxl_present_position) > DXL_MOVING_STATUS_THRESHOLD:
                break

        # Change goal position
        if index == 0:
            index = 1
        else:
            index = 0

    # Disable Dynamixel Torque
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_MX_TORQUE_ENABLE,
                                                              TORQUE_DISABLE)
    if dxl_comm_result != dynamixel_sdk.COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))

    # Close port
    portHandler.closePort()


@app.route('/')
def getdata():
    motor()
    v = "Assembly Container RUnning , Now you can test Other containers using their End Points"
    return v


@app.route('/test')
def test():
    print('In Assembly Container routing')
    r = requests.get('http://SensorContainer:5000')
    response = r.json()
    return 'Response from Sensor Container : {}'.format(response)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
