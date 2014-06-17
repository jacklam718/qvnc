#!/usr/bin/env python
# --*-- coding: utf-8 --*--
#
#    The MIT License (MIT)
#
#    Copyright (c) 2013 Jack Lam <jacklam718@gmail.com>
#
#    Permission is hereby granted, free of charge, to any person obtaining a copy
#    of this software and associated documentation files (the "Software"), to deal
#    in the Software without restriction, including without limitation the rights
#    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#    copies of the Software, and to permit persons to whom the Software is
#    furnished to do so, subject to the following conditions:
#
#    The above copyright notice and this permission notice shall be included in all
#    copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#    SOFTWARE.

import qt4reactor
from PyQt4 import QtGui
from PyQt4 import QtCore
from dialog import passwdDialog, connectDialog
from struct import pack, unpack
import rfb
import sys
import time
app = QtGui.QApplication(sys.argv)

qt4reactor.install( )

from twisted.internet import reactor

class RFBtoViewer32(rfb.RFBClient):
    def vncConnectionMade(self):
        print('vncConnectionMade')
        self.notifyImage = self.factory.window.notifyImage
        self.window = self.factory.window
        self.window.show( )
        self.window.readyVNCViewer(self)
        self.window.resize(self.width, self.height)
        self.setEncodings(self.factory.encodings)
        self.setPixelFormat( )           #set up pixel format to 32 bits
        self.framebufferUpdateRequest( ) #request initial screen update

    def vncRequestPassword(self):
        print('vncRequestPassword')
        if self.factory.password:
            self.sendPassword(self.factory.password)
        else:
            passwd = passwdDialog(message="VNC Server "+host)
            if not passwd:
                return
            self.sendPassword(passwd)

    def commitUpdate(self, rectangles = None):
        print("commitUpdate")
        """finish series of display updates"""
        self.window.repaint( )
        self.framebufferUpdateRequest(incremental=5)

    def updateRectangle(self, x, y, width, height, data):
        imageFormat = QtGui.QImage.Format_RGB32
        image = QtGui.QImage(data, width, height, imageFormat)
        self.notifyImage(x, y, image)

    #def copyRectangle(self, srcx, srcy, x, y, width, height):
        pass

    #def fillRectangle(self, x, y, width, height, color):
    #    pass

    def bell(self):
        print "katsching"

    def copy_text(self, text):
        print "Clipboard: %r" % text


class VNCFactory(rfb.RFBFactory):
    def __init__(self, window, depth, fast, *args, **kwargs):
        rfb.RFBFactory.__init__(self, *args, **kwargs)
        self.window = window
        if depth == 32:
            self.protocol = RFBtoViewer32
        elif depth == 8:
            self.protocol = RFBToGUIeightbits
        else:
            raise ValueError, "color depth not supported"
            
        if fast:
            self.encodings = [
                rfb.COPY_RECTANGLE_ENCODING,
                rfb.RAW_ENCODING,
            ]
        else:
            self.encodings = [
                rfb.COPY_RECTANGLE_ENCODING,
                rfb.HEXTILE_ENCODING,
                rfb.CORRE_ENCODING,
                rfb.RRE_ENCODING,
                rfb.RAW_ENCODING,
            ]

    def buildProtocol(self, addr):
        return rfb.RFBFactory.buildProtocol(self, addr)

    def clientConnectionLost(self, connector, reason):
        #log.msg("connection lost: %r" % reason.getErrorMessage())
        reactor.stop()

    def clientConnectionFailed(self, connector, reason):
        #log.msg("cannot connect to server: %r\n" % reason.getErrorMessage())
        reactor.stop()


class QVNCViewer(QtGui.QDialog):
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self.setMouseTracking(True)
        self._refresh    = [ ]
        self._rectangles = [ ]

    def readyVNCViewer(self, rfb):
        self._rfb = rfb
    
    def notifyImage(self, x, y, qimage):
        self._refresh.append({"x": x, "y": y, "image": qimage})
        self.repaint( )
    
    def paintEvent(self, event):
        if not self._refresh:
            return

        qp = QtGui.QPainter( )
        qp.begin(self)
        for image in self._refresh:
            qp.drawImage(image["x"], image["y"], image["image"])
        qp.end( )

    def sendMouseEvent(self, e):
        mask = e.button( )
        self._rfb.pointerEvent(e.pos().x(), e.pos().y(), mask)

    def sendKeyEvent(self, e):
        self._rfb.keyEvent(e.nativeVirtualKey(), True)

    def updateFramebuffer(self, pixelmap):
        self.framebuffer = pixelmap

    def keyPressEvent(self, event):
        self.sendKeyEvent(event)

    def mouseMoveEvent(self,  event):
        self.sendMouseEvent(event)

    def mousePressEvent(self, event):
        self.sendMouseEvent(event)
        
    def resizeEvent(self, event):
        size = event.size( )
        self.width, self.height = (size.width(), size.height())
    
    def closeEvent(self, event):
        reactor.stop( )
        self.close( )
        exit( ) 

def main( ):
    global host
    option = connectDialog( )
    if not option:
        return
    host, speed = option
    print(host, speed)
    window = QVNCViewer( )
    reactor.connectTCP(
        host,
        5900,
        VNCFactory(
                window,
                32,
                "fast",
                "",   # password
                1,
            )
        )
    
    reactor.run( )
if __name__ == "__main__":
    main( )
