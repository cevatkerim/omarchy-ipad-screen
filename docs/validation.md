# Validation record

Tested on the development Omarchy/Quattro desktop with Hyprland 0.56.2,
2026-09-12. The separate backend contains the detailed investigation history.

- Manifest validation passes; three Python controller tests pass.
- Installed into the user plugin directory and enabled on the right of the bar.
- Tablet icon and opened panel inspected on screen. Shell summon/hide and Escape
  exercised; no plugin QML errors observed in the shell runtime log.
- The controller started and stopped real USB Extend and Mirror sessions on an
  iPad Pro 9.7-inch, iPadOS 16.7.16, with Dopamine. Extension queued 3,084 frames
  in 104.44 seconds; mirror queued 4,420 frames in 148.37 seconds. Both reported
  zero renderer errors. The temporary extended monitor was removed on stop.
- Disable/re-enable and an update from the public GitHub origin preserved the
  running mirror session. The service also survived the QML reloads involved in
  creating/removing a display.
- A second install of the companion through the updated backend successfully
  reached its listening state in Dopamine's standard Applications directory.

The owner confirmed the companion opens; confirmation of visible playback
smoothness on the Pro 9.7 is pending. Frame counts describe submission to the
native renderer, not measured panel refresh or end-to-end latency. The Pro 10.5
was visually verified with the backend earlier. Actual iPad 9 hardware, other
host GPUs, full shell restart, graphical logout, and removal during playback have
not been tested. Stop a display before removing its widget.

The documented standalone `qmllint` command cannot resolve this installation's
virtual `qs.*` imports, so its warnings are not a clean static QML validation.
The actual running Omarchy shell loaded the widget and its controls successfully.
