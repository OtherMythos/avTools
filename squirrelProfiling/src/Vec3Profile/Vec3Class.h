#pragma once

#include "SquirrelFramework/SquirrelFramework.h"

class Vec3Class : public SquirrelFramework{
public:
    Vec3Class();
    ~Vec3Class();

    void run();

private:
    void _setupSquirrel();
    void _execute();

    static SQInteger createVec3(HSQUIRRELVM vm);
    static SQInteger createVec3Get(HSQUIRRELVM vm);
};
