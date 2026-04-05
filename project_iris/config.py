import pyautogui

# ── Screen ──────────────────────────────────────────────
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

# ── Camera ──────────────────────────────────────────────
CAM_WIDTH  = 640
CAM_HEIGHT = 480

# ── Gesture Thresholds ──────────────────────────────────
PINCH_THRESHOLD        = 40   # px – thumb+index close = pinch
FINGER_EXTENDED_RATIO  = 0.6  # how straight a finger must be to count as "extended"

# ── Mode Switching ──────────────────────────────────────
MODE_HOLD_FRAMES = 20   # frames a gesture must be held to switch mode

# ── Mouse Smoothing ─────────────────────────────────────
SMOOTHING = 6           # higher = smoother but slightly more lag (range 1-10)

# ── Modes ───────────────────────────────────────────────
MODE_MOUSE  = "MOUSE"
MODE_VOLUME = "VOLUME"
MODE_APP    = "APP"
DEFAULT_MODE = MODE_MOUSE

# ── Click Cooldown ──────────────────────────────────────
CLICK_COOLDOWN_FRAMES = 15  # frames to wait between clicks to avoid double clicks

# ── Volume Control ──────────────────────────────────────
VOLUME_MIN_DIST = 30    # px – minimum thumb-index distance (volume = 0%)
VOLUME_MAX_DIST = 200   # px – maximum thumb-index distance (volume = 100%)

# ── App Launcher ────────────────────────────────────────
APP_BROWSER  = "Safari"
APP_EDITOR   = "Visual Studio Code"
APP_TERMINAL = "Terminal"