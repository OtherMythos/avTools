::MeshView <- {
    oldMouseX = 0,
    oldMouseY = 0,

    meshItem = null,
    cameraNode = null,
    mouseDown = false,
    currentZoomLevel = 1.8,

    function setup(){
        local containerNode = _scene.getRootSceneNode().createChildSceneNode();

        local targetMesh = _settings.getUserSetting("targetMesh");
        assert(targetMesh != "");

        try{
            meshItem = _scene.createItem(targetMesh);
        }catch(e){
            //The mesh provided by the user might have been invalid, so check that.
        }
        containerNode.attachObject(meshItem);

        //Position the camera.
        positionCameraToZoom(currentZoomLevel);

        this.cameraNode = _scene.getRootSceneNode().createChildSceneNode();
    },

    function positionCameraToZoom(zoom){
        local meshRadius = meshItem.getLocalRadius();
        _camera.setPosition(0, 0, meshRadius * zoom);

        _camera.lookAt(0, 0, 0);
        currentZoomLevel = zoom;
    },

    function processMouseMovement(){
        local xPos = _input.getMouseX();
        local yPos = _input.getMouseY();

        local deltaX = xPos - oldMouseX;
        local deltaY = yPos - oldMouseY;

        oldMouseX = xPos;
        oldMouseY = yPos;

        this.cameraNode.yaw(deltaX * 0.1, _NODE_TRANSFORM_PARENT);
        this.cameraNode.pitch(deltaY * 0.1, _NODE_TRANSFORM_LOCAL);
        local cameraVecPos = this.cameraNode.getPositionVec3();

        _camera.setOrientation(this.cameraNode.getOrientation());
    },

    function update(){
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
            positionCameraToZoom(currentZoomLevel + (mouseScroll * 0.1));
        }
    }
};
