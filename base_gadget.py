import io, logging, os, sys, requests
from logging.handlers import TimedRotatingFileHandler
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QRectF
from PyQt5.QtGui import QColor, QFont, QPainter, QPainterPath, QPixmap, QImage, QLinearGradient, QPen, QBrush
from PyQt5.QtWidgets import QWidget, QLabel, QGraphicsDropShadowEffect, QMenu, QAction, QMessageBox, QApplication
from PIL import Image as PilImage, ImageFile
import config as cfg

# ── LOGGING KONFIGŪRACIJA ───────────────────────────────────────────────────
def _exe_dir():
    if hasattr(sys, '_MEIPASS'):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

log_file = os.path.join(_exe_dir(), "gadget.log")
handler = TimedRotatingFileHandler(log_file, when="H", interval=1, backupCount=24, encoding="utf-8")
handler.suffix = "%Y-%m-%d_%H.%M.%S.log"

logging.basicConfig(
    handlers=[handler],
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s"
)
for lib in ["urllib3", "aiohttp", "PIL"]:
    logging.getLogger(lib).setLevel(logging.CRITICAL)

def log_ui(msg):
    logging.debug(f"DEBUG_UI: {msg}")

ImageFile.LOAD_TRUNCATED_IMAGES = True

# ── PAGALBINĖS FUNKCIJOS ──────────────────────────────────────────────────────
def add_shadow(widget):
    log_ui(f"add_shadow elementui: {widget}")
    fx = QGraphicsDropShadowEffect(widget)
    fx.setBlurRadius(cfg.SHADOW_BLUR)
    fx.setOffset(0, cfg.SHADOW_OFFSET)
    fx.setColor(QColor(0, 0, 0, cfg.SHADOW_ELEM_ALPHA))
    widget.setGraphicsEffect(fx)

def lbl(text, size=11, bold=False, color=cfg.T_WHITE, wrap=0):
    l = QLabel(str(text))
    l.setFont(QFont(cfg.FONT_FAMILY, size, QFont.Bold if bold else QFont.Normal))
    l.setStyleSheet(f"color: {color}; background: transparent; border: none;")
    if wrap:
        l.setWordWrap(True)
        l.setMaximumWidth(wrap)
    return l

def fetch_pixmap(url, w=72, h=50):
    px = QPixmap(w, h)
    px.fill(QColor(100, 100, 100, 50))
    if not url: return px
    try:
        log_ui(f"fetch_pixmap užklausa: {url}")
        resp = requests.get(url, timeout=3)
        resp.raise_for_status()
        img = PilImage.open(io.BytesIO(resp.content)).convert("RGBA").resize((w, h))
        return QPixmap.fromImage(QImage(img.tobytes(), w, h, QImage.Format_RGBA8888))
    except Exception as e:
        logging.error(f"fetch_pixmap klaida ({url}): {e}")
        return px

class RoundedPixmapLabel(QLabel):
    def __init__(self, radius=5, parent=None):
        super().__init__(parent)
        self._radius = radius
        self._pixmap = QPixmap()

    def setPixmap(self, a0):
        self._pixmap = a0
        self.update()

    def paintEvent(self, a0):
        if self._pixmap.isNull():
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), self._radius, self._radius)
        p.setClipPath(path)
        p.drawPixmap(self.rect(), self._pixmap)

# ── BAZINĖS KLASĖS ────────────────────────────────────────────────────────────
class FetchWorker(QThread):
    done = pyqtSignal(object)
    def __init__(self, func, parent=None):
        super().__init__(parent)
        self.func = func
    def run(self):
        try:
            log_ui(f"Gija paleista: {self.func}")
            result = self.func()
            logging.warning(f"FetchWorker sėkmingai: {self.func.__name__ if hasattr(self.func, '__name__') else 'lambda'}")
            self.done.emit(result)
        except Exception as e:
            logging.error(f"FetchWorker klaida: {e}", exc_info=True)
            self.done.emit(None)

class RoundedWindow(QWidget):
    UPDATE_INTERVAL = 900
    def __init__(self, bg, border, grad=None):
        super().__init__()
        self.bg, self.border, self.grad = bg, border, grad
        self.active_threads = []
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.pad, self.remaining = cfg.SHADOW_SIZE, self.UPDATE_INTERVAL
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(1000)

    def _tick(self):
        if self.remaining % 300 == 0:
            log_ui(f"{self.__class__.__name__} heartbeat: {self.remaining}s")
        if self.remaining <= 0:
            self.remaining = self.UPDATE_INTERVAL
            self.active_threads = [w for w in self.active_threads if w.isRunning()]
            self._start_fetch()
        self.remaining -= 1

    def _cleanup(self, w):
        if w in self.active_threads: self.active_threads.remove(w)

    def _spawn(self, func, slot):
        self.active_threads = [w for w in self.active_threads if w.isRunning()]
        w = FetchWorker(func, self)
        self.active_threads.append(w)
        w.done.connect(slot)
        w.done.connect(lambda: self._cleanup(w))
        w.finished.connect(w.deleteLater)
        w.start()

    def paintEvent(self, a0):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        rect = QRectF(self.rect()).adjusted(self.pad, self.pad, -self.pad, -self.pad)
        p.setPen(Qt.NoPen)
        for i in range(int(self.pad), 0, -1):
            alpha = int(cfg.SHADOW_ALPHA * (1 - i/self.pad) ** cfg.SHADOW_FALLOFF)
            if alpha < 1: continue
            p.setBrush(QColor(0, 0, 0, alpha))
            p.drawRoundedRect(rect.adjusted(-i, -i, i, i), cfg.CORNER_RADIUS + i*0.5, cfg.CORNER_RADIUS + i*0.5)
        path = QPainterPath(); path.addRoundedRect(rect, cfg.CORNER_RADIUS, cfg.CORNER_RADIUS)
        if self.grad:
            g = QLinearGradient(rect.topLeft(), rect.bottomLeft())
            g.setColorAt(0.0, self.bg); g.setColorAt(1.0, self.grad)
            p.fillPath(path, QBrush(g))
        else: p.fillPath(path, QBrush(self.bg))
        p.setPen(QPen(self.border, 1.2)); p.drawPath(path)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background: #1e1e2e; color: white; border: 1px solid #446; padding: 4px; }")
        for txt, slot in [("↺ Atnaujinti", self._start_fetch), ("ℹ Apie", self._show_about), ("✕ Uždaryti", QApplication.quit)]:
            a = QAction(txt, self); a.triggered.connect(slot); menu.addAction(a)
        menu.exec_(event.globalPos())

    def _show_about(self):
        QMessageBox.information(self, "Apie", "Darbalaukio gadgetas\nAtnaujinimas kas 15 min.")
