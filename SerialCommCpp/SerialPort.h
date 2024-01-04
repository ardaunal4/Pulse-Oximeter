#pragma once
#define WAIT_TIME 100
#define INPUT_DATA_BYTES 8 // 14000\n
#ifdef _DEBUG
	#undef _DEBUG
	#include <python.h>
	#define _DEBUG
#else
	#include <python.h>
#endif

#include <Windows.h>
#include <stdio.h>
#include <stdlib.h>

class SerialPort
{
private:
	HANDLE handleToCOM;
	bool connected;
	COMSTAT status;
	DWORD errors;
public:
	SerialPort(char* portName);
	~SerialPort();

	int ReadSerialPort(char* buffer, unsigned int buf_size);
	bool WriteSerialPort(char* buffer, unsigned int buf_size);
	bool isConnected();
};