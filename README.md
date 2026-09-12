# iPad Screen for Omarchy

A small tablet icon in the Omarchy bar. Click it to extend your desktop onto a
USB iPad, mirror the focused monitor, stop streaming, or select software encoding.
The icon dims when the paired device is disconnected and shows a dot while the
plugin's display service runs. Escape closes the panel.

## Requirements

This repository is the **public Omarchy interface**. It requires a separately
installed `ipad-screen` backend; that project and its iPad companion are currently
private. Installing this plugin alone does not install the display engine or app.
You need access to that backend checkout and its Linux setup instructions.

Requires Omarchy's Quattro plugin shell, Hyprland with Lua monitor support,
Python 3, a systemd user session, OpenSSH, usbmuxd, libimobiledevice, wf-recorder,
and ffmpeg. The jailbroken iPad must be trusted over USB and paired with the
backend, with the native companion installed. A running session keeps the iPad
awake. Only one iPad/display session is supported at a time.

## Install

```sh
omarchy plugin add https://github.com/cevatkerim/omarchy-ipad-screen.git --enable
python3 ~/.config/omarchy/plugins/kerim.ipad-screen/control.py configure /path/to/ipad-screen
```

Use an absolute path to your backend checkout. It must include the saved-profile
support and native capture recovery. Backend credentials stay in its ignored
`.runtime/` directory. Only the backend path is written to
`${XDG_CONFIG_HOME:-~/.config}/ipad-screen/host.json`. No password is entered in
the panel, included in this repository, or passed on a command line.

Click the tablet icon on the right of the bar. **Extend** creates a display to the
right at scale 2; **Mirror** captures the focused output, with letterboxing when
aspect ratios differ. **Stop** releases capture, USB, and the temporary display.
Hardware encoding uses VA-API at 30 fps. Select **Encoder: Software** before
starting if your GPU cannot encode H.264 through `/dev/dri/renderD128`.

The panel shows host process/USB status and recent diagnostics. It cannot prove
that the iPad panel physically presented each frame. If you started a session
in a terminal, stop it with Ctrl+C there before using the plugin.

See [setting up another iPad](docs/another-ipad.md).

## Update and remove

Stop the display before updating or removing the plugin:

```sh
python3 ~/.config/omarchy/plugins/kerim.ipad-screen/control.py stop
omarchy plugin update kerim.ipad-screen
# Or remove the bar integration:
omarchy plugin remove kerim.ipad-screen
```

Disabling/removing the widget does not stop an active display. The transient
`ipad-screen.service` owns capture so opening a second monitor, changing bar
settings, or reloading QML cannot interrupt playback. It stops with the graphical
session. If the icon is unavailable, use `systemctl --user stop ipad-screen`.
Removal leaves the backend, iPad app, pairing, and host path configuration intact.

## Development

The manifest is at the repository root, following the official
[plugin development guide](https://plugins.omarchy.org/develop.html) and
[shell plugin manual](https://omarchy.org/manual/shell-plugins/).
The widget loads its panel in Omarchy's existing Quickshell process. A small
Python helper invokes the backend with argument arrays via a transient systemd
user service. No root daemon or persistent autostart is installed.

```sh
omarchy plugin validate .
python3 -m unittest discover -s tests -v
python3 control.py status
omarchy-shell shell summon kerim.ipad-screen '{}'
omarchy-shell shell hide kerim.ipad-screen
```

Edit a user-owned plugin copy, not `/usr/share/omarchy`. Saved QML reloads
automatically. Inspect runtime errors with
`qs log -p /usr/share/omarchy/shell --tail 100`.

This is an experimental Linux integration. Mac and Windows host applications,
touch input, audio and multiple simultaneous iPads are future work.
