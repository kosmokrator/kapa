# -*- coding: utf-8 -*-
import pygtk
pygtk.require("2.0")
import gtk

import threading
import serial
import math

class Input(threading.Thread):
    def __init__(self, stream):
        self.stream = stream
        self.canceled = False
        
        
    def run(self):
        while not self.canceled:
            byte = self.stream.read()
            if byte == "":
                break
            

class Capture(object):
    pass

class Plotter(gtk.DrawingArea):

    def __init__(self):
        super(Plotter, self).__init__()
        self.set_size_request(1, 1)
        self.connect("expose-event", self.expose)
        self.connect("configure-event", self.configure)

    def configure(self, widget, event):
        x, y, width, height = self.get_allocation()
        self.pixmap = gtk.gdk.Pixmap(self.window, width, height)
        xgc = self.window.new_gc()
        xgc.set_rgb_fg_color(gtk.gdk.Color(40000, 40000, 40000))
        self.pixmap.draw_rectangle(xgc, True, 0, 0, width, height)
        return True

    def expose(self, widget, event):
        x, y, width, height = event.area
        self.window.draw_drawable(self.get_style().fg_gc[gtk.STATE_NORMAL], self.pixmap, x, y, x, y, width, height)
        return False

class Kapa(gtk.Window):

    def delete_event(self, widget, event, data=None):
        print "delete event occured"
        return False


    def destroy(self, widget, data=None):
        gtk.main_quit()


    def toggle_capture(self, widget, data=None):
        if self.capture:
            self.stop_capture()
        else:
            self.start_capture()

    def start_capture(self):
        self.capture = Capture()
        self.capture_btn.set_stock_id(gtk.STOCK_MEDIA_STOP)
        self.statusbar.push(self.statusbar_context_id, "Aufnahme läuft")

    def stop_capture(self):
        self.capture = None
        self.capture_btn.set_stock_id(gtk.STOCK_MEDIA_RECORD)        
        self.statusbar.pop(self.statusbar_context_id)

    def export(self, widget, data=None):
        f = gtk.FileChooserDialog(
            title="Exportieren",
            parent=self,
            action=gtk.FILE_CHOOSER_ACTION_SAVE,
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK)
            )
        f.run()
        f.destroy()

    def make_ui(self):
        self.set_title("Kapazitätsmesser")
        
        self.connect("delete_event", self.delete_event)
        self.connect("destroy", self.destroy)

        self.vbox = gtk.VBox(False, 0)

        self.toolbar = gtk.Toolbar()
        self.toolbar.set_orientation(gtk.ORIENTATION_HORIZONTAL)

        self.capture_btn = gtk.ToolButton(gtk.STOCK_MEDIA_RECORD)
        self.capture_btn.connect("clicked", self.toggle_capture)
        self.toolbar.insert(self.capture_btn, 0)
        self.toolbar.show()

        self.export_btn = gtk.ToolButton(gtk.STOCK_FLOPPY)
        self.export_btn.connect("clicked", self.export)
        self.toolbar.insert(self.export_btn, 1)

        self.vbox.pack_start(self.toolbar, False, False, 0)

        self.table = gtk.Table(3, 2, False)

        self.plotter = Plotter()
        self.table.attach(self.plotter, 1, 2, 1, 2, gtk.EXPAND|gtk.FILL, gtk.FILL, 0, 0)
        self.plotter.set_events(gtk.gdk.POINTER_MOTION_MASK | gtk.gdk.POINTER_MOTION_HINT_MASK)
        self.hrule = gtk.HRuler()
        self.hrule.set_metric(gtk.PIXELS)
        self.hrule.set_range(0, 800, 0, 800)
        self.plotter.connect_object("motion-notify-event", lambda r, e : r.emit("motion-notify-event", e), self.hrule)
        self.table.attach(self.hrule, 1, 2, 0, 1, gtk.EXPAND|gtk.SHRINK|gtk.FILL, gtk.FILL, 0, 0)

        self.vrule = gtk.VRuler()
        self.vrule.set_metric(gtk.PIXELS)
        self.vrule.set_range(0, 800, 0, 800)
        self.plotter.connect_object("motion-notify-event", lambda r, e : r.emit("motion-notify-event", e), self.vrule)
        self.table.attach(self.vrule, 0, 1, 1, 2, gtk.FILL, gtk.EXPAND|gtk.SHRINK|gtk.FILL, 0, 0)

        self.vbox.pack_start(self.table, True, True, 0)

        self.statusbar = gtk.Statusbar()
        self.statusbar_context_id = self.statusbar.get_context_id("Anwendung")
        self.vbox.pack_end(self.statusbar, False, False, 0)
        
        self.add(self.vbox)

        self.show_all()

        self.show()

        
    def __init__(self):
        super(Kapa, self).__init__(gtk.WINDOW_TOPLEVEL)
        self.make_ui()
        self.capture = None


    def main(self):
        gtk.main()

if __name__ == "__main__":
    Kapa().main()
