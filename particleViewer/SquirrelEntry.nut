const SCROLL_WHEEL_STRENGTH = 0.1;

function start(){
    ::mResChangeCounter <- 0;

    ::mSettingsWindow <- _gui.createWindow();
    ::mSettingsWindow.setSize(100, 100);
    ::mSettingsWindow.setVisualsEnabled(false);

    ::mParticleSystemName <- _settings.getUserSetting("ParticleName");
    ::mParticleScriptName <- _resources.getScriptForParticleSystem(::mParticleSystemName);
    ::mParticleGroupName <- _resources.findGroupContainingResource(::mParticleScriptName);
    print("Particle system found in script " + ::mParticleScriptName);
    print("Group " + ::mParticleGroupName);
    ::mPrevModifiedTime <- getModifiedTime();

    ::mReloadButton <- mSettingsWindow.createButton();
    ::mReloadButton.setText("Reload");
    ::mReloadButton.attachListener(function(widget, action){
        if(action != 2) return;
        reloadParticles();
    }, this);

    createParticleSystem();

    ::oldMouseX <- 0;
    ::oldMouseY <- 0;
    ::currentZoomLevel <- 1.8;
    ::mCameraRotX <- PI/2;
    ::mCameraRotY <- 0;

    positionCamera();
}

function update(){
    local mousePos = _gui.getMousePosGui();

    local mouseScroll = _input.getMouseWheelValue();
    if(mouseScroll != 0){
        positionCameraToZoom(currentZoomLevel + (mouseScroll * SCROLL_WHEEL_STRENGTH));
    }

    if(_input.getMouseButton(0)){
        local deltaX = mousePos.x - oldMouseX;
        local deltaY = mousePos.y - oldMouseY;

        oldMouseX = mousePos.x;
        oldMouseY = mousePos.y;

        mCameraRotX += deltaX * 0.005;
        mCameraRotY += deltaY * 0.005;

        positionCamera();
    }

    //Check every five frames if there has been a change in the particle resource.
    ::mResChangeCounter++;
    if(::mResChangeCounter >= 5){
        ::mResChangeCounter = 0;
        local time = getModifiedTime();

        if(mPrevModifiedTime != time){
            print("Particle script changed");
            //The script has changed so reload the particles.
            reloadParticles();
        }

        mPrevModifiedTime = time;
    }
}

function getModifiedTime(){
    //TODO determine the resource location and fill that in here.
    return _resources.resourceModifiedTime(::mParticleGroupName, ::mParticleScriptName);
}

function positionCameraToZoom(zoom){
    currentZoomLevel = zoom;

    positionCamera();
}

function positionCamera(){
    local xPos = cos(mCameraRotX)*currentZoomLevel;
    local yPos = sin(mCameraRotX)*currentZoomLevel;
    _camera.setPosition(xPos, 0, yPos);
    _camera.lookAt(0, 0, 0);
}

function reloadParticles(){
    destroyParticleSystem();
    _resources.destroyResourceGroup(::mParticleGroupName);
    _scene.removeAllParticleSystemTemplates();

    //Reparse the groups
    _resources.parseOgreResourcesFile(_settings.getOgreResourcesFile());

    _resources.initialiseResourceGroup(::mParticleGroupName);
    createParticleSystem();
}

function createParticleSystem(){
    if(::mParticleSystemName){
        ::mParticleNode <- _scene.getRootSceneNode().createChildSceneNode();
        ::mParticleSystem <- _scene.createParticleSystem(::mParticleSystemName);
        mParticleNode.attachObject(mParticleSystem);
        mParticleNode.setScale(0.1, 0.1, 0.1);
    }
}

function destroyParticleSystem(){
    ::mParticleNode.recursiveDestroyAttachedObjects();
    ::mParticleNode.destroyNodeAndChildren();
    ::mParticleNode = null;
    ::mParticleSystem = null;
}

function end(){

}