import subprocess
import config

# ── App Launcher (macOS) ─────────────────────────────────
# Uses macOS 'open' command to launch applications
# No extra libraries needed!

class AppLauncher:
    def __init__(self):
        self.launch_cooldown = 0
        self.cooldown_frames = 60  # wait 60 frames between launches
                                   # prevents same app opening multiple times

    def launch(self, app_name):
        # Use macOS 'open -a' command to open any app by name
        subprocess.Popen(["open", "-a", app_name])
        print(f"[App] Launching {app_name}")

    def update(self, gesture):
        import gesture_recognizer as gr

        # Tick down cooldown every frame
        if self.launch_cooldown > 0:
            self.launch_cooldown -= 1
            return None  # still cooling down, don't launch anything

        launched = None

        # Thumb Up → Open Browser
        if gesture == gr.GESTURE_THUMB_UP:
            self.launch(config.APP_BROWSER)
            launched = config.APP_BROWSER
            self.launch_cooldown = self.cooldown_frames

        # Two Fingers → Open Code Editor
        elif gesture == gr.GESTURE_TWO_FINGERS:
            self.launch(config.APP_EDITOR)
            launched = config.APP_EDITOR
            self.launch_cooldown = self.cooldown_frames

        # Fist → Open Terminal
        elif gesture == gr.GESTURE_FIST:
            self.launch(config.APP_TERMINAL)
            launched = config.APP_TERMINAL
            self.launch_cooldown = self.cooldown_frames

        return launched