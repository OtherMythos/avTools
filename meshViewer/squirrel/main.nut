function start(){
    _doFile("res://meshView.nut");
    _doFile("res://meshGui.nut");

    MeshGui.setup();
    MeshView.setup();
    if(!MeshView.validMesh){
        MeshGui.notifyInvalidMesh(MeshView.errorReason);
    }
}

function update(){
    MeshView.update();
}
