import io
import sys
from datetime import datetime

import requests
from PIL import Image as PilImage, ImageFile
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QUrl, QRectF
from PyQt5.QtGui import QColor, QFont, QPainter, QPainterPath, QPixmap, QImage, QLinearGradient, QPen, QBrush, \
    QDesktopServices
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGraphicsDropShadowEffect

import config as cfg
import news
import meteo_lt
import nordpool

ImageFile.LOAD_TRUNCATED_IMAGES = True


# ── PAGALBINĖS FUNKCIJOS ──────────────────────────────────────────────────────

def add_shadow(widget):
    fx = QGraphicsDropShadowEffect(widget)
    fx.setBlurRadius(cfg.SHADOW_BLUR)
    fx.setOffset(0, cfg.SHADOW_OFFSET)
    fx.setColor(QColor(0, 0, 0, cfg.SHADOW_ELEM_ALPHA))
    widget.setGraphicsEffect(fx)


def lbl(text, size=11, bold=False, color=cfg.T_WHITE, wrap=0):
    l = QLabel(text)
    l.setFont(QFont(cfg.FONT_FAMILY, size, QFont.Bold if bold else QFont.Normal))
    l.setStyleSheet(f"color: {color}; background: transparent; border: none;")
    if wrap:
        l.setWordWrap(True)
        l.setMaximumWidth(wrap)
    return l


def fetch_pixmap(url, w=72, h=50):
    px = QPixmap(w, h)
    px.fill(QColor(100, 100, 100, 50))

    if not url:
        return px

    try:
        resp = requests.get(url, timeout=3)
        resp.raise_for_status()
        img = PilImage.open(io.BytesIO(resp.content))
        img = img.convert("RGBA").resize((w, h))
        return QPixmap.fromImage(
            QImage(img.tobytes(), w, h, QImage.Format_RGBA8888)
        )
    except Exception:
        return px


# ── DUOMENŲ KROVĖJAS ─────────────────────────────────────────────────────────

class FetchWorker(QThread):
    done = pyqtSignal(object)

    def __init__(self, func, parent=None):
        super().__init__(parent)
        self.func = func

    def run(self):
        try:
            self.done.emit(self.func())
        except Exception:
            self.done.emit(None)


# ── BAZINIS LANGAS ───────────────────────────────────────────────────────────

class RoundedWindow(QWidget):
    UPDATE_INTERVAL = 900

    def __init__(self, bg, border, grad=None):
        super().__init__()
        self.bg, self.border, self.grad = bg, border, grad
        self.active_threads = []
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.pad = cfg.SHADOW_SIZE
        self.remaining = self.UPDATE_INTERVAL
        t = QTimer(self)
        t.timeout.connect(self._tick)
        t.start(1000)

    def _tick(self):
        if self.remaining <= 0:
            self.remaining = self.UPDATE_INTERVAL
            self._start_fetch()
        self.remaining -= 1

    def _start_fetch(self):
        pass

    def _cleanup(self, w):
        if w in self.active_threads:
            self.active_threads.remove(w)
        w.finished.connect(w.deleteLater)

    def _spawn(self, func, slot):
        w = FetchWorker(func, self)
        self.active_threads.append(w)
        w.done.connect(slot)
        w.done.connect(lambda: self._cleanup(w))
        w.start()

    def paintEvent(self, a0):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        pad = float(self.pad)
        rect = QRectF(self.rect()).adjusted(pad, pad, -pad, -pad)

        p.setPen(Qt.NoPen)
        for i in range(int(pad), 0, -1):
            t = i / pad
            alpha = int(cfg.SHADOW_ALPHA * (1 - t) ** cfg.SHADOW_FALLOFF)
            if alpha < 1:
                continue
            p.setBrush(QColor(0, 0, 0, alpha))
            r = cfg.CORNER_RADIUS + i * 0.5
            p.drawRoundedRect(rect.adjusted(-i, -i, i, i), r, r)

        path = QPainterPath()
        path.addRoundedRect(rect, cfg.CORNER_RADIUS, cfg.CORNER_RADIUS)
        if self.grad:
            g = QLinearGradient(rect.topLeft(), rect.bottomLeft())
            g.setColorAt(0.0, self.bg)
            g.setColorAt(1.0, self.grad)
            p.fillPath(path, QBrush(g))
        else:
            p.fillPath(path, QBrush(self.bg))
        p.setPen(QPen(self.border, 1.2))
        p.drawPath(path)


