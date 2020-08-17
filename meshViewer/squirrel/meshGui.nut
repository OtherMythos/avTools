::MeshGui <- {

    guiWindow = null,
    meshNameLabel = null,
    meshInfoLabel = null,
    layout = null,

    meshAnimationWindow = null,
    meshAnimationName = null,

    function setup(){
        guiWindow = _gui.createWindow();
        guiWindow.setPosition(0, 0);
        guiWindow.setSize(500, 100);

        layout = _gui.createLayoutLine();

        meshNameLabel = guiWindow.createLabel();
        meshNameLabel.setText(_settings.getUserSetting("targetMesh"));
        layout.addCell(meshNameLabel);

        meshInfoLabel = guiWindow.createLabel();
        //No text for the moment.
        meshInfoLabel.setText("");
        layout.addCell(meshInfoLabel);

        layout.layout();
    },

    function setupAnimationWindow(){
        meshAnimationWindow = _gui.createWindow();
        meshAnimationWindow.setPosition(0, 110);
        meshAnimationWindow.setSize(500, 100);

        meshAnimationName = meshAnimationWindow.createLabel();
        meshAnimationName.setText("Animation Name");
    }

    function notifyInvalidMesh(errorReason){
        meshInfoLabel.setText(errorReason);
        meshInfoLabel.setSize(500, 100);
    }
};
