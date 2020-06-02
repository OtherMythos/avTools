#pragma once

#include <squirrel.h>

class SquirrelFramework{
public:
    SquirrelFramework();
    virtual ~SquirrelFramework();

    virtual void run();

protected:
    HSQUIRRELVM mSqvm;

    void runString(const char* script);

    void addFunction(const char* fname, SQFUNCTION f);

private:
    void _setupVM();
    void _shutdowVM();
};
