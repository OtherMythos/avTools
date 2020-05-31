#pragma once

#include <chrono>
#include <iostream>

class Timer{
public:
    Timer(const char* timerName = 0);
    ~Timer();

    //Start the timer.
    void start();
    //Stop the timer.
    void stop();

    /**
    Get the difference between the start and stop time in milliseconds.
    */
    float getTimeTotal();

    void printTime();

private:
    std::chrono::high_resolution_clock::time_point begin;
    std::chrono::high_resolution_clock::time_point end;

    const char* mTimerName = 0;
};
