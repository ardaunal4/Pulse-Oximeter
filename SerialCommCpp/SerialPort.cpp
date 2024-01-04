#include "SerialPort.h"

SerialPort::SerialPort(char* portName) {
	errors = 0;
	status = { 0 };
	connected = false;

	// Create & open the COM I/O device. This returns a handle to the COM device
	handleToCOM = CreateFileA(static_cast<LPCSTR>(portName), GENERIC_READ | GENERIC_WRITE,
		0, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);

	DWORD errMsg = GetLastError();

	if (errMsg == 2) {
		printf("Plug the device/n");
	}
	else if (errMsg == 5) {
		printf("Another app is already using the device\n");
	}

	else if (errMsg == 0) {
		DCB dcbSerialParameters = { 0 };

		if (!GetCommState(handleToCOM, &dcbSerialParameters)){
			printf("failed to get current serial parameters.");
		}
		else {
			dcbSerialParameters.BaudRate = CBR_115200;
			dcbSerialParameters.ByteSize = 8;
			dcbSerialParameters.StopBits = ONESTOPBIT;
			dcbSerialParameters.Parity = NOPARITY;
			dcbSerialParameters.fDtrControl = DTR_CONTROL_ENABLE;

			if (!SetCommState(handleToCOM, &dcbSerialParameters))
			{
				printf("Alert: could not set Serial port parameters\n");
			}
			else {
				connected = true;
				PurgeComm(handleToCOM, PURGE_RXCLEAR | PURGE_TXCLEAR);
				Sleep(WAIT_TIME);
			}
		}
	}
}
SerialPort::~SerialPort() {
	if (connected == true) {
		connected = false;
		CloseHandle(handleToCOM);
	}
}
int SerialPort::ReadSerialPort(char* buffer, unsigned int buf_size) 
{
	DWORD bytesRead;
	unsigned int toRead = 0;

	ClearCommError(handleToCOM, &errors, &status);

	if (status.cbInQue > 0) 
	{
		if (status.cbInQue > buf_size) 
		{
			toRead = buf_size;
		}
		else toRead = status.cbInQue;
	}

	if (ReadFile(handleToCOM, buffer, toRead, &bytesRead, NULL))
	{
		return bytesRead;
	}

	return 0;
}
bool SerialPort::WriteSerialPort(char* buffer, unsigned int buf_size) {
	
	DWORD bytesSend;

	if (!WriteFile(handleToCOM, (void*)buffer, buf_size, &bytesSend, 0))
	{
		ClearCommError(handleToCOM, &this->errors, &this->status);
		return false;
	}

	return true;
}
bool SerialPort::isConnected() {
	return connected;
}