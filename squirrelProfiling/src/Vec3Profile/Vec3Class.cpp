#include "Vec3Class.h"

#include "SquirrelFramework/Timer.h"

SQMemberHandle handleX;
SQMemberHandle handleY;
SQMemberHandle handleZ;
SQObject classObject;

Vec3Class::Vec3Class() : SquirrelFramework(){

}

Vec3Class::~Vec3Class(){

}

SQInteger Vec3Class::createVec3(HSQUIRRELVM vm){
    sq_pushobject(vm, classObject);

    sq_createinstance(vm, -1);

    return 1;
}

SQInteger Vec3Class::createVec3Get(HSQUIRRELVM vm){
    sq_pushroottable(vm);
    sq_pushstring(vm, _SC("Vec3"), -1);
    sq_get(vm, -2);

    sq_createinstance(vm, -1);

    return 1;
}

float Vec3Class::run(){
    _setupSquirrel();

    _execute();
}

/*
Create as class.
See how long it takes to construct and pass 100 of them into a function.
*/
void Vec3Class::_setupSquirrel(){
    sq_pushroottable(mSqvm);

    sq_pushstring(mSqvm, _SC("Vec3"), -1);
    sq_newclass(mSqvm, 0);

    sq_pushstring(mSqvm, _SC("x"), -1);
    sq_pushfloat(mSqvm, 0);
    sq_newslot(mSqvm, -3, false);

    sq_pushstring(mSqvm, _SC("y"), -1);
    sq_pushfloat(mSqvm, 0);
    sq_newslot(mSqvm, -3, false);

    sq_pushstring(mSqvm, _SC("z"), -1);
    sq_pushfloat(mSqvm, 0);
    sq_newslot(mSqvm, -3, false);


    sq_pushstring(mSqvm, _SC("x"), -1);
    sq_getmemberhandle(mSqvm, -2, &handleX);

    sq_pushstring(mSqvm, _SC("y"), -1);
    sq_getmemberhandle(mSqvm, -2, &handleY);

    sq_pushstring(mSqvm, _SC("z"), -1);
    sq_getmemberhandle(mSqvm, -2, &handleZ);

    sq_resetobject(&classObject);
    sq_getstackobj(mSqvm, -1, &classObject);

    sq_newslot(mSqvm, -3, false);


    addFunction("createVec3", createVec3);
    addFunction("createVec3Get", createVec3Get);
}

void Vec3Class::_execute(){

    { //Create an instance from the global value.
        Timer t("create Vec3");

        t.start();
        runString(
            "for(local i = 0; i < 10000; i++){"
            "local thing = Vec3();"
            "}"
        );
        t.stop();

        t.printTime();
    }

    { //Create an instance by calling a function.
        Timer t("Call Vec3 create function");

        t.start();
        runString(
            "for(local i = 0; i < 10000; i++){"
            "local thing = createVec3();"
            "}"
        );
        t.stop();

        t.printTime();
    }

    { //Create an instance by calling a function which does an unintelligent get.
        Timer t("Call Vec3 create function with get");

        t.start();
        runString(
            "for(local i = 0; i < 10000; i++){"
            "local thing = createVec3Get();"
            "}"
        );
        t.stop();

        t.printTime();
    }

}
