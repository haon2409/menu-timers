from PyObjCTools import AppHelper
from Foundation import NSObject, NSTimer, NSRunLoop, NSRunLoopCommonModes, NSMakeSize, NSColor
from AppKit import NSApplication, NSApp, NSStatusBar, NSMenu, NSMenuItem, NSSound, NSAlert, NSTextField, NSView, NSImage, NSAttributedString, NSDictionary, NSFont, NSVariableStatusItemLength
import os

class TimerApp(NSObject):
    def applicationDidFinishLaunching_(self, notification):
        NSApp.setActivationPolicy_(1)  # Ẩn icon trên Dock
        
        self.status_bar = NSStatusBar.systemStatusBar()        
        self.status_item = self.status_bar.statusItemWithLength_(NSVariableStatusItemLength)
        
        # Tải icon từ file icon64.png
        icon_path = os.path.join(os.path.dirname(__file__), "icon64.png")
        self.icon = NSImage.alloc().initWithContentsOfFile_(icon_path)
        if self.icon:
            self.icon.setSize_((22, 22))  # Điều chỉnh kích thước icon
            self.status_item.setImage_(self.icon)
        else:
            self.status_item.setTitle_("⏳")  # Dự phòng nếu không tải được icon
        
        self.menu = NSMenu.alloc().init()
        
        self.timers = {            
            "1 min": 60,
            "3 min": 180,
            "5 min": 300,
            "10 min": 600,
            "15 min": 900,
            "20 min": 1200,
            "30 min": 1800,
            "45 min": 2700,
            "1 hr": 3600            
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
    
    def create_colored_text_image(self, text):
        # Tạo attributed string với màu đen đặc
        attributes = NSDictionary.dictionaryWithObjects_forKeys_(
            [
                NSFont.fontWithName_size_("DSEG7Classic-Regular", 16),  # Tăng kích thước font lên 18
                NSColor.blackColor(),  # Màu chính là đen
                NSColor.blackColor(),  # Màu viền cũng là đen
                -3  # Giá trị âm để stroke đi vào trong (làm đặc chữ)
            ],
            ["NSFont", "NSForegroundColor", "NSStrokeColor", "NSStrokeWidth"]
        )
        attr_string = NSAttributedString.alloc().initWithString_attributes_(text, attributes)
        
        # Tính kích thước của văn bản
        text_size = attr_string.size()
        
        # Tạo hình ảnh với kích thước phù hợp (thêm padding 2px mỗi bên)
        image = NSImage.alloc().initWithSize_(NSMakeSize(text_size.width + 4, text_size.height + 4))
        image.lockFocus()
        attr_string.drawAtPoint_((2, 2))  # Vẽ text với offset 2px để có padding
        image.unlockFocus()
        
        return image
    
    def updateMenuTitle(self):
        if self.active_timers:
            # Khi có timer, hiển thị thời gian với màu #FCC419
            min_duration = min(t[0] for t in self.active_timers)
            minutes = min_duration // 60
            seconds = min_duration % 60
            time_text = f"{minutes:02d}:{seconds:02d}"
            
            # Tạo hình ảnh với văn bản màu #FCC419
            time_image = self.create_colored_text_image(time_text)
            self.status_item.setImage_(time_image)
            self.status_item.setTitle_("")  # Xóa title để chỉ hiển thị hình ảnh
        else:
            # Khi không có timer, hiển thị icon
            if self.icon:
                self.status_item.setImage_(self.icon)
            else:
                self.status_item.setTitle_("⏳")
            self.status_item.setTitle_("")
    
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
            self.updateMenuTitle()
    
    def updateMenuWithTimers(self):
        for item in self.timer_items:
            self.menu.removeItem_(item)
        if self.menu.itemArray().containsObject_(self.timer_separator):
            self.menu.removeItem_(self.timer_separator)
        self.timer_items = []
        
        for i, (duration, _, is_paused) in enumerate(self.active_timers):
            minutes = duration // 60
            seconds = duration % 60
            pause_play_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                f"Timer {i+1}: {minutes:02d}:{seconds:02d} [{'Pause' if not is_paused else 'Play'}]",
                b"toggleTimerPause:",
                ""
            )
            pause_play_item.setRepresentedObject_(i)
            self.menu.insertItem_atIndex_(pause_play_item, i * 2)
            self.timer_items.append(pause_play_item)
            
            cancel_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                f"Cancel Timer {i+1}",
                b"toggleTimerCancel:",
                ""
            )
            cancel_item.setRepresentedObject_(i)
            self.menu.insertItem_atIndex_(cancel_item, i * 2 + 1)
            self.timer_items.append(cancel_item)
        
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
        self.updateMenuTitle()
    
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