from PyObjCTools import AppHelper
from Foundation import NSObject, NSTimer
from AppKit import NSApplication, NSApp, NSStatusBar, NSMenu, NSMenuItem, NSSound, NSAlert, NSTextField, NSView

class TimerApp(NSObject):
    def applicationDidFinishLaunching_(self, notification):
        NSApp.setActivationPolicy_(1)  # Ẩn icon trên Dock
        
        self.status_bar = NSStatusBar.systemStatusBar()
        self.status_item = self.status_bar.statusItemWithLength_(-1)
        self.status_item.setTitle_("⏳")
        
        self.menu = NSMenu.alloc().init()
        
        self.timers = {
            "3 sec (Test)": 3,
            "1 min": 60,
            "3 min": 180,
            "5 min": 300,
            "10 min": 600,
            "15 min": 900,
            "30 min": 1800,
            "1 hr": 3600,
            "2 hr": 7200
        }
        
        self.active_timers = []  # Danh sách các timer đang chạy
        self.custom_timers = []  # Danh sách các timer được tạo thủ công
        
        for label, seconds in self.timers.items():
            menu_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                label, b"startTimer:", ""
            )
            menu_item.setRepresentedObject_(seconds)
            self.menu.addItem_(menu_item)
        
        self.menu.addItem_(NSMenuItem.separatorItem())
        self.custom_timer_separator = NSMenuItem.separatorItem()
        self.menu.addItem_(self.custom_timer_separator)
        
        self.custom_timer_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "+", b"showCustomTimerDialog:", ""
        )
        self.menu.addItem_(self.custom_timer_item)
        
        self.menu.addItem_(NSMenuItem.separatorItem())
        
        self.quit_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Quit", b"terminate:", "q"
        )
        self.menu.addItem_(self.quit_item)
        
        self.status_item.setMenu_(self.menu)
        self.update_timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            1.0, self, b"updateCountdown:", None, True
        )
    
    def startTimer_(self, sender):
        duration = sender.representedObject()
        self.active_timers.append((duration, sender))
        self.active_timers.sort()
        self.updateMenuTitle()
    
    def updateCountdown_(self, sender):
        if self.active_timers:
            self.active_timers[0] = (self.active_timers[0][0] - 1, self.active_timers[0][1])
            if self.active_timers[0][0] <= 0:
                self.playSoundRepeatedly()
                finished_timer = self.active_timers.pop(0)
                if finished_timer[1] in self.custom_timers:
                    self.menu.removeItem_(finished_timer[1])
                    self.custom_timers.remove(finished_timer[1])
            self.updateMenuTitle()
    
    def updateMenuTitle(self):
        if self.active_timers:
            minutes = self.active_timers[0][0] // 60
            seconds = self.active_timers[0][0] % 60
            self.status_item.setTitle_(f"⏳ {minutes}:{seconds:02d}")
        else:
            self.status_item.setTitle_("⏳")
    
    def playSoundRepeatedly(self):
        self.sound_count = 0
        self.sound_timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            1.0, self, b"playSound:", None, True
        )
    
    def playSound_(self, sender):
        if self.sound_count < 10:
            sound = NSSound.soundNamed_("Glass")
            if sound:
                sound.play()
            self.sound_count += 1
        else:
            self.sound_timer.invalidate()
            self.sound_timer = None
    
    def showCustomTimerDialog_(self, sender):
        NSApp.activateIgnoringOtherApps_(True)
        
        alert = NSAlert.alloc().init()
        alert.setMessageText_("Set Custom Timer")
        alert.setInformativeText_("Enter hours and minutes")
        
        view = NSView.alloc().initWithFrame_(((0, 0), (200, 50)))
        hour_field = NSTextField.alloc().initWithFrame_(((10, 10), (50, 24)))
        minute_field = NSTextField.alloc().initWithFrame_(((70, 10), (50, 24)))
        
        hour_field.setPlaceholderString_("Hrs")
        minute_field.setPlaceholderString_("Mins")
        
        view.addSubview_(hour_field)
        view.addSubview_(minute_field)
        
        alert.setAccessoryView_(view)
        
        alert.addButtonWithTitle_("Start")
        alert.addButtonWithTitle_("Cancel")
        
        response = alert.runModal()
        if response == 1000:
            try:
                hours = int(hour_field.stringValue()) if hour_field.stringValue() else 0
                minutes = int(minute_field.stringValue()) if minute_field.stringValue() else 0
                total_seconds = (hours * 3600) + (minutes * 60)
                if total_seconds > 0:
                    custom_timer = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                        f"Custom: {hours}h {minutes}m", b"startTimer:", ""
                    )
                    custom_timer.setRepresentedObject_(total_seconds)
                    self.menu.insertItem_aboveItem_(custom_timer, self.custom_timer_separator)
                    self.custom_timers.append(custom_timer)
                    self.startTimer_(custom_timer)
            except ValueError:
                pass
    
if __name__ == "__main__":
    app = NSApplication.sharedApplication()
    delegate = TimerApp.alloc().init()
    app.setDelegate_(delegate)
    AppHelper.runEventLoop()