# ── ORŲ BLOKAS ───────────────────────────────────────────────────────────────

class WeatherWidget(RoundedWindow):
    def __init__(self, x, y):
        super().__init__(cfg.BLUE_BLOCK_BG, cfg.BLUE_BLOCK_BRD, cfg.BLUE_BLOCK_GRAD)
        self.setFixedWidth(cfg.WIN_WIDTH + 2 * self.pad)
        self.move(x, y)
        self.last_update = '--:--'

        lo = QVBoxLayout(self)
        lo.setContentsMargins(self.pad + 15, self.pad + 5, self.pad + 15, self.pad + 10)

        self.city_lbl = lbl("Kraunama...", 14, True, cfg.T_ACCENT)
        self.temp_lbl = lbl("", 20, True)
        self.feels_lbl = lbl("", 12, True, "#d9e8ff")
        self.timer_lbl = lbl("", 7, color=cfg.T_MUTED)
        self.timer_lbl.setAlignment(Qt.AlignRight)
        self.left_details = lbl("", 9, color="#d9e8ff")
        self.right_details = lbl("", 9, color="#d9e8ff")
        self.right_details.setAlignment(Qt.AlignRight)

        self.icon_lbl = QLabel()
        self.icon_lbl.setFixedSize(48, 48)
        self.icon_lbl.setAlignment(Qt.AlignCenter)

        add_shadow(self.temp_lbl)
        add_shadow(self.feels_lbl)
        add_shadow(self.icon_lbl)

        cx = QHBoxLayout()
        cx.addStretch()
        cx.addWidget(self.temp_lbl)
        cx.addStretch()

        h1 = QHBoxLayout()
        h1.addWidget(self.city_lbl)
        h1.addLayout(cx)
        h1.addWidget(self.feels_lbl)

        h2 = QHBoxLayout()
        h2.addWidget(self.left_details, 1)
        h2.addWidget(self.icon_lbl)
        h2.addWidget(self.right_details, 1)

        lo.addLayout(h1)
        lo.addLayout(h2)
        lo.addWidget(self.timer_lbl)
        self._start_fetch()

    def _start_fetch(self):
        self._spawn(meteo_lt.get_weather_data, self._on_data)

    def _on_data(self, res):
        if not res:
            return
        self.city_lbl.setText(res[0])
        self.temp_lbl.setText(res[1])
        self.feels_lbl.setText(res[2])
        self.left_details.setText(res[3])
        self.right_details.setText(res[4])
        self.icon_lbl.setPixmap(QPixmap(res[5]).scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.last_update = datetime.now().strftime("%H:%M")
        self.adjustSize()

    def _tick(self):
        super()._tick()
        m, s = divmod(self.remaining, 60)
        self.timer_lbl.setText(f"Atnaujinta: {self.last_update} | Kitąkart po: {m:02d}:{s:02d}")


# ── NORDPOOL BLOKAS ──────────────────────────────────────────────────────────

class NordPoolWidget(RoundedWindow):
    def __init__(self, x, y):
        super().__init__(cfg.DARK_BLOCK_BG, cfg.DARK_BLOCK_BRD)
        self.setFixedWidth(cfg.WIN_WIDTH + 2 * self.pad)
        self.move(x, y)
        self.setFixedHeight(60 + 2 * self.pad)

        lo = QHBoxLayout(self)
        lo.setContentsMargins(self.pad + 15, self.pad, self.pad + 15, self.pad)
        self.info_lbl = lbl("Kraunama...", 10)
        lo.addWidget(self.info_lbl, 1)

        nordpool_lbl = lbl("NordPool", 16, True, cfg.T_ACCENT)
        add_shadow(nordpool_lbl)
        lo.addWidget(nordpool_lbl)
        self._start_fetch()

    def _start_fetch(self):
        self._spawn(nordpool.get_nordpool_info, lambda r: self.info_lbl.setText(r or "Klaida"))


# ── NAUJIENŲ BLOKAS ──────────────────────────────────────────────────────────

class RoundedPixmapLabel(QLabel):
    def __init__(self, radius=5):
        super().__init__()
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


class ClickableLabel(QLabel):
    def __init__(self, text, url):
        super().__init__(text)
        self._url = url

    def mousePressEvent(self, ev):
        QDesktopServices.openUrl(QUrl(self._url))


class NewsRow(QWidget):
    def __init__(self, title, link, img_url, parent_win):
        super().__init__()
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 2, 0, 2)
        lay.setSpacing(10)

        self.img = RoundedPixmapLabel(radius=5)
        self.img.setFixedSize(72, 50)
        self.img.setPixmap(fetch_pixmap(""))
        lay.addWidget(self.img)

        t = ClickableLabel(f"• {title}", link)
        t.setFont(QFont(cfg.FONT_FAMILY, 9))
        t.setStyleSheet(f"color: {cfg.T_NEWS_LNK}; background: transparent; border: none;")
        t.setWordWrap(True)
        t.setMaximumWidth(cfg.WIN_WIDTH - 110)
        t.setCursor(Qt.PointingHandCursor)
        lay.addWidget(t, 1)

        if img_url:
            parent_win._spawn(lambda u=img_url: fetch_pixmap(u), self.img.setPixmap)


class NewsSection(QWidget):
    def __init__(self, title, parent_win, show_line=True):
        super().__init__()
        self._pw = parent_win
        self._line = show_line
        self.lay = QVBoxLayout(self)
        self.lay.setContentsMargins(0, 2, 0, 8 if show_line else 2)
        self.lay.setSpacing(2)
        self.lay.addWidget(lbl(title, 9, True, cfg.T_NEWS_HDR))

    def set_items(self, items):
        while self.lay.count() > 1:
            item = self.lay.takeAt(1)
            if item:
                w = item.widget()
                if w:
                    w.deleteLater()
        for t, l, i in items:
            self.lay.addWidget(NewsRow(t, l, i, self._pw))

    def paintEvent(self, a0):
        if self._line:
            p = QPainter(self)
            p.setPen(QPen(QColor(0, 0, 0, 30), 1))
            p.drawLine(0, self.height() - 1, self.width(), self.height() - 1)


class NewsWidget(RoundedWindow):
    def __init__(self, x, y):
        super().__init__(cfg.LIGHT_BLOCK_BG, cfg.LIGHT_BLOCK_BRD)
        self.setFixedWidth(cfg.WIN_WIDTH + 2 * self.pad)
        self.move(x, y)

        lo = QVBoxLayout(self)
        lo.setContentsMargins(self.pad + 12, self.pad + 8, self.pad + 12, self.pad + 18)
        lo.setSpacing(0)

        self.s1 = NewsSection("15min naujienos", self)
        lo.addWidget(self.s1)
        self.s2 = NewsSection("LRT naujienos", self)
        lo.addWidget(self.s2)
        self.s3 = NewsSection("Delfi naujienos", self)
        lo.addWidget(self.s3)
        self.s4 = NewsSection("Verslo žinios", self, False)
        lo.addWidget(self.s4)
        self._start_fetch()

    def _start_fetch(self):
        self._spawn(
            lambda: (news.get_15min_news(), news.get_lrt_news(),
                     news.get_delfi_news(), news.get_vz_news()),
            self._on_data
        )

    def _on_data(self, res):
        if not res:
            return
        for s, r in zip([self.s1, self.s2, self.s3, self.s4], res):
            s.set_items(r)
        QTimer.singleShot(100, self.adjustSize)


# ── PAGRINDINĖ PROGRAMA ───────────────────────────────────────────────────────

class GadgetApp:
    def __init__(self):
        self._widgets = []
        screen = QApplication.primaryScreen()
        x = (screen.geometry().width() if screen else 1920) - cfg.WIN_WIDTH - cfg.X_OFFSET - cfg.SHADOW_SIZE
        self._show(WeatherWidget(x, cfg.Y_OFFSET))
        QTimer.singleShot(800, lambda: self._init_rest(x))

    def _show(self, w):
        w.show()
        self._widgets.append(w)
        return w

    def _init_rest(self, x):
        y = self._widgets[-1].y() + self._widgets[-1].height() + cfg.GAP
        for cls in [NordPoolWidget, NewsWidget]:
            self._show(cls(x, y))
            y += self._widgets[-1].height() + cfg.GAP


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    GadgetApp()
    sys.exit(app.exec_())
