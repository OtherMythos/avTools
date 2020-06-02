#include "Vec3UserData.h"

#include "SquirrelFramework/Timer.h"

SQObject closureObject;

struct Vec3Data{
    float x;
    float y;
    float z;
};

Vec3UserData::Vec3UserData() : SquirrelFramework(){

}

Vec3UserData::~Vec3UserData(){

}

SQInteger Vec3UserData::createVec3(HSQUIRRELVM vm){
    Vec3Data* pointer = (Vec3Data*)sq_newuserdata(vm, sizeof(Vec3Data));
    *pointer = {10, 20, 30};

    sq_pushobject(vm, closureObject);
    sq_setdelegate(vm, -2);

    return 1;
}

SQInteger Vec3UserData::getXVal(HSQUIRRELVM vm){
    SQUserPointer pointer, typeTag;
    sq_getuserdata(vm, -1, &pointer, &typeTag);

    Vec3Data* p = static_cast<Vec3Data*>(pointer);
    sq_pushfloat(vm, p->x);

    return 0;
}

SQInteger Vec3UserData::getMetamethod(HSQUIRRELVM vm){
    //std::cout << "Calling the thing" << '\n';

    // sq_pushnull(vm);
    // return sq_throwobject(vm);
    sq_pushfloat(vm, 10.0f);

    return 1;
}

SQInteger Vec3UserData::setMetamethod(HSQUIRRELVM vm){
    SQFloat val;
    sq_getfloat(vm, -1, &val);
    //std::cout << val << '\n';

    const SQChar *outStr;
    sq_getstring(vm, -2, &outStr);
    //std::cout << outStr << '\n';

    return 0;
}

float Vec3UserData::run(){
    _setupSquirrel();

    _execute();
}

void Vec3UserData::_setupSquirrel(){
    sq_pushroottable(mSqvm);

    addFunction("createVec3", createVec3);


    //Create the delegate table.

    sq_newtableex(mSqvm, 1);

    addFunction("getXVal", getXVal);
    addFunction("_get", getMetamethod);
    addFunction("_set", setMetamethod);

    sq_resetobject(&closureObject);
    sq_getstackobj(mSqvm, -1, &closureObject);
    sq_addref(mSqvm, &closureObject);
    sq_pop(mSqvm, 1);
}

void Vec3UserData::_execute(){

    {
        Timer t("Create Vec3 UserData");

        t.start();
        runString(
            "for(local i = 0; i < 10000; i++){"
            "local thing = createVec3();"
            "}"
        );
        t.stop();

        t.printTime();
    }

    {
        Timer t("Get Vec3 value by function");

        t.start();
        runString(
            "for(local i = 0; i < 10000; i++){"
            "local thing = createVec3();"
            "local second = thing.getXVal();"
            "}"
        );
        t.stop();

        t.printTime();
    }

    {
        Timer t("Get Vec3 value by metamethod");

        t.start();
        runString(
            "for(local i = 0; i < 10000; i++){"
            "local thing = createVec3();"
            "local second = thing.x;"
            //"print(second);"
            "}"
        );
        t.stop();

        t.printTime();
    }

    {
        Timer t("Set Vec3 value by metamethod");

        t.start();
        runString(
            "for(local i = 0; i < 10000; i++){"
            "local thing = createVec3();"
            "thing.x = 20;"
            "}"
        );
        t.stop();

        t.printTime();
    }

}
