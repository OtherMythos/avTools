::MeshView <- {
    oldMouseX = 0,
    oldMouseY = 0,

    cameraNode = null,
    mouseDown = false,

    function setup(){
        local containerNode = _scene.getRootSceneNode().createChildSceneNode();

        local meshItem = _scene.createItem("cube");
        containerNode.attachObject(meshItem);

        //Position the camera.
        _camera.setPosition(0, 0, 10);
        _camera.lookAt(0, 0, 0);

        this.cameraNode = _scene.getRootSceneNode().createChildSceneNode();
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
    }
};
