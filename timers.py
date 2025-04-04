from PyObjCTools import AppHelper
from Foundation import NSObject, NSTimer, NSRunLoop, NSRunLoopCommonModes
from AppKit import NSApplication, NSApp, NSStatusBar, NSMenu, NSMenuItem, NSSound, NSAlert, NSTextField, NSView
import os

class TimerApp(NSObject):
    def applicationDidFinishLaunching_(self, notification):
        NSApp.setActivationPolicy_(1)  # Ẩn icon trên Dock
        
        self.status_bar = NSStatusBar.systemStatusBar()
        self.status_item = self.status_bar.statusItemWithLength_(65)  # Cố định độ dài 120 pixel
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
        
        self.active_timers = []  # Danh sách timer: (duration, menu_item, is_paused)
        self.timer_items = []  # Danh sách các mục menu cho timer
        
        self.timer_separator = NSMenuItem.separatorItem()
        
        for label, seconds in self.timers.items():
            menu_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                label, b"startTimer:", ""
            )
            menu_item.setRepresentedObject_(seconds)
            self.menu.addItem_(menu_item)
        
        self.menu.addItem_(NSMenuItem.separatorItem())
        
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
        NSRunLoop.currentRunLoop().addTimer_forMode_(
            self.update_timer, NSRunLoopCommonModes
        )
    
    def startTimer_(self, sender):
        duration = sender.representedObject()
        self.active_timers.append((duration, sender, False))
        self.updateMenuWithTimers()
    
    def updateCountdown_(self, sender):
        if self.active_timers:
            updated_timers = []
            for duration, menu_item, is_paused in self.active_timers:
                if not is_paused:
                    duration -= 1
                if duration > 0:
                    updated_timers.append((duration, menu_item, is_paused))
                else:
                    self.playSound_(None)
            self.active_timers = updated_timers
            self.updateMenuWithTimers()
            self.updateMenuTitle()  # Đảm bảo cập nhật thanh menu
    
    def updateMenuTitle(self):
        if self.active_timers:
            min_duration = min(t[0] for t in self.active_timers)
            minutes = min_duration // 60
            seconds = min_duration % 60
            self.status_item.setTitle_(f"⏳ {minutes:02d}:{seconds:02d}")  # Thêm padding số 0
        else:
            self.status_item.setTitle_("⏳")
    
    def updateMenuWithTimers(self):
        # Xóa các mục timer cũ
        for item in self.timer_items:
            self.menu.removeItem_(item)
        if self.menu.itemArray().containsObject_(self.timer_separator):
            self.menu.removeItem_(self.timer_separator)
        self.timer_items = []
        
        # Thêm các mục timer mới
        for i, (duration, _, is_paused) in enumerate(self.active_timers):
            minutes = duration // 60
            seconds = duration % 60
            # Mục Pause/Play
            pause_play_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                f"Timer {i+1}: {minutes:02d}:{seconds:02d} [{'Pause' if not is_paused else 'Play'}]",
                b"toggleTimerPause:",
                ""
            )
            pause_play_item.setRepresentedObject_(i)
            self.menu.insertItem_atIndex_(pause_play_item, i * 2)
            self.timer_items.append(pause_play_item)
            
            # Mục Cancel
            cancel_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                f"Cancel Timer {i+1}",
                b"toggleTimerCancel:",
                ""
            )
            cancel_item.setRepresentedObject_(i)
            self.menu.insertItem_atIndex_(cancel_item, i * 2 + 1)
            self.timer_items.append(cancel_item)
        
        # Thêm gạch ngang sau các timer
        if self.active_timers:
            self.menu.insertItem_atIndex_(self.timer_separator, len(self.active_timers) * 2)
    
    def toggleTimerPause_(self, sender):
        index = sender.representedObject()
        duration, menu_item, is_paused = self.active_timers[index]
        self.active_timers[index] = (duration, menu_item, not is_paused)
        self.updateMenuWithTimers()
    
    def toggleTimerCancel_(self, sender):
        index = sender.representedObject()
        del self.active_timers[index]
        self.updateMenuWithTimers()
        self.updateMenuTitle()  # Cập nhật lại thanh menu khi hủy
    
    def playSound_(self, sender):
        sound_path = os.path.join(os.path.dirname(__file__), "alert.mp3")
        sound = NSSound.alloc().initWithContentsOfFile_byReference_(sound_path, True)
        if sound:
            sound.play()

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
                    self.active_timers.append((total_seconds, None, False))
                    self.updateMenuWithTimers()
            except ValueError:
                pass

if __name__ == "__main__":
    app = NSApplication.sharedApplication()
    delegate = TimerApp.alloc().init()
    app.setDelegate_(delegate)
    AppHelper.runEventLoop()