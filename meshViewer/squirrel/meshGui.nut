::MeshGui <- {

    guiWindow = null,
    meshNameLabel = null,

    function setup(){
        guiWindow = _gui.createWindow();
        guiWindow.setPosition(0, 0);
        guiWindow.setSize(500, 100);

        local layout = _gui.createLayoutLine();

        meshNameLabel = guiWindow.createLabel();
        meshNameLabel.setText(_settings.getUserSetting("targetMesh"));
        layout.addCell(meshNameLabel);

        layout.layout();
    }
};
