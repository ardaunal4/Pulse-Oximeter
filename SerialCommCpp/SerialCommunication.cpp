// SerialCommunication.cpp : This file contains the 'main' function. Program execution begins and ends there.
//

#include <iostream>
#include <iomanip>
#include <thread>
#include <string>
#include "SerialPort.h"
#include <chrono>
#include <vector>
#include <fstream>
#include "matplotlibcpp.h"

namespace plt = matplotlibcpp;                                                          // Use matplotlib namespace

char inputData[INPUT_DATA_BYTES];                                                       // Define a buffer for incoming data with 8 Bytes
int inputVal = 0;                                                                       // Define an integer variable for incoming data
char outputStart[2] = "1";                                                              // Define a char buffer to start DAQ
char outputFinish[2] = "0";                                                             // Define a char buffer to end DAQ

char comport[] = "COM7";                                                                // Define serial port
char* port = comport;
double get_time = 0.0;                                                                  // Define and initiliaze time variable
int start = 0;                                                                          // Define and initiliaze start condition variable                                                               

std::vector<int> spo2Buffer = {0};                                                      // Define data buffer for DAQ as a vector

void plotData() 
{   /*
    Plot live data
    */

    plt::clf();                                                                         // Clear figure
    plt::plot(spo2Buffer, "r-.");                                                       // Plot data in the buffer
    plt::pause(0.1);                                                                   // Pause the figure for a 20 ms
}

int main()
{
    SerialPort stm32(port);                                                             // Define stm32 object

    plt::figure();                                                                      // Open matplotlib figure
    plt::ion();                                                                         // Make figure active
    plt::title("Pulse Oximetry");                                                       // Add title to the figure
    plt::grid("on");                                                                    // Add grid into figure
    plt::show();                                                                        // Show the Figure

    if (stm32.isConnected())                                                            // Check if PC is connected to stm32 or not
    {
        std::cout << "Connected to " << port << std::endl;
    }
    else
    {
        std::cin >> port;
    }
    std::cout << "Enter the measurement time in seconds: ";
    std::cin >> get_time;
    std::cout << "\n";

    std::cout << "To start press 1 and enter: ";
    std::cin >> start;
    std::cout << "\n";

    std::ofstream outputFile;
    outputFile.open("output.csv");                                                          // Open CSV File

    if (!outputFile.is_open()) {                                                            // Check if CSV file is opened or not
        std::cerr << "Error opening output.csv for writing." << std::endl;
        return -1;
    }

    outputFile << "spo2" << std::endl;                                                      // Write column name into CSV File

    auto init_time = std::chrono::steady_clock::now();                                      // Initiliaze time
    stm32.WriteSerialPort(outputStart, 2);                                                  // Start DAQ

    while (stm32.isConnected())
    {
        auto time_now = std::chrono::steady_clock::now();                                   // Take time value
        std::chrono::duration<double> elapsed_seconds = time_now - init_time;               // Calculate elapsed time
        if ((elapsed_seconds.count() <= get_time))                                          // If elapsed time is smaller than the given time, then continue
        {
            stm32.ReadSerialPort(inputData, INPUT_DATA_BYTES);                              // Read serial data

            std::string inputValStr(inputData);                                             // Make it string

            if (!inputValStr.empty())                                                       // If the string is not empty, then continue
            {   
                inputVal = std::stoi(inputValStr);                                          // Convert incoming data to the float
                spo2Buffer.push_back(inputVal);                                             // Add it into data buffer
                outputFile << inputVal << std::endl;                                        // And write into CSV file
            }
            inputValStr.clear();                                                            // clear the string used for acquired data
            plotData();                                                                     // Plot data
            std::this_thread::sleep_for(std::chrono::milliseconds(WAIT_TIME));              // Sleep for a specified time which corresponds to incoming data frequency             
        }
        else                                                                                // If time now bigger than the given time
        {
            stm32.WriteSerialPort(outputFinish, 2);                                         // Send 0 to end acquisition
            outputFile.close();                                                             // Close CSV file
            std::cout << "Program is finished.\n";              
            break;                                                                          // Break the While loop
        }
    }

    return 0;
}