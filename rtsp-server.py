#!/usr/bin/env python3
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GObject

Gst.init(None)

class RTSPServer(GstRtspServer.RTSPServer):
    def __init__(self):
        super(RTSPServer, self).__init__()
        factory = GstRtspServer.RTSPMediaFactory()
        factory.set_launch(
            "( autovideosrc ! videoconvert ! x264enc tune=zerolatency bitrate=800 "
            "speed-preset=ultrafast ! rtph264pay name=pay0 pt=96 )"
        )
        factory.set_shared(True)
        self.get_mount_points().add_factory("/test", factory)
        self.attach(None)
        print("RTSP stream ready at rtsp://localhost:8554/test")

if __name__ == '__main__':
    server = RTSPServer()
    loop = GObject.MainLoop()
    loop.run()
