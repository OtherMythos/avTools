function start(){
    _doFile("res://meshView.nut");
    _doFile("res://meshGui.nut");
    _doFile("res://animationGui.nut");

    MeshGui.setup();
    MeshView.setup();
    if(!MeshView.validMesh){
        MeshGui.notifyInvalidMesh(MeshView.errorReason);
    }
    //Probably have a better way to get this at some point.
    if(MeshView.meshSkeletonAnimation != null){
        AnimationGui.setup();
    }
}

function update(){
    MeshView.update();
}
