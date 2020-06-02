#pragma once

#include "SquirrelFramework/SquirrelFramework.h"

class Vec3UserData : public SquirrelFramework{
public:
    Vec3UserData();
    ~Vec3UserData();

    void run();

private:
    void _setupSquirrel();
    void _execute();

    static SQInteger createVec3(HSQUIRRELVM vm);

    static SQInteger getXVal(HSQUIRRELVM vm);
    static SQInteger getMetamethod(HSQUIRRELVM vm);
    static SQInteger setMetamethod(HSQUIRRELVM vm);
};
