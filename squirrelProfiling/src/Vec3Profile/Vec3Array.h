#pragma once

#include "SquirrelFramework/SquirrelFramework.h"

class Vec3Array : public SquirrelFramework{
public:
    Vec3Array();
    ~Vec3Array();

    void run();

private:
    void _setupSquirrel();
    void _execute();

    static SQInteger createVec3(HSQUIRRELVM vm);
};
