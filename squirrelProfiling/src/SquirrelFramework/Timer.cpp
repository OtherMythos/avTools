#include "Timer.h"

Timer::Timer(const char* timerName)
    : mTimerName(timerName) {

}

Timer::~Timer(){

}

void Timer::start(){
    begin = std::chrono::high_resolution_clock::now();
}

void Timer::stop(){
    end = std::chrono::high_resolution_clock::now();
}

float Timer::getTimeTotal(){
    std::chrono::duration<float> duration = std::chrono::duration_cast<std::chrono::nanoseconds>(end - begin);

    return duration.count();
}

void Timer::printTime(){
    if(mTimerName){
        std::cout << mTimerName << ":\t";
    }
    std::cout << getTimeTotal() << " ns" << '\n';
}
