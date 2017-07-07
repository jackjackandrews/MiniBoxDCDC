# MiniBoxDCDC

This Python module can be used to communicate with a [MiniBox DCDC-USB-200](http://www.mini-box.com/DCDC-USB-200) intelligent DC-DC converter (or other MiniBox converters) over a USB connection. This allows for status monitoring and configuration of paramters of the module.

It uses the Python [`ctypes`](https://docs.python.org/3/library/ctypes.html) module to wrap a Windows DLL in pure Python and allow functions in the DLL to be called.

## How to Use

**Note: this class only works with x86 (32-bit) versions of the Python interpreter - the DCDCUsbLib dll is compiled for 32-bit platforms only.**

1. Ensure you clone the 'DLL' folder along with the DcDcConverter.py class file itself. This folder contains the DCDCUsbLib.dll provided by MiniBox which packages the functions used to communicate with the module. In addition, it also contains some Microsoft Visual C++ 2005 re-distributables which are required by DCDCUsbLib.dll. These can also be installed as standard system libraries by installing the [Microsoft Visual C++ 2005 Redistributable Package](https://www.microsoft.com/en-us/download/details.aspx?id=3387).

    The 'DLL' folder **must** exist in the same directory as the module file - that is where the module looks when it is imported for the first time.

2. Import the module in the Python program which requires it using: `import DcDcConverter` 

    This loads the DLL into memory and makes it available for use by the class when it is initialised.

3. Initialise the class using `ExampleConverterName = DcDcConverter(devcount, timer, timeout)`

    Where:

    * `devcount` is the number of the device you want to connect to - use when multiple DCDC-USB-200s are connected.

    * `timer` is the DCDCUsbLib API refresh rate in **seconds** - ie. how often it refreses the data returned by the `GetXXX()` functions.

    * `timeout` is the time in seconds that the class should carry on trying to detect a device for, if it doesn't detect one at first.

Documentation of available functions is provided within the class itself.

**Note:** If the module is executed by itself (ie. as \_\_main\_\_), it will run a small test program which establishes connection with a DCDC-USB-200 and prints out its Windows device path and firmware version.