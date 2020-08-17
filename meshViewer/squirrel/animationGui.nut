::AnimationGui <- {
    layout = null,

    guiWindow = null,
    meshAnimationName = null,
    playAnimationButton = null,

    playingAnimation = null,

    function playPauseAnimationButtonPressed(widget, action){
        if(action == 2){
            ::AnimationGui.togglePlayAnimation();
        }
    },

    function setup(){
        guiWindow = _gui.createWindow();
        guiWindow.setPosition(0, 110);
        guiWindow.setSize(500, 100);

        layout = _gui.createLayoutLine();

        meshAnimationName = guiWindow.createLabel();
        meshAnimationName.setText("Animation Name");
        layout.addCell(meshAnimationName);

        playAnimationButton = guiWindow.createButton();
        playAnimationButton.setText("");
        playAnimationButton.attachListener(playPauseAnimationButtonPressed);
        layout.addCell(playAnimationButton);

        layout.layout();

        setPlayAnimation(false);
    },

    function togglePlayAnimation() { setPlayAnimation(!playingAnimation); },

    function setPlayAnimation(play){
        this.playingAnimation = play;

        playAnimationButton.setText(play ? "Stop Animation" : "Play Animation");
    }
};
