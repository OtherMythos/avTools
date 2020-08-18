function start(){
    _doFile("res://meshView.nut");
    _doFile("res://meshGui.nut");
    _doFile("res://animationGui.nut");

    MeshGui.setup();
    MeshView.setup();
    if(!MeshView.validMesh){
        MeshGui.notifyInvalidMesh(MeshView.errorReason);
        return;
    }

    AnimationGui.setup(MeshView);
}

function update(){
    MeshView.update();
    AnimationGui.update(0.01);
}
