#include "Vec3Array.h"

#include "SquirrelFramework/Timer.h"

Vec3Array::Vec3Array() : SquirrelFramework(){

}

Vec3Array::~Vec3Array(){

}

SQInteger Vec3Array::createVec3(HSQUIRRELVM vm){
    sq_newarray(vm, 3);
    sq_pushfloat(vm, 10);
    sq_pushfloat(vm, 20);
    sq_pushfloat(vm, 30);
    sq_arrayinsert(vm, -4, 0);
    sq_arrayinsert(vm, -3, 1);
    sq_arrayinsert(vm, -2, 2);

    return 1;
}

void Vec3Array::run(){
    _setupSquirrel();

    _execute();
}

void Vec3Array::_setupSquirrel(){
    sq_pushroottable(mSqvm);

    addFunction("createVec3", createVec3);
}

void Vec3Array::_execute(){

    {
        Timer t("Create Vec3 Array");

        t.start();
        runString(
            "for(local i = 0; i < 10000; i++){"
            "local thing = [10, 20, 30];"
            "}"
        );
        t.stop();

        t.printTime();
    }

    {
        Timer t("Create vec3 from function");

        t.start();
        runString(
            "for(local i = 0; i < 10000; i++){"
            "local thing = createVec3();"
            "}"
        );
        t.stop();

        t.printTime();
    }

}
