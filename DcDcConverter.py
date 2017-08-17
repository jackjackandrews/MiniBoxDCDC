# -*- coding: utf-8 -*-
"""
@package DcDcConverter
@date Created on 29 Jun 2017

@author Jack Andrews <jackjackandrews2@gmail.com>

@brief Module to communicate with DC-DC converters from Mini-Box.com
"""

import os
import logging

from time import sleep, monotonic
from ctypes import *

##@cond
logger = logging.getLogger(__name__)

logger.debug("DcDcConverter module imported")

if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s\t-\t %(name)s\t- %(message)s', level=logging.NOTSET)

try:
    module_path = os.path.dirname(__file__)
    DCDCUsbLib = cdll.LoadLibrary(module_path + '\\DLL\\DCDCUsbLib.dll')
    logger.info("DCDCUsbLib DLL loaded successfully")
    logger.debug("Resource handle: {}".format(DCDCUsbLib))
except OSError as err:
    logger.error("DCDCUsbLib DLL could not be loaded")
    logger.error("Could not import DcDcConverter module")
    raise err
##@endcond

class DcDcConverter(object):
    
    def __init__(self, devcount, timer, connectiontimeout):
        """Initialisation function for the class each time it is called.
        
            @param devcount  number of device to be opened
            @param timer period (seconds) for API data refresh rate
            @param connectiontimeout how long to keep trying to connect if connection fails first time (seconds)
            
            @see OpenDevice
            @see OpenDeviceByCnt
        
        """
        
        ##@cond 
        self.DCDCUsbLib = DCDCUsbLib
        
        self._setResTypes(self.DCDCUsbLib)
        self._setArgsTypes(self.DCDCUsbLib)
           
        self.devcount = devcount
        self.timer = timer * 1000
        self.connectiontimeout = connectiontimeout
        
        connection_status = self.OpenDeviceByCnt(self.devcount, self.timer)
        
        if connection_status == 1:
            pass
        elif connection_status == 0 :
            logger.info("No DC-DC converter found, trying again for {} seconds".format(connectiontimeout))
            timeout = monotonic() + connectiontimeout
            
            while monotonic() < timeout:
                connection_status = self.GetConnected()
                if connection_status == 1:
                    break
                else:
                    pass
                
        try:
            if connection_status == 1:
                logger.info("Connected to DC-DC converter with devcount: {}".format(devcount))
                
                dev_path = create_string_buffer(b'\00', size=1024)
                self.GetDevicePath(dev_path)
                logger.debug("Device path: {}".format(dev_path.value.decode('UTF-8')))

                sleep(timer)     #Wait for first API refresh otherwise get/set commands might fail
            else:
                raise Exception
        except Exception as err:
            logger.error("No DC-DC converter found; closing device")
            self.CloseDevice()  
            raise err
        ##@endcond
        
        
    def _setResTypes(self, dcdc_object):
        """Set the return types for the dcdc converter object.
        
        This is necessary to avoid passing incorrect data types to the DCDCUsbLib functions, and
        saves having to cast arguments when functions are called.
        
        @param dcdc_object object of type DCDCUsbLib
        """
        #Device initialisation commands
        dcdc_object.dcdcOpenDevice.restype = c_ubyte
        dcdc_object.dcdcOpenDeviceByCnt.restype = c_ubyte
        dcdc_object.dcdcGetDevicePath.restype = None
        dcdc_object.dcdcCloseDevice.restype = None
        
        #Get commands
        dcdc_object.dcdcGetConnected.restype = c_ubyte
        dcdc_object.dcdcGetTimeCfg.restype = c_ubyte
        dcdc_object.dcdcGetVoltageCfg.restype = c_ubyte
        dcdc_object.dcdcGetMode.restype = c_ubyte
        dcdc_object.dcdcGetState.restype = c_ubyte
        dcdc_object.dcdcGetVin.restype = c_float
        dcdc_object.dcdcGetVIgn.restype = c_float
        dcdc_object.dcdcGetVOut.restype = c_float
        dcdc_object.dcdcGetEnabledPowerSwitch.restype = c_ubyte
        dcdc_object.dcdcGetEnabledOutput.restype = c_ubyte
        dcdc_object.dcdcGetEnabledAuxVOut.restype = c_ubyte
        dcdc_object.dcdcGetFlagsStatus1.restype = c_ubyte
        dcdc_object.dcdcGetFlagsStatus2.restype = c_ubyte
        dcdc_object.dcdcGetFlagsVoltage.restype = c_ubyte
        dcdc_object.dcdcGetFlagsTimer.restype = c_ubyte
        dcdc_object.dcdcGetFlashPointer.restype = c_ubyte
        dcdc_object.dcdcGetTimerWait.restype = c_uint
        dcdc_object.dcdcGetTimerVout.restype = c_uint
        dcdc_object.dcdcGetTimerVAux.restype = c_uint
        dcdc_object.dcdcGetTimerPwSwitch.restype = c_uint
        dcdc_object.dcdcGetTimerOffDelay.restype = c_uint
        dcdc_object.dcdcGetTimerHardOff.restype = c_uint
        dcdc_object.dcdcGetVersionMajor.restype = c_ubyte
        dcdc_object.dcdcGetVersionMinor.restype = c_ubyte
        
        #Set commands
        dcdc_object.dcdcSetEnabledAuxVOut.restype = None
        dcdc_object.dcdcSetEnabledPowerSwitch.restype = None
        dcdc_object.dcdcSetEnabledOutput.restype = None
        dcdc_object.dcdcIncDecVOutVolatile.restype = None
        dcdc_object.dcdcSetVOutVolatile.restype = None
        dcdc_object.dcdcLoadFlashValues.restype = None
        dcdc_object.dcdcGetLoadState.restype = c_ubyte
        dcdc_object.dcdcGetMaxVariableCnt.restype = c_uint
        dcdc_object.dcdcGetVariableData.restype = c_ubyte
        dcdc_object.dcdcSetVariableData.restype = c_ubyte
        dcdc_object.dcdcSaveFlashValues.restype = None
        
    def _setArgsTypes(self, dcdc_object):
        """Set the argument types for the dcdc converter object.
        
        @param dcdc_object object of type DCDCUsbLib
        """        
        #Device initialisation commands
        dcdc_object.dcdcOpenDevice.argtypes = [c_uint]
        dcdc_object.dcdcOpenDeviceByCnt.argtypes = [c_uint, c_uint]
        dcdc_object.dcdcGetDevicePath.argtypes = [c_char_p]
        dcdc_object.dcdcCloseDevice.argtypes = None
        
        #Get commands
        dcdc_object.dcdcGetConnected.argtypes = None
        dcdc_object.dcdcGetTimeCfg.argtypes = None
        dcdc_object.dcdcGetVoltageCfg.argtypes = None
        dcdc_object.dcdcGetMode.argtypes = None
        dcdc_object.dcdcGetState.argtypes = None
        dcdc_object.dcdcGetVin.argtypes = None
        dcdc_object.dcdcGetVIgn.argtypes = None
        dcdc_object.dcdcGetVOut.argtypes = None
        dcdc_object.dcdcGetEnabledPowerSwitch.argtypes = None
        dcdc_object.dcdcGetEnabledOutput.argtypes = None
        dcdc_object.dcdcGetEnabledAuxVOut.argtypes = None
        dcdc_object.dcdcGetFlagsStatus1.argtypes = None
        dcdc_object.dcdcGetFlagsStatus2.argtypes = None
        dcdc_object.dcdcGetFlagsVoltage.argtypes = None
        dcdc_object.dcdcGetFlagsTimer.argtypes = None
        dcdc_object.dcdcGetFlashPointer.argtypes = None
        dcdc_object.dcdcGetTimerWait.argtypes = None
        dcdc_object.dcdcGetTimerVout.argtypes = None
        dcdc_object.dcdcGetTimerVAux.argtypes = None
        dcdc_object.dcdcGetTimerPwSwitch.argtypes = None
        dcdc_object.dcdcGetTimerOffDelay.argtypes = None
        dcdc_object.dcdcGetTimerHardOff.argtypes = None
        dcdc_object.dcdcGetVersionMajor.argtypes = None
        dcdc_object.dcdcGetVersionMinor.argtypes = None
        
        #Set commands
        dcdc_object.dcdcSetEnabledAuxVOut.argtypes = [c_ubyte]
        dcdc_object.dcdcSetEnabledPowerSwitch.argtypes = [c_ubyte]
        dcdc_object.dcdcSetEnabledOutput.argtypes = [c_ubyte]
        dcdc_object.dcdcIncDecVOutVolatile.argtypes = [c_ubyte]
        dcdc_object.dcdcSetVOutVolatile.argtypes = [c_float]
        dcdc_object.dcdcLoadFlashValues.argtypes = None
        dcdc_object.dcdcGetLoadState.argtypes = None
        dcdc_object.dcdcGetMaxVariableCnt.argtypes = None
        dcdc_object.dcdcGetVariableData.argtypes = [c_uint, c_char_p, c_char_p, c_char_p, c_char_p]
        dcdc_object.dcdcSetVariableData.argtypes = [c_uint, c_char_p]
        dcdc_object.dcdcSaveFlashValues.argtypes = None
         
    def OpenDevice(self, timer):
        """Opens first DCDCUsb found on USB
            
            Notes on timer parameter: Smaller values are forcing the API to refresh the data requested with the rest of the functions 
            faster but also will cause data congestion. Recommended values are between 1000-10000 to have a 1-10 second refresh rate.
            
            After unsuccesfull dcdcOpenDevice call if there is no dcdcCloseDevice call
            the API will wait to the first DCDCUsb plugged in and will connect automatically to it!
        
            @param timer milisecond period for data refresh rate
            
            @return 1 on success, 0 on fail
        """
        return self.DCDCUsbLib.dcdcOpenDevice(timer)
    
    def OpenDeviceByCnt(self, devcount, timer):
        """Opens devcount device (1 - first device, 2 - second...etc.)
        
            @param devcount number of device to be opened
            @param timer same as OpenDevice(timer)
        
            @see OpenDevice
        
            @return 1 on success, 0 on fail        
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
            
            @param path c-type pointer to char, minimum length 1024
        """
        
        self.DCDCUsbLib.dcdcGetDevicePath(path)
                
    def CloseDevice(self):
        """Close the opened DCDCUsb device
        """
        self.DCDCUsbLib.dcdcCloseDevice()    
      
    def GetConnected(self):
        """Get connection state of the DCDCUsb
        
            @return 1 on connected state, 0 on not connected        
        """
        return self.DCDCUsbLib.dcdcGetConnected()
    
    def GetTimeCfg(self):
        """Get state variable: Timer Config
        
            @return State variable: Timer config
        """
        return self.DCDCUsbLib.dcdcGetTimeCfg()
    
    def GetVoltageCfg(self):
        """Get state variable: Voltage Config
        
            @return State variable: Voltage config
        """
        return self.DCDCUsbLib.dcdcGetVoltageCfg()
    
    def GetMode(self):
        """Get state variable: Mode
        
            @return State variable: Mode (0=Dumb, 1=Automotive, 2=Script, 3=UPS, Other values=ERROR)
        """
        return self.DCDCUsbLib.dcdcGetMode()
    
    def GetState(self):
        """Get state variable: DCDC State
        
            @return State variable: DCDC State
        """
        return self.DCDCUsbLib.dcdcGetState()
    
    def GetVin(self):
        """Get state variable: Voltage In
        
            @return State variable: Voltage In
        """
        return self.DCDCUsbLib.dcdcGetVin()
    
    def GetVIgn(self):
        """Get state variable: Voltage Ignition
        
            @return State variable: Voltage Ignition
        """
        return self.DCDCUsbLib.dcdcGetVIgn()
    
    def GetVOut(self):
        """Get state variable: Voltage Out
        
            @return State variable: Voltage Out
        """
        return self.DCDCUsbLib.dcdcGetVOut()
    
    def GetEnabledPowerSwitch(self):
        """Get state variable: Power Switch Enabled
        
            @return State variable: Power Switch Enabled
        """
        return self.DCDCUsbLib.dcdcGetEnabledPowerSwitch()
    
    def GetEnabledOutput(self):
        """Get state variable: Output Enabled
        
            @return State variable: Output Enabled
        """    
        return self.DCDCUsbLib.dcdcGetEnabledOutput()
    
    def GetEnabledAuxVOut(self):
        """Get state variable: Auxiliary Output Enabled
        
            @return State variable: Auxiliary Output Enabled
        """
        return self.DCDCUsbLib.dcdcGetEnabledAuxVOut()
    
    def GetFlagsStatus1(self):
        """Get state variable: Status 1 flags
        
            @return State variable: Status 1 flags
        """
        return self.DCDCUsbLib.dcdcGetFlagsStatus1()
    
    def GetFlagsStatus2(self):
        """Get state variable: Status 2 flags
        
            @return State variable: Status 2 flags
        """
        return self.DCDCUsbLib.dcdcGetFlagsStatus2()
    
    def GetFlagsVoltage(self):
        """Get state variable: Voltage flags
        
            @return State variable: Voltage flags
        """
        return self.DCDCUsbLib.dcdcGetFlagsVoltage()
    
    def GetFlagsTimer(self):
        """Get state variable: Timer flags
        
            @return State variable: Timer flags        
        """
        return self.DCDCUsbLib.dcdcGetFlagsTimer()
    
    def GetFlashPointer(self):
        """Get state variable: Flash pointer
        
            @return State variable: Flash pointer
        """
        return self.DCDCUsbLib.dcdcGetFlashPointer()
    
    def GetTimerWait(self):
        """Get state variable: Wait timer
        
            @return State variable: Wait timer
        """
        return self.DCDCUsbLib.dcdcGetTimerWait()
    
    def GetTimerVout(self):
        """Get state variable: Voltage Out Timer
        
            @return State variable: Voltage Out Timer
        """
        return self.DCDCUsbLib.dcdcGetTimerVout()
    
    def GetTimerVAux(self):
        """Get state variable: Voltage Auxiliary Timer
        
            @return State variable: Voltage Auxiliary Timer
        """
        return self.DCDCUsbLib.dcdcGetTimerVAux()
    
    def GetTimerPwSwitch(self):
        """Get state variable: Power Switch Timer
        
            @return State variable: Power Switch Timer
        """        
        return self.DCDCUsbLib.dcdcGetTimerPwSwitch()
    
    def GetTimerOffDelay(self):
        """Get state variable: Off Delay Timer
        
            @return State variable: Off Delay Timer
        """
        return self.DCDCUsbLib.dcdcGetTimerOffDelay()
    
    def GetTimerHardOff(self):
        """Get state variable: Hard Off Timer
        
            @return State variable: Hard Off Timer
        """
        return self.DCDCUsbLib.dcdcGetTimerHardOff()
    
    def GetVersionMajor(self):
        """Get firmware version major number
        
            @return Firmware version major number
        """
        return self.DCDCUsbLib.dcdcGetVersionMajor()
    
    def GetVersionMinor(self):
        """Get firmware version minor number
        
            @return Firmware version minor number
        """
        return self.DCDCUsbLib.dcdcGetVersionMinor()
    
    def GetVersion(self):
        """Get firmware version (major and minor)
        
            @return Firmware version (major and minor) as a string
        """
        fw_ver_major = self.GetVersionMajor()
        fw_ver_minor = self.GetVersionMinor()
        return str(fw_ver_major) + '.' + str(fw_ver_minor)
    
    def SetEnabledAuxVOut(self, on):
        """Set Auxiliary Output Enable
        
            @param on on/off
        """
        self.DCDCUsbLib.dcdcSetEnabledAuxVOut(on)
    
    def SetEnabledPowerSwitch(self, on):
        """Set Power Switch Enable
        
            @param on on/off
        """
        self.DCDCUsbLib.dcdcSetEnabledPowerSwitch(on)
        
    def SetEnabledOutput(self, on):
        """Set Output Enable
        
            @param on on/off
        """
        self.DCDCUsbLib.dcdcSetEnabledOutput(on)
        
    def IncDecVOutVolatile(self, inc):
        """Increase or decrease VOut
        
            This value will be reset together with DCDCUsb Reset.
            For permanent values set the flash value and restart the unit.
            
            @param inc inc/dec
        """
        self.DCDCUsbLib.dcdcIncDecVOutVolatile(inc)
        
    def SetVOutVolatile(self, vout):
        """Set VOut
        
            This value will be reset together with DCDCUsb Reset.
            For permanent values set the flash value and restart the unit.
            
            @param vout voltage
        """
        self.DCDCUsbLib.dcdcSetVOutVolatile(vout)
        
    def LoadFlashValues(self):
        """Start loading flash values.
        
            Load state is indicated by GetLoadState function.
            
            @see GetLoadState
        """
        self.DCDCUsbLib.dcdcLoadFlashValues()
        
    def GetLoadState(self):
        """Get loading state of flash variables. 
        
            @return Loading state, 100 on success
        """
        return self.DCDCUsbLib.dcdcGetLoadState()
    
    def GetMaxVariableCnt(self):
        """Get maximum count of variables in DCDCUsb
        
            @return Maximum count of variables in DCDCUsb
        """
        return self.DCDCUsbLib.dcdcGetMaxVariableCnt()
    
    def GetVariableData(self, cnt, name, value, unit, comment):
        """Get the data related to a variable.
            
            The values will be written in name, value, unit and comment pointers 
            so ensure they have enough bytes allocated. Recommended length of buffers are 256 for name, value, unit and 1024 for comment.
            
            Will return valid data in value only after first succesfull LoadFlashValues (100%).
            
            For details on passing pointers in Python see GetDevicePath function.
            
            @see GetDevicePath
            @see LoadFlashValues
        
            @param cnt variable id
            @param name variable short name
            @param value variable value
            @param unit measurement unit
            @param comment long comment
            
            @return 1 if the variable does exist
        """
        return self.DCDCUsbLib.dcdcGetVariableData(cnt, name, value, unit, comment)
    
    def SetVariableData(self, cnt, value):
        """Set one data value in PC copy of DCDCUsb Variables.
        
            The format for the variables can be different - for list of formats see either a complete listing of values using 
            GetVariableData or the DCDCUsb Windows software/Settings tab.
            
            This function should be called only after a first succesfull call to LoadFlashValues otherwise nothing will be saved.
            
            For details on passing pointers in Python see GetDevicePath function.
            
            @see GetDevicePath
            @see GetVariableData
            @see LoadFlashValues
            
            @param cnt variable id
            @param value variable value
            
            @return unknown
            
            @todo need to test function to see what value is returned upon success/failure
        """
        return self.DCDCUsbLib.dcdcSetVariableData(cnt, value)
    
    def SaveFlashValues(self):
        """Save the full flash to DCDCUsb.
        
            There can be multiple calls of SetVariableData before one SaveFlashValues.
            Since the flash in the DCDCUsb has a limit of 10k writes we do not recommend 
            functionality which writes the flash many times.

            This function should be called only after first succesfull dcdcLoadFlashValues otherwise nothing will be saved.        
        """
        self.DCDCUsbLib.dcdcSaveFlashValues()


##@cond
if __name__ == '__main__':
      
    try:
        Converter = DcDcConverter(1, 1, 5)
    except Exception as err:
        logger.info("Program terminated")
        raise err
    
    fw_version = Converter.GetVersion()    
    
    logger.info("FW version: {}".format(fw_version))
    
    logger.info("Program terminated")
    
    exit()
##@endcond