#include "SquirrelFramework.h"

#include <sqstdio.h>
#include <sqstdmath.h>
#include <sqstdsystem.h>
#include <sqstdstring.h>
#include <iostream>
#include <stdarg.h>
#include <string.h>

#ifdef SQUNICODE
#define scvprintf vwprintf
#else
#define scvprintf vprintf
#endif

SquirrelFramework::SquirrelFramework(){
    _setupVM();
}

SquirrelFramework::~SquirrelFramework(){
    _shutdowVM();
}

float SquirrelFramework::run(){

}

void printfunc(HSQUIRRELVM v, const SQChar *s, ...){
    va_list arglist;
    va_start(arglist, s);
    scvprintf(s, arglist);
    va_end(arglist);
    std::cout << '\n';
}

void SquirrelFramework::_setupVM(){
    mSqvm = sq_open(1024);

    sq_setprintfunc(mSqvm, printfunc, NULL);
}

void SquirrelFramework::_shutdowVM(){
    sq_close(mSqvm);
}

void SquirrelFramework::runString(const char* script){
    sq_compilebuffer(mSqvm, script, (int)strlen(script)*sizeof(SQChar), "compiledString", true);
    sq_pushroottable(mSqvm);
    sq_call(mSqvm,1,1,0);

    //TODO might want to pop here.
}

void SquirrelFramework::addFunction(const char* fname, SQFUNCTION f){
    sq_pushstring(mSqvm, _SC(fname), -1);
    sq_newclosure(mSqvm,f,0);
    sq_newslot(mSqvm,-3,SQFalse);
}
