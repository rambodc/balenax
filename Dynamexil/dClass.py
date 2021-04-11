from __future__ import print_function
import os, sys
import dynamixel_sdk

#

class dClass:

    def __init__(self):
        # Control table address
        self.ADDR_MX_TORQUE_ENABLE = 24
        self.ADDR_MX_GOAL_POSITION = 30
        self.ADDR_MX_PRESENT_POSITION = 36
        self.ADDR_LED
        # Protocol version
        self.PROTOCOL_VERSION = 1.0

        # Default setting
        self.DXL_ID = 1
        self.BAUDRATE = 1000000
        self.DEVICENAME = '/dev/ttyUSB0'

        self.TORQUE_ENABLE = 1
        self.TORQUE_DISABLE = 0
        self.DXL_MINIMUM_POSITION_VALUE = 10
        self.DXL_MAXIMUM_POSITION_VALUE = 1023
        self.DXL_MOVING_STATUS_THRESHOLD = 20
        self.temp_pos = 0
        self.index = 0
        self.dxl_goal_position = [self.DXL_MINIMUM_POSITION_VALUE, self.DXL_MAXIMUM_POSITION_VALUE]
        self.portHandler = dynamixel_sdk.PortHandler(self.DEVICENAME)
        self.packetHandler = dynamixel_sdk.PacketHandler(self.PROTOCOL_VERSION)
        if self.portHandler.openPort():
            print("Succeeded to open the port")
        else:
            print("Failed to open the port")
            quit()
        if self.portHandler.setBaudRate(self.BAUDRATE):
            print("Succeeded to change the baudrate")
        else:
            print("Failed to change the baudrate")
            quit()

        # Enable Dynamixel Torque
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, self.DXL_ID,
                                                                       self.ADDR_MX_TORQUE_ENABLE, self.TORQUE_ENABLE)
        if dxl_comm_result != dynamixel_sdk.COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(dxl_error))
        else:
            print("Dynamixel has been successfully connected")

    def run_motor(self, pos):
        dxl_comm_result, dxl_error = self.packetHandler.write2ByteTxRx(self.portHandler, self.DXL_ID,
                                                                       self.ADDR_MX_GOAL_POSITION, pos)
        if dxl_comm_result != dynamixel_sdk.COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(dxl_error))
        while 1:
            # Read present position
            dxl_present_position, dxl_comm_result, dxl_error = self.packetHandler.read2ByteTxRx(self.portHandler, self.DXL_ID, self.ADDR_MX_PRESENT_POSITION)
            if dxl_comm_result != dynamixel_sdk.COMM_SUCCESS:
                print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
                print("%s" % self.packetHandler.getRxPacketError(dxl_error))

            print("[ID:%03d] GoalPos:%03d  PresPos:%03d" % (self.DXL_ID, pos, dxl_present_position))

            if not abs(pos - dxl_present_position) > self.DXL_MOVING_STATUS_THRESHOLD:
                break

    def close_motor(self):
        self.portHandler.closePort()
        pass
