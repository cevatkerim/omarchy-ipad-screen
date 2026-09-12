import QtQuick
import qs.Commons
import qs.Ui
import qs.Ui as Ui

Ui.BarWidget {
  id: root
  moduleName: "kerim.ipad-screen"
  readonly property bool opened: panelLoader.item ? panelLoader.item.opened : false
  readonly property bool popoutSwitchClosing: panelLoader.item ? panelLoader.item.popoutSwitchClosing : false
  function open() { if (panelLoader.item) panelLoader.item.open() }
  function close() { if (panelLoader.item) panelLoader.item.close() }
  function toggle() { if (panelLoader.item) panelLoader.item.toggle() }
  function closeForPopoutSwitch() { if (panelLoader.item) panelLoader.item.closeForPopoutSwitch() }
  function injectPanel() {
    if (!panelLoader.item) return
    panelLoader.item.bar = root.bar
    panelLoader.item.anchorItem = button
    panelLoader.item.hostWidget = root
  }
  implicitWidth: button.implicitWidth
  implicitHeight: button.implicitHeight
  onBarChanged: injectPanel()
  Loader {
    id: panelLoader
    active: true
    visible: false
    source: Qt.resolvedUrl("Panel.qml")
    onLoaded: { root.injectPanel(); Qt.callLater(root.injectPanel) }
  }
  WidgetButton {
    id: button
    anchors.fill: parent
    bar: root.bar
    hasVisualContent: true
    fixedWidth: root.barSize
    tooltipText: "iPad Screen"
    onPressed: function(buttonCode) { if (buttonCode === Qt.LeftButton) root.toggle() }
    Rectangle {
      anchors.centerIn: parent
      width: Style.space(19); height: Style.space(14)
      radius: Style.space(3)
      color: "transparent"
      border.width: Style.space(1.5)
      border.color: button.foreground
      opacity: panelLoader.item && panelLoader.item.hostStatus.connected ? 1 : 0.55
      Rectangle {
        anchors.right: parent.right; anchors.bottom: parent.bottom
        anchors.margins: -Style.space(2)
        width: Style.space(6); height: width; radius: width / 2
        color: button.activeColor
        visible: panelLoader.item ? panelLoader.item.hostStatus.running === true : false
      }
    }
  }
}
