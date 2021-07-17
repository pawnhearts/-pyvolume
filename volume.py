import gi
import os, sys

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("Keybinder", "3.0")
from gi.repository import Gtk, GLib, Gdk, Keybinder

from pydbus import SessionBus


class VolumeDBUSService(object):
    """
        <node>
            <interface name='net.lew21.pydbus.ClientServerExample'>
                <method name='Draw'>
                </method>
                <method name='Set'>
                    <arg type='s' name='volume' direction='in'/>
                    <arg type='i' name='volume' direction='out'/>
                </method>
                <method name='Get'>
                    <arg type='i' name='volume' direction='out'/>
                </method>
                <method name='Quit'/>
            </interface>
        </node>
    """

    def __init__(self, win):
        self.win = win

    def Draw(self):
        self.win.draw()

    def Set(self, s):
        return self.win.change_volume(s)

    def Get(self):
        return self.win.volume

    def Quit(self):
        """removes this object from the DBUS connection and exits"""
        loop.quit()



class VolumeWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="ProgressBar Demo")
        self.set_position(Gtk.WindowPosition.CENTER)
        self.resize(500, 100)
        #self.resize(Gdk.Screen.get_default())
        self.set_decorated(False)
        #self.set_modal(True)
        self.set_border_width(10)

        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        self.progressbar = Gtk.ProgressBar()
        self.progressbar.set_show_text(True)
        self.add(self.vbox)
        self.vbox.pack_start(self.progressbar, True, True, 0)
        Keybinder.init()
        Keybinder.bind(0x1008ff13, lambda *_: self.change_volume('+10'))
        Keybinder.bind(0x1008ff11, lambda *_: self.change_volume('-10'))
        Keybinder.bind(0x1008ff12, lambda *_: self.toggle_mute())

    @property
    def volume(self):
        return int(os.popen('pamixer --get-volume').read())
    @volume.setter
    def volume(self, value):
        os.system(f'pamixer --set-volume {int(value)}')
        self.progressbar.set_fraction(value/100)
        self.progressbar.set_text(f'{value}%')
        return value

    def change_volume(self, s):
        if s[0] in '+-':
            self.volume += int(s)
        else:
            self.volume = int(s)
        return self.volume
    
    def toggle_mute(self):
        os.system('pamixer -t')

    @property
    def muted(self):
        return os.popen('pamixer --get-mute').read() == 'true'

    def draw(self, timeout=1500):
        self.set_keep_above(True)
        self.show_all()
        GLib.timeout_add(timeout, self.hide)
        #GLib.timeout_add(timeout, Gtk.main_quit)

    #def on_timeout(self, user_data):
    #    """
    #    Update value on the progress bar
    #    """
    #    if self.activity_mode:
    #        self.progressbar.pulse()
    #    else:
    #        new_value = self.progressbar.get_fraction() + 0.01

    #        if new_value > 1:
    #            new_value = 0

    #        self.progressbar.set_fraction(new_value)

    #    # As this is a timeout function, return True so that it
    #    # continues to get called
    #    return True



if __name__ == '__main__':
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    bus = SessionBus()
    try:
        client = bus.get("net.lew21.pydbus.ClientServerExample")
        client.Draw()
        if arg is not None:
            print(client.Set(arg))
        sys.exit(0)
    except GLib.Error:
        win = VolumeWindow()
        bus.publish("net.lew21.pydbus.ClientServerExample", VolumeDBUSService(win))
        win.connect("destroy", Gtk.main_quit)
        win.draw()
        if arg is not None:
            win.change_volume(arg)
        
    Gtk.main()
