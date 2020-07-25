function start(){
    _doFile("res://meshView.nut");
    _doFile("res://meshGui.nut");

    MeshGui.setup();
    MeshView.setup();
}

function update(){
    MeshView.update();
}
