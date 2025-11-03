# RTSP Webcam Streaming Setup (macOS)

This guide describes how to set up a **GStreamer RTSP server** on macOS to stream the Mac’s webcam video feed over the local network (LAN).  
Useful for testing pipelines that normally read from an RTSP source (e.g., Pupil Labs devices).

---

## 1️⃣ Install GStreamer

Download the **official GStreamer Runtime and Development packages** from:
[https://gstreamer.freedesktop.org/download/](https://gstreamer.freedesktop.org/download/)

Install both `.pkg` files:
- `gstreamer-1.0-x86_64.pkg` (Runtime)
- `gstreamer-1.0-devel-x86_64.pkg` (Development)

They’ll install under:
`/Library/Frameworks/GStreamer.framework`


---

## 2️⃣ Install Python bindings and dependencies

Make sure you’re using the **system Python**, not Conda.  
Install required packages via Homebrew and `pip`:

```bash
brew install pygobject3 gst-python cairo pkg-config
python3 -m pip install pycairo PyGObject
```

## 3️⃣ Set environment variables

Append the following to your `~/.zshrc` (or run once per session):

```bash
# --- GStreamer environment ---
export DYLD_LIBRARY_PATH="/Library/Frameworks/GStreamer.framework/Libraries:$DYLD_LIBRARY_PATH"
export LD_LIBRARY_PATH="/Library/Frameworks/GStreamer.framework/Libraries:$LD_LIBRARY_PATH"
export GI_TYPELIB_PATH="/opt/homebrew/lib/girepository-1.0"
export PATH="/Library/Frameworks/GStreamer.framework/Commands:$PATH"
# --- end GStreamer ---
```

Reload:
```bash
source ~/.zshrc
```

## 4️⃣ Create the RTSP server script

Create a file named `rtsp-server.py`:

```python
#!/usr/bin/env python3
import gi, socket
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
gi.require_version('GLib', '2.0')
from gi.repository import Gst, GstRtspServer, GLib

Gst.init(None)

class RTSPServer(GstRtspServer.RTSPServer):
    def __init__(self):
        super().__init__()
        factory = GstRtspServer.RTSPMediaFactory()
        factory.set_launch(
            "( autovideosrc ! videoconvert ! x264enc tune=zerolatency bitrate=800 "
            "speed-preset=ultrafast ! rtph264pay name=pay0 pt=96 )"
        )
        factory.set_shared(True)
        self.get_mount_points().add_factory("/test", factory)
        self.attach(None)
        ip = socket.gethostbyname(socket.gethostname())
        print(f"RTSP stream ready at rtsp://{ip}:8554/test")

if __name__ == '__main__':
    server = RTSPServer()
    loop = GLib.MainLoop()
    loop.run()
```

Run it: 
```bash
python3 rtsp-server.py
```

Expected output:
`RTSP stream ready at rtsp://192.168.x.xxx:8554/test`

## 5️⃣ View the stream (same machine or another computer)
### Local test (same Mac)
Open a second terminal:
```bash
gst-launch-1.0 rtspsrc location=rtsp://localhost:8554/test latency=60 ! decodebin ! autovideosink
```

### Remote test (e.g. PC)

Replace the IP with your Mac’s LAN IP:
```bash
gst-launch-1.0 rtspsrc location=rtsp://192.168.x.xxx:8554/test latency=60 ! decodebin ! autovideosink
```
---

## Troubleshooting

| Issue                                                      | Cause                                                         | Fix                                                                                                                             |
| ---------------------------------------------------------- | ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `ValueError: Namespace Gst not available`                  | Missing GStreamer `.typelib` files                            | Install via `brew install gst-python` and set `GI_TYPELIB_PATH=/opt/homebrew/lib/girepository-1.0`                              |
| `libglib-2.0.0.dylib` / `libgobject-2.0.0.dylib` not found | macOS can’t find GStreamer libs                               | Add to `.zshrc`:<br>`export DYLD_LIBRARY_PATH=/Library/Frameworks/GStreamer.framework/Libraries:$DYLD_LIBRARY_PATH`             |
| `ModuleNotFoundError: No module named 'gi'`                | PyGObject not installed or wrong Python used                  | Install with `python3 -m pip install PyGObject` and ensure `which python3` points to `/Library/Frameworks/Python.framework/...` |
| No video or high latency                                   | Network buffering or Wi-Fi interference                       | Reduce latency:<br>`gst-launch-1.0 rtspsrc location=rtsp://<ip>:8554/test latency=0 ! decodebin ! autovideosink sync=false`     |
| Still not working                                          | PATHs or versions mixed between Homebrew and framework builds | Run GStreamer from a fresh terminal after `source ~/.zshrc`                                                                     |
