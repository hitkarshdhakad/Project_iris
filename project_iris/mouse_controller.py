import pyautogui
import config
import utils

# Disable pyautogui's fail-safe corner (optional, comment out if you want it)
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0  # Remove default delay between actions for smooth movement

# ── Mouse Controller ─────────────────────────────────────
class MouseController:
    def __init__(self):
        self.smoother         = utils.SmoothCursor()
        self.click_cooldown   = 0
        self.right_click_cooldown = 0
        self.is_dragging      = False

    def move_cursor(self, hand_landmarks, frame_w, frame_h):
        lm = hand_landmarks.landmark

        # Use index fingertip (landmark 8) to control cursor
        index_tip = lm[8]

        # Convert from camera space (0.0-1.0) to screen space
        # We flip x because camera is mirrored
        raw_x = (1 - index_tip.x) * config.SCREEN_WIDTH
        raw_y = index_tip.y * config.SCREEN_HEIGHT

        # Apply smoothing so cursor doesn't jitter
        smooth_x, smooth_y = self.smoother.smooth(raw_x, raw_y)

        # Clamp to screen boundaries
        smooth_x = max(0, min(config.SCREEN_WIDTH  - 1, smooth_x))
        smooth_y = max(0, min(config.SCREEN_HEIGHT - 1, smooth_y))

        pyautogui.moveTo(smooth_x, smooth_y)

    def try_click(self, gesture):
        import gesture_recognizer as gr

        # Tick down cooldown every frame
        if self.click_cooldown > 0:
            self.click_cooldown -= 1
        if self.right_click_cooldown > 0:
            self.right_click_cooldown -= 1

        # Left click on pinch
        if gesture == gr.GESTURE_PINCH and self.click_cooldown == 0:
            pyautogui.click()
            self.click_cooldown = config.CLICK_COOLDOWN_FRAMES
            print("[Mouse] Left click")

        # Right click on two fingers
        elif gesture == gr.GESTURE_TWO_FINGERS and self.right_click_cooldown == 0:
            pyautogui.rightClick()
            self.right_click_cooldown = config.CLICK_COOLDOWN_FRAMES
            print("[Mouse] Right click")

    def update(self, gesture, hand_landmarks, frame_w, frame_h):
        import gesture_recognizer as gr

        # Always move cursor when index finger is up
        if gesture in [gr.GESTURE_INDEX_ONLY,
                       gr.GESTURE_PINCH,
                       gr.GESTURE_TWO_FINGERS]:
            self.move_cursor(hand_landmarks, frame_w, frame_h)

        # Handle clicks
        self.try_click(gesture)