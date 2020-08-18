::MeshView <- {
    oldMouseX = 0,
    oldMouseY = 0,

    rotX = 0,
    rotY = 0,
    scrollWheelStrength = 0.1,

    meshItem = null,
    cameraNode = null,
    mouseDown = false,
    meshOriginPoint = null,
    currentZoomLevel = 1.8,
    validMesh = true,
    errorReason = "",
    meshSkeletonAnimation = null,

    function setup(){
        local containerNode = _scene.getRootSceneNode().createChildSceneNode();

        local targetMesh = _settings.getUserSetting("targetMesh");
        assert(targetMesh != "");

        try{
            meshItem = _scene.createItem(targetMesh);
        }catch(e){
            //The mesh provided by the user was invalid.
            validMesh = false;
            errorReason = e;
            return;
        }
        containerNode.attachObject(meshItem);

        local meshAabb = meshItem.getLocalAabb();
        meshOriginPoint = meshAabb.getCentre();

        //Position the camera.
        local meshRadius = meshItem.getLocalRadius();
        currentZoomLevel = meshAabb.getSize().y * 1.6;
        scrollWheelStrength = meshRadius * 0.1;
        positionCameraToZoom(currentZoomLevel);

        this.cameraNode = _scene.getRootSceneNode().createChildSceneNode();

        /*if(meshItem.hasSkeleton()){
            local skeleton = meshItem.getSkeleton();
            local animation = skeleton.getAnimation("Run");

            animation.setEnabled(true);
            animation.setLoop(true);
            meshSkeletonAnimation = animation;
            /* for(local i = 0; i < skeleton.getNumBones(); i++){
                local bone = skeleton.getBone(i);
                print(bone.getName());
            } */
            /*local bone = skeleton.getBone(0);
            iterateBone(bone);
        }*/
    },

    function iterateBone(bone){
        print(bone.getName());
        print(bone.getNumChildrenBones());
        for(local i = 0; i < bone.getNumChildrenBones(); i++){
            local newBone = bone.getChildBone(i);
            iterateBone(newBone);
        }
    },

    function positionCameraToZoom(zoom){
        currentZoomLevel = zoom;

        positionCamera();
    },

    function processMouseMovement(){
        if(!validMesh) return;

        local xPos = _input.getMouseX();
        local yPos = _input.getMouseY();

        local deltaX = xPos - oldMouseX;
        local deltaY = yPos - oldMouseY;

        oldMouseX = xPos;
        oldMouseY = yPos;

        rotX += deltaX * 0.005;
        rotY += deltaY * 0.005;

        /*this.cameraNode.yaw(deltaX * 0.1, _NODE_TRANSFORM_PARENT);
        this.cameraNode.pitch(deltaY * 0.1, _NODE_TRANSFORM_LOCAL);
        local cameraVecPos = this.cameraNode.getPositionVec3();

        _camera.setOrientation(this.cameraNode.getOrientation()); */

        positionCamera()
    },

    function positionCamera(){
        local xPos = cos(rotX)*currentZoomLevel;
        local yPos = sin(rotX)*currentZoomLevel;
        _camera.setPosition(xPos, this.meshOriginPoint.y, yPos);
        _camera.lookAt(this.meshOriginPoint);
    },

    function update(){
        if(!validMesh) return;

        if(meshSkeletonAnimation){
            meshSkeletonAnimation.addTime(0.001);
        }

        if(_input.getMouseButton(0)){
            if(!mouseDown){
                oldMouseX = _input.getMouseX();
                oldMouseY = _input.getMouseY();
            }
            processMouseMovement();

            mouseDown = true;
        }else{
            mouseDown = false;
        }
        local mouseScroll = _input.getMouseWheelValue();
        if(mouseScroll != 0){
            print(mouseScroll)
            positionCameraToZoom(currentZoomLevel + (mouseScroll * scrollWheelStrength));
        }
    }
};
