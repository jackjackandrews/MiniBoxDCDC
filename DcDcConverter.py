# -*- coding: utf-8 -*-
"""
@date: Created on 29 Jun 2017

@author: Jack Andrews
@contact: jackjackandrews2@gmail.com
"""

import os
import logging

from time import sleep, monotonic
from ctypes import *

logger = logging.getLogger(__name__)

logger.debug("DcDcConverter module imported")

if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s - %(message)s', level=logging.NOTSET)

try:
    module_path = os.path.dirname(__file__)
    DCDCUsbLib = cdll.LoadLibrary(module_path + '\\DLL\\DCDCUsbLib.dll')
    logger.info("DCDCUsbLib DLL loaded successfully")
    logger.debug("Resource handle: {}".format(DCDCUsbLib))
except OSError as err:
    logger.error("DCDCUsbLib DLL could not be loaded")
    logger.error("Could not import DcDcConverter module")
    raise err

class DcDcConverter:
    """Class to communicate with multiple DCDC-USB-200 DC-DC converters from Mini-Box.com.

        Uses DCDCUsbLib.dll provided by Mini-Box in their API to communicate with converters over USB interface.
    """

    def __init__(self, devcount, timer, connectiontimeout):
        """Initialisation function for the class each time it is called.
        
            @param devcount:  number of device to be opened
            @param timer: period (seconds) for API data refresh rate
            @param connectiontimeout: how long to keep trying to connect if connection fails first time (seconds)
            
            @see: OpenDevice
            @see: OpenDeviceByCnt
        
        """
        
        self.DCDCUsbLib = DCDCUsbLib
        
        SetResTypes(self.DCDCUsbLib)
        SetArgsTypes(self.DCDCUsbLib)
            
        self.devcount = devcount
        self.timer = timer * 1000
        self.connectiontimeout = connectiontimeout
        
        connection_status = self.OpenDeviceByCnt(self.devcount, self.timer)
        
        if connection_status == 1:
            pass
        elif connection_status == 0 :
            logger.info("No DCDC-USB-200 found, trying again for {} seconds".format(connectiontimeout))
            timeout = monotonic() + connectiontimeout
            
            while monotonic() < timeout:
                connection_status = self.GetConnected()
                if connection_status == 1:
                    break
                else:
                    pass
                
        try:
            if connection_status == 1:
                logger.info("Successfully connected to DCDC-USB-200 with devcount: {}".format(devcount))
                
                dev_path = create_string_buffer(b'\00', size=1024)
                self.GetDevicePath(dev_path)
                logger.debug("Device path: {}".format(dev_path.value.decode('UTF-8')))

                sleep(timer + 1)     #Wait for first API refresh otherwise get/set commands might fail
            else:
                raise Exception
        except Exception as err:
            logger.error("No DCDC-USB-200 found; closing device")
            self.CloseDevice()  
            raise err
        
        self.connection_status = self.GetConnected()
        
    #Device initialisation commands     
    def OpenDevice(self, timer):
        """Opens first DCDCUsb found on USB
            
            Notes on timer parameter: Smaller values are forcing the API to refresh the data requested with the rest of the functions 
            faster but also will cause data congestion. Recommended values are between 1000-10000 to have a 1-10 second refresh rate.
            
            IMPORTANT: after unsuccesfull dcdcOpenDevice call if there is no dcdcCloseDevice call
            the API will wait to the first DCDCUsb plugged in and will connect automatically to it!
        
            @param timer: milisecond period for data refresh rate
            
            @return: 1 on success, 0 on fail
        """
        return self.DCDCUsbLib.dcdcOpenDevice(timer)
    
    def OpenDeviceByCnt(self, devcount, timer):
        """Opens devcount device (1 - first device, 2 - second ... etc.)
        
            @param devcount: number of device to be opened
            @param timer: same as OpenDevice(timer)
        
            @see: OpenDevice
        
            @return: 1 on success, 0 on fail        
        """
        return self.DCDCUsbLib.dcdcOpenDeviceByCnt(devcount, timer)
    
    def GetDevicePath(self, path):
        """Get opened device path
            
            Pointer to char can be created using standard Python method
                
                dev_path = create_string_buffer(init, size)
                
            Then pass in dev_path to the method.
            
            Path can be decoded using standard Python method
            
                dev_path.value.decode('UTF-8')
                
            Assuming UTF-8 encoding.
            
            @param path: c-type pointer to char, minimum length 1024
        """
        
        self.DCDCUsbLib.dcdcGetDevicePath(path)
                
    def CloseDevice(self):
        """Close the opened DCDCUsb device
        """
        self.DCDCUsbLib.dcdcCloseDevice()    
    
    #Get commands    
    def GetConnected(self):
        """Get connection state of the DCDCUsb
        
            @return: 1 on connected state, 0 on not connected        
        """
        return self.DCDCUsbLib.dcdcGetConnected()
    
    def GetTimeCfg(self):
        """Get state variable: Timer Config
        
            @return: State variable: Timer config
        """
        return self.DCDCUsbLib.dcdcGetTimeCfg()
    
    def GetVoltageCfg(self):
        """Get state variable: Voltage Config
        
            @return: State variable: Voltage config
        """
        return self.DCDCUsbLib.dcdcGetVoltageCfg()
    
    def GetMode(self):
        """Get state variable: Mode
        
            @return: State variable: Mode (0=Dumb, 1=Automotive, 2=Script, 3=UPS, Other values=ERROR)
        """
        return self.DCDCUsbLib.dcdcGetMode()
    
    def GetState(self):
        """Get state variable: DCDC State
        
            @return: State variable: DCDC State
        """
        return self.DCDCUsbLib.dcdcGetState()
    
    def GetVin(self):
        """Get state variable: Voltage In
        
            @return: State variable: Voltage In
        """
        return self.DCDCUsbLib.dcdcGetVin()
    
    def GetVIgn(self):
        """Get state variable: Voltage Ignition
        
            @return: State variable: Voltage Ignition
        """
        return self.DCDCUsbLib.dcdcGetVIgn()
    
    def GetVOut(self):
        """Get state variable: Voltage Out
        
            @return: State variable: Voltage Out
        """
        return self.DCDCUsbLib.dcdcGetVOut()
    
    def GetEnabledPowerSwitch(self):
        """Get state variable: Power Switch Enabled
        
            @return: State variable: Power Switch Enabled
        """
        return self.DCDCUsbLib.dcdcGetEnabledPowerSwitch()
    
    def GetEnabledOutput(self):
        """Get state variable: Output Enabled
        
            @return: State variable: Output Enabled
        """    
        return self.DCDCUsbLib.dcdcGetEnabledOutput()
    
    def GetEnabledAuxVOut(self):
        """Get state variable: Auxiliary Output Enabled
        
            @return: State variable: Auxiliary Output Enabled
        """
        return self.DCDCUsbLib.dcdcGetEnabledAuxVOut()
    
    def GetFlagsStatus1(self):
        """Get state variable: Status 1 flags
        
            @return: State variable: Status 1 flags
        """
        return self.DCDCUsbLib.dcdcGetFlagsStatus1()
    
    def GetFlagsStatus2(self):
        """Get state variable: Status 2 flags
        
            @return: State variable: Status 2 flags
        """
        return self.DCDCUsbLib.dcdcGetFlagsStatus2()
    
    def GetFlagsVoltage(self):
        """Get state variable: Voltage flags
        
            @return: State variable: Voltage flags
        """
        return self.DCDCUsbLib.dcdcGetFlagsVoltage()
    
    def GetFlagsTimer(self):
        """Get state variable: Timer flags
        
            @return: State variable: Timer flags        
        """
        return self.DCDCUsbLib.dcdcGetFlagsTimer()
    
    def GetFlashPointer(self):
        """Get state variable: Flash pointer
        
            @return: State variable: Flash pointer
        """
        return self.DCDCUsbLib.dcdcGetFlashPointer()
    
    def GetTimerWait(self):
        """Get state variable: Wait timer
        
            @return: State variable: Wait timer
        """
        return self.DCDCUsbLib.dcdcGetTimerWait()
    
    def GetTimerVout(self):
        """Get state variable: Voltage Out Timer
        
            @return: State variable: Voltage Out Timer
        """
        return self.DCDCUsbLib.dcdcGetTimerVout()
    
    def GetTimerVAux(self):
        """Get state variable: Voltage Auxiliary Timer
        
            @return: State variable: Voltage Auxiliary Timer
        """
        return self.DCDCUsbLib.dcdcGetTimerVAux()
    
    def GetTimerPwSwitch(self):
        """Get state variable: Power Switch Timer
        
            @return: State variable: Power Switch Timer
        """        
        return self.DCDCUsbLib.dcdcGetTimerPwSwitch()
    
    def GetTimerOffDelay(self):
        """Get state variable: Off Delay Timer
        
            @return: State variable: Off Delay Timer
        """
        return self.DCDCUsbLib.dcdcGetTimerOffDelay()
    
    def GetTimerHardOff(self):
        """Get state variable: Hard Off Timer
        
            @return: State variable: Hard Off Timer
        """
        return self.DCDCUsbLib.dcdcGetTimerHardOff()
    
    def GetVersionMajor(self):
        """Get firmware version major number
        
            @return: Firmware version major number
        """
        return self.DCDCUsbLib.dcdcGetVersionMajor()
    
    def GetVersionMinor(self):
        """Get firmware version minor number
        
            @return: Firmware version minor number
        """
        return self.DCDCUsbLib.dcdcGetVersionMinor()
    
    def GetVersion(self):
        """Get firmware version (major and minor)
        
            @return: Firmware version (major and minor) as a string
        """
        fw_ver_major = self.GetVersionMajor()
        fw_ver_minor = self.GetVersionMinor()
        return str(fw_ver_major) + '.' + str(fw_ver_minor)
    
    #Set commands
    def SetEnabledAuxVOut(self, on):
        """Set Auxiliary Output Enable
        
            @param on: on/off
        """
        self.DCDCUsbLib.dcdcSetEnabledAuxVOut(on)
    
    def SetEnabledPowerSwitch(self, on):
        """Set Power Switch Enable
        
            @param on: on/off
        """
        self.DCDCUsbLib.dcdcSetEnabledPowerSwitch(on)
        
    def SetEnabledOutput(self, on):
        """Set Output Enable
        
            @param on: on/off
        """
        self.DCDCUsbLib.dcdcSetEnabledOutput(on)
        
    def IncDecVOutVolatile(self, inc):
        """Increase or decrease VOut
        
            IMPORTANT:this value will be reset together with DCDCUsb Reset.
            For permanent values set the flash value and restart the unit.
            
            @param inc: inc/dec
        """
        self.DCDCUsbLib.dcdcIncDecVOutVolatile(inc)
        
    def SetVOutVolatile(self, vout):
        """Set VOut
        
            IMPORTANT:this value will be reset together with DCDCUsb Reset.
            For permanent values set the flash value and restart the unit.
            
            @param vout: voltage
        """
        self.DCDCUsbLib.dcdcSetVOutVolatile(vout)
        
    def LoadFlashValues(self):
        """Start loading flash values.
        
            Load state is indicated by GetLoadState function.
            
            @see: GetLoadState
        """
        self.DCDCUsbLib.dcdcLoadFlashValues()
        
    def GetLoadState(self):
        """Loading state. 100 (%) on success
        
            @return: Loading state
        """
        return self.DCDCUsbLib.dcdcGetLoadState()
    
    def GetMaxVariableCnt(self):
        """Get maximum count of variables in DCDCUsb
        
            @return: Maximum count of variables in DCDCUsb
        """
        return self.DCDCUsbLib.dcdcGetMaxVariableCnt()
    
    def GetVariableData(self, cnt, name, value, unit, comment):
        """Get the data related to a variable.
            
            The values will be written in name, value, unit and comment pointers 
            so ensure they have enough bytes allocated. Recommended length of buffers are 256 for name, value, unit and 1024 for comment.
            IMPORTANT: will return valid data in value only after first succesfull LoadFlashValues (100%).
            
            For details on passing pointers in Python see GetDevicePath function.
            
            @see: GetDevicePath
        
            @param cnt: variable id
            @param name: variable short name
            @param value: variable value
            @param unit: measurement unit
            @param comment: long comment
            
            @return: 1 if the variable does exist
        """
        return self.DCDCUsbLib.dcdcGetVariableData(cnt, name, value, unit, comment)
    
    def SetVariableData(self, cnt, value):
        """Set one data value in PC copy of DCDCUsb Variables.
        
            The format for the variables can be different - for list of formats see either a complete listing of values using 
            GetVariableData or the DCDCUsb Windows software/Settings tab.
            
            IMPORTANT: this function should be called only after first succesfull dcdcLoadFlashValues otherwise nothing will be saved.
            
            For details on passing pointers in Python see GetDevicePath function.
            
            @see: GetDevicePath
            @see: GetVariableData
            
            @param cnt: variable id
            @param value: variable value
            
            @return: unknown
            
            @todo: need to test function to see what value is returned upon success/failure
        """
        return self.DCDCUsbLib.dcdcSetVariableData(cnt, value)
    
    def SaveFlashValues(self):
        """Save the full flash to DCDCUsb.
        
            There can be multiple calls of SetVariableData before one SaveFlashValues.
            Since the flash in the DCDCUsb has a limit of 10k writes we do not recommend 
            functionality which writes the flash many times.

            IMPORTANT: this function should be called only after first succesfull dcdcLoadFlashValues otherwise nothing will be saved.        
        """
        self.DCDCUsbLib.dcdcSaveFlashValues()


class SetResTypes(object):
    """Class containing the return types of all functions in the DCDCUsbLib DLL
    
        This class will set the return types of any object passed to it when it is called.    
    """
    
    def __init__(self, object):
        
        #Device initialisation commands
        object.dcdcOpenDevice.restype = c_ubyte
        object.dcdcOpenDeviceByCnt.restype = c_ubyte
        object.dcdcGetDevicePath.restype = None
        object.dcdcCloseDevice.restype = None
        
        #Get commands
        object.dcdcGetConnected.restype = c_ubyte
        object.dcdcGetTimeCfg.restype = c_ubyte
        object.dcdcGetVoltageCfg.restype = c_ubyte
        object.dcdcGetMode.restype = c_ubyte
        object.dcdcGetState.restype = c_ubyte
        object.dcdcGetVin.restype = c_float
        object.dcdcGetVIgn.restype = c_float
        object.dcdcGetVOut.restype = c_float
        object.dcdcGetEnabledPowerSwitch.restype = c_ubyte
        object.dcdcGetEnabledOutput.restype = c_ubyte
        object.dcdcGetEnabledAuxVOut.restype = c_ubyte
        object.dcdcGetFlagsStatus1.restype = c_ubyte
        object.dcdcGetFlagsStatus2.restype = c_ubyte
        object.dcdcGetFlagsVoltage.restype = c_ubyte
        object.dcdcGetFlagsTimer.restype = c_ubyte
        object.dcdcGetFlashPointer.restype = c_ubyte
        object.dcdcGetTimerWait.restype = c_uint
        object.dcdcGetTimerVout.restype = c_uint
        object.dcdcGetTimerVAux.restype = c_uint
        object.dcdcGetTimerPwSwitch.restype = c_uint
        object.dcdcGetTimerOffDelay.restype = c_uint
        object.dcdcGetTimerHardOff.restype = c_uint
        object.dcdcGetVersionMajor.restype = c_ubyte
        object.dcdcGetVersionMinor.restype = c_ubyte
        
        #Set commands
        object.dcdcSetEnabledAuxVOut.restype = None
        object.dcdcSetEnabledPowerSwitch.restype = None
        object.dcdcSetEnabledOutput.restype = None
        object.dcdcIncDecVOutVolatile.restype = None
        object.dcdcSetVOutVolatile.restype = None
        object.dcdcLoadFlashValues.restype = None
        object.dcdcGetLoadState.restype = c_ubyte
        object.dcdcGetMaxVariableCnt.restype = c_uint
        object.dcdcGetVariableData.restype = c_ubyte
        object.dcdcSetVariableData.restype = c_ubyte
        object.dcdcSaveFlashValues.restype = None

    
class SetArgsTypes(object):
    """Class containing the argument types of all functions in the DCDCUsbLib DLL
    
        This class will set the argument types of any object passed to it when it is called.
        This is necessary to avoid passing incorrect data types to the DCDCUsbLib functions, and
        saves having to cast arguments when functions are called.    
    """
    
    
    def __init__(self, object):
        
        #Device initialisation commands
        object.dcdcOpenDevice.argtypes = [c_uint]
        object.dcdcOpenDeviceByCnt.argtypes = [c_uint, c_uint]
        object.dcdcGetDevicePath.argtypes = [c_char_p]
        object.dcdcCloseDevice.argtypes = None
        
        #Get commands
        object.dcdcGetConnected.argtypes = None
        object.dcdcGetTimeCfg.argtypes = None
        object.dcdcGetVoltageCfg.argtypes = None
        object.dcdcGetMode.argtypes = None
        object.dcdcGetState.argtypes = None
        object.dcdcGetVin.argtypes = None
        object.dcdcGetVIgn.argtypes = None
        object.dcdcGetVOut.argtypes = None
        object.dcdcGetEnabledPowerSwitch.argtypes = None
        object.dcdcGetEnabledOutput.argtypes = None
        object.dcdcGetEnabledAuxVOut.argtypes = None
        object.dcdcGetFlagsStatus1.argtypes = None
        object.dcdcGetFlagsStatus2.argtypes = None
        object.dcdcGetFlagsVoltage.argtypes = None
        object.dcdcGetFlagsTimer.argtypes = None
        object.dcdcGetFlashPointer.argtypes = None
        object.dcdcGetTimerWait.argtypes = None
        object.dcdcGetTimerVout.argtypes = None
        object.dcdcGetTimerVAux.argtypes = None
        object.dcdcGetTimerPwSwitch.argtypes = None
        object.dcdcGetTimerOffDelay.argtypes = None
        object.dcdcGetTimerHardOff.argtypes = None
        object.dcdcGetVersionMajor.argtypes = None
        object.dcdcGetVersionMinor.argtypes = None
        
        #Set commands
        object.dcdcSetEnabledAuxVOut.argtypes = [c_ubyte]
        object.dcdcSetEnabledPowerSwitch.argtypes = [c_ubyte]
        object.dcdcSetEnabledOutput.argtypes = [c_ubyte]
        object.dcdcIncDecVOutVolatile.argtypes = [c_ubyte]
        object.dcdcSetVOutVolatile.argtypes = [c_float]
        object.dcdcLoadFlashValues.argtypes = None
        object.dcdcGetLoadState.argtypes = None
        object.dcdcGetMaxVariableCnt.argtypes = None
        object.dcdcGetVariableData.argtypes = [c_uint, c_char_p, c_char_p, c_char_p, c_char_p]
        object.dcdcSetVariableData.argtypes = [c_uint, c_char_p]
        object.dcdcSaveFlashValues.argtypes = None
 

if __name__ == '__main__':
      
    try:
        Converter = DcDcConverter(1, 1, 5)
    except Exception as err:
        logger.info("Program terminated")
        exit()
    
    fw_version = Converter.GetVersion()    
    
    logger.info("FW version: {}".format(fw_version))
    
    logger.info("Program terminated")
    
    exit()