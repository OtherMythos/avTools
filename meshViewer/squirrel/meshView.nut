::MeshView <- {
    oldMouseX = 0,
    oldMouseY = 0,

    rotX = 0,
    rotY = 0,
    scrollWheelStrength = 0.1,

    meshItem = null,
    cameraNode = null,
    mouseDown = false,
    currentZoomLevel = 1.8,
    validMesh = true,
    errorReason = "",

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

        //Position the camera.
        local meshRadius = meshItem.getLocalRadius();
        currentZoomLevel = meshRadius * 1.8;
        scrollWheelStrength = meshRadius * 0.1;
        positionCameraToZoom(currentZoomLevel);

        this.cameraNode = _scene.getRootSceneNode().createChildSceneNode();

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
        _camera.setPosition(xPos, 0, yPos);
        _camera.lookAt(0, 0, 0);
    },

    function update(){
        if(!validMesh) return;

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
