import QtQuick
import Quickshell
import Quickshell.Io
import qs.Commons
import qs.Ui
import qs.Ui as Ui

Ui.Panel {
  id: root
  moduleName: "kerim.ipad-screen"
  manageIpc: false
  property var anchorItem: null
  property var hostWidget: null
  property var hostStatus: ({})
  property string actionError: ""
  property string encoder: "vaapi"
  readonly property string helper: decodeURIComponent(Qt.resolvedUrl("control.py").toString().replace(/^file:\/\//, ""))
  function open() { root.controller.show(); refresh() }
  function close() { root.controller.hide() }
  function refresh() { if (!statusProcess.running) statusProcess.running = true }
  function act(args) {
    if (actionProcess.running) return
    actionError = ""
    actionProcess.command = ["python3", helper].concat(args)
    actionProcess.running = true
  }
  function switchPanel(direction) {
    if (root.bar && typeof root.bar.switchPanelFrom === "function")
      return root.bar.switchPanelFrom(root.hostWidget || root, direction)
    return false
  }
  Component.onCompleted: refresh()
  Timer { interval: root.opened ? 2000 : 5000; running: true; repeat: true; onTriggered: root.refresh() }
  Process {
    id: statusProcess
    command: ["python3", root.helper, "status"]
    stdout: StdioCollector {
      onStreamFinished: {
        try { root.hostStatus = JSON.parse(this.text) }
        catch (e) { root.hostStatus = {error: "Could not read host status"} }
      }
    }
  }
  Process {
    id: actionProcess
    stdout: StdioCollector {
      onStreamFinished: {
        try { root.actionError = JSON.parse(this.text).error || "" }
        catch (e) { root.actionError = "The host command did not return a result" }
      }
    }
    onExited: root.refresh()
  }
  KeyboardPanel {
    id: popup
    anchorItem: root.anchorItem
    owner: root.hostWidget || root
    bar: root.bar
    open: root.opened
    focusTarget: keys
    contentWidth: popup.fittedContentWidth(Style.space(360))
    contentHeight: popup.fittedContentHeight(content.implicitHeight)
    PanelKeyCatcher {
      id: keys
      anchors.fill: parent
      onCloseRequested: root.close()
      onTabRequested: function(direction) { root.switchPanel(direction) }
      Column {
        id: content
        width: parent.width
        spacing: Style.space(14)
        Text {
          text: "iPad Screen"; color: root.barForeground
          font.family: Style.font.family; font.pixelSize: Style.font.display; font.bold: true
        }
        Text {
          width: parent.width; wrapMode: Text.WordWrap; textFormat: Text.PlainText
          text: root.actionError || root.hostStatus.error || root.hostStatus.message || "Checking USB connection…"
          color: root.barForeground; font.family: Style.font.family; font.pixelSize: Style.font.body
        }
        Text {
          visible: root.hostStatus.configured === true
          text: (root.hostStatus.model === "ipad9" ? "iPad 9 · 2160 × 1620" : root.hostStatus.model === "pro97" ? "iPad Pro 9.7 · 2048 × 1536" : "iPad Pro 10.5 · 2224 × 1668") + " · 30 fps"
          color: root.barForeground; opacity: 0.65
          font.family: Style.font.family; font.pixelSize: Style.font.caption
        }
        Row {
          spacing: Style.space(8)
          Repeater {
            model: ["extend", "mirror"]
            WidgetButton {
              required property string modelData
              bar: root.bar
              text: modelData === "extend" ? "Extend" : "Mirror"
              interactive: root.hostStatus.ready === true && !root.hostStatus.running && !actionProcess.running
              dimmed: !interactive
              onPressed: root.act(["start", modelData, "--encoder", root.encoder])
            }
          }
          WidgetButton {
            bar: root.bar; text: "Stop"
            interactive: root.hostStatus.running === true && !actionProcess.running
            dimmed: !interactive
            onPressed: root.act(["stop"])
          }
        }
        WidgetButton {
          bar: root.bar
          text: root.encoder === "vaapi" ? "Encoder: Hardware" : "Encoder: Software"
          interactive: !root.hostStatus.running && !actionProcess.running
          dimmed: !interactive
          onPressed: root.encoder = root.encoder === "vaapi" ? "software" : "vaapi"
        }
        Text {
          width: parent.width; wrapMode: Text.WordWrap; textFormat: Text.PlainText
          text: root.hostStatus.detail || "Extend adds a desktop to the right. Mirror uses the focused monitor."
          maximumLineCount: 4; elide: Text.ElideRight
          color: root.barForeground; opacity: 0.65
          font.family: Style.font.family; font.pixelSize: Style.font.caption
        }
        WidgetButton {
          bar: root.bar; text: "Setup guide"
          onPressed: Qt.openUrlExternally(Qt.resolvedUrl("README.md"))
        }
      }
    }
  }
}
