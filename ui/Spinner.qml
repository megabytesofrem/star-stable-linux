import QtQuick
import QtQuick.Controls

Item {
    id: spinnerContainer
    
    // 1. Set default fallback sizes, but allow layouts to override them
    implicitWidth: 24
    implicitHeight: 24

    property alias isLoading: loadingSpinner.playing
    visible: isLoading

    AnimatedImage {
        id: loadingSpinner
        anchors.fill: parent
        source: "../resources/spinner.gif" 
        playing: true
        
        // PreserveAspectFit ensures it never stretches or distorts
        fillMode: Image.PreserveAspectFit
        mipmap: true 

        opacity: playing ? 1.0 : 0.0
        Behavior on opacity {
            NumberAnimation { duration: 250 }
        }
    }
}