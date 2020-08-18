::AnimationGui <- {
    layout = null,

    guiWindow = null,
    meshAnimationName = null,
    mMeshAnimationTimeLabel = null,
    playAnimationButton = null,

    mPlayingAnimation = null,

    currentAnimation = null,

    mAnimationNames = null,
    mViewingMesh = null,
    mCurrentSkeletalAnimation = null

    function playPauseAnimationButtonPressed(widget, action){
        if(action == 2){
            ::AnimationGui.togglePlayAnimation();
        }
    },

    function animationSelectButton(widget, action){
        if(action == 2){
            ::AnimationGui.setCurrentAnimation(widget.getText());
        }
    },

    function setup(mesh){
        if(!mesh.meshItem.hasSkeleton()) return;
        mViewingMesh = mesh;

        guiWindow = _gui.createWindow();
        guiWindow.setPosition(0, 110);
        guiWindow.setSize(500, 300);

        layout = _gui.createLayoutLine();

        meshAnimationName = guiWindow.createLabel();
        layout.addCell(meshAnimationName);

        mMeshAnimationTimeLabel = guiWindow.createLabel();
        layout.addCell(mMeshAnimationTimeLabel);

        //You need to write something into the labels so the resize works.
        meshAnimationName.setText("h");
        mMeshAnimationTimeLabel.setText("h");

        local skeleton = mesh.meshItem.getSkeleton();
        mAnimationNames = [];
        for(local i = 0; i < skeleton.getNumAnimations(); i++){
            local animName = skeleton.getAnimation(i).getName()
            mAnimationNames.append(animName);

            local animButton = guiWindow.createButton();
            animButton.setText(animName);
            animButton.attachListener(animationSelectButton);
            layout.addCell(animButton);
        }

        playAnimationButton = guiWindow.createButton();
        playAnimationButton.setText("");
        playAnimationButton.attachListener(playPauseAnimationButtonPressed);
        layout.addCell(playAnimationButton);

        layout.layout();

        setPlayAnimation(false);
        if(mAnimationNames.len() > 0){
            setCurrentAnimation(mAnimationNames[0]);
        }
    },

    function setCurrentAnimation(newName){
        meshAnimationName.setText(newName);

        if(mCurrentSkeletalAnimation != null){
            mCurrentSkeletalAnimation.setEnabled(false);
            mCurrentSkeletalAnimation.setLoop(false);
        }

        mCurrentSkeletalAnimation = mViewingMesh.meshItem.getSkeleton().getAnimation(newName);
        mCurrentSkeletalAnimation.setEnabled(true);
        mCurrentSkeletalAnimation.setLoop(true);
    },

    function togglePlayAnimation() { setPlayAnimation(!mPlayingAnimation); },

    function setPlayAnimation(play){
        this.mPlayingAnimation = play;

        playAnimationButton.setText(play ? "Stop Animation" : "Play Animation");
    },

    function updateAnimationTimers(){
        mMeshAnimationTimeLabel.setText("Animation Time: " + mCurrentSkeletalAnimation.getCurrentTime());
    },

    function update(delta){
        if(mPlayingAnimation) return false;
        if(mCurrentSkeletalAnimation == null) return false;

        mCurrentSkeletalAnimation.addTime(delta);
        updateAnimationTimers();
    }
};
