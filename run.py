import sys, logging, datetime
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PyQt5.QtCore import pyqtSignal, Qt, QUrl, QTimer
from PyQt5.QtGui import QPixmap, QDesktopServices, QFont, QPen, QColor, QPainter
import config as cfg
import meteo_lt, nordpool, news
from base_gadget import RoundedWindow, lbl, add_shadow, fetch_pixmap, log_ui, RoundedPixmapLabel


class WeatherWidget(RoundedWindow):
    ready = pyqtSignal()
    def __init__(self, x, y):
        super().__init__(cfg.BLUE_BLOCK_BG, cfg.BLUE_BLOCK_BRD, cfg.BLUE_BLOCK_GRAD)
        self._ready_emitted = False
        self.setFixedWidth(cfg.WIN_WIDTH + 2 * self.pad); self.move(x, y)
        self.last_update = '--:--'
        lo = QVBoxLayout(self); lo.setContentsMargins(self.pad + 15, self.pad + 5, self.pad + 15, self.pad + 10)
        self.city_lbl = lbl("Kraunama...", 14, True, cfg.T_ACCENT)
        self.temp_lbl = lbl("", 20, True); self.feels_lbl = lbl("", 12, True, cfg.T_MUTED)
        self.timer_lbl = lbl("", 7, color=cfg.T_MUTED); self.timer_lbl.setAlignment(Qt.AlignRight)
        self.left_details = lbl("", 9); self.right_details = lbl("", 9); self.right_details.setAlignment(Qt.AlignRight)
        self.icon_lbl = QLabel(); self.icon_lbl.setFixedSize(48, 48)
        add_shadow(self.temp_lbl); add_shadow(self.icon_lbl)
        h1 = QHBoxLayout(); h1.addWidget(self.city_lbl); h1.addStretch(); h1.addWidget(self.temp_lbl); h1.addStretch(); h1.addWidget(self.feels_lbl)
        h2 = QHBoxLayout(); h2.addWidget(self.left_details, 1); h2.addWidget(self.icon_lbl); h2.addWidget(self.right_details, 1)
        lo.addLayout(h1); lo.addLayout(h2); lo.addWidget(self.timer_lbl)
        self._start_fetch()

    def _start_fetch(self): self._spawn(meteo_lt.get_weather_data, self._on_data)

    def _on_data(self, res):
        if not res: return
        try:
            self.city_lbl.setText(res[0]); self.temp_lbl.setText(res[1]); self.feels_lbl.setText(res[2])
            self.left_details.setText(res[3]); self.right_details.setText(res[4])
            px = QPixmap(res[5])
            if not px.isNull(): self.icon_lbl.setPixmap(px.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.last_update = datetime.datetime.now().strftime("%H:%M")
            self.adjustSize()
            if not self._ready_emitted: self._ready_emitted = True; self.ready.emit()
        except Exception as e: logging.error(f"Weather UI error: {e}")

    def _tick(self):
        super()._tick()
        m, s = divmod(self.remaining, 60)
        self.timer_lbl.setText(f"Atnaujinta: {self.last_update} | Kitąkart po: {m:02d}:{s:02d}")

class NordPoolWidget(RoundedWindow):
    def __init__(self, x, y):
        super().__init__(cfg.DARK_BLOCK_BG, cfg.DARK_BLOCK_BRD)
        self.setFixedWidth(cfg.WIN_WIDTH + 2 * self.pad); self.move(x, y); self.setFixedHeight(60 + 2 * self.pad)
        lo = QHBoxLayout(self); lo.setContentsMargins(self.pad + 15, self.pad, self.pad + 15, self.pad)
        self.info_lbl = lbl("Kraunama...", 10)
        np_lbl = lbl("NordPool", 16, True, cfg.T_ACCENT); add_shadow(np_lbl)
        lo.addWidget(self.info_lbl, 1); lo.addWidget(np_lbl)
        self._start_fetch()

    def _start_fetch(self): self._spawn(nordpool.get_nordpool_info, self._on_data)
    def _on_data(self, res): self.info_lbl.setText(res or "Klaida")

# ── NAUJIENŲ PAPILDOMOS KLASĖS ──
class ClickableLabel(QLabel):
    def __init__(self, text, url):
        super().__init__(text); self._url = url
    def mousePressEvent(self, ev):
        try: QDesktopServices.openUrl(QUrl(self._url))
        except Exception as e: logging.error(f"Nuorodos klaida: {e}")

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
        super().__init__(); self._pw = parent_win; self._line = show_line
        self.lay = QVBoxLayout(self); self.lay.setContentsMargins(0, 2, 0, 8 if show_line else 2); self.lay.setSpacing(2)
        self.lay.addWidget(lbl(title, 9, True, cfg.T_NEWS_HDR))
    def set_items(self, items):
        while self.lay.count() > 1:
            it = self.lay.takeAt(1); it.widget().deleteLater() if it.widget() else None
        for t, l, i in items: self.lay.addWidget(NewsRow(t, l, i, self._pw))
    def paintEvent(self, a0):
        if self._line:
            p = QPainter(self); p.setPen(QPen(QColor(0, 0, 0, 30), 1))
            p.drawLine(0, self.height() - 1, self.width(), self.height() - 1)

class NewsWidget(RoundedWindow):
    def __init__(self, x, y):
        super().__init__(cfg.LIGHT_BLOCK_BG, cfg.LIGHT_BLOCK_BRD)
        self.setFixedWidth(cfg.WIN_WIDTH + 2 * self.pad); self.move(x, y)
        lo = QVBoxLayout(self); lo.setContentsMargins(self.pad + 12, self.pad + 8, self.pad + 12, self.pad + 18)
        self.s1 = NewsSection("15min naujienos", self); self.s2 = NewsSection("LRT naujienos", self)
        self.s3 = NewsSection("Delfi naujienos", self); self.s4 = NewsSection("Verslo žinios", self, False)
        for s in [self.s1, self.s2, self.s3, self.s4]: lo.addWidget(s)
        self._start_fetch()
    def _start_fetch(self):
        self._spawn(lambda: (news.get_15min_news(), news.get_lrt_news(), news.get_delfi_news(), news.get_vz_news()), self._on_data)
    def _on_data(self, res):
        if not res: return
        for s, r in zip([self.s1, self.s2, self.s3, self.s4], res): s.set_items(r)
        QTimer.singleShot(100, self.adjustSize)

class GadgetApp:
    def __init__(self):
        log_ui("GadgetApp startuojama"); self._widgets = []
        screen = QApplication.primaryScreen().geometry()
        self.x = screen.width() - cfg.WIN_WIDTH - cfg.X_OFFSET - cfg.SHADOW_SIZE
        self.weather = WeatherWidget(self.x, cfg.Y_OFFSET)
        self.weather.ready.connect(lambda: self._init_rest())
        self.weather.show(); self._widgets.append(self.weather)

    def _init_rest(self):
        if len(self._widgets) > 1: return
        y = self.weather.y() + self.weather.height() + cfg.GAP
        for cls in [NordPoolWidget, NewsWidget]:
            w = cls(self.x, y); w.show(); self._widgets.append(w)
            y += w.height() + cfg.GAP

if __name__ == "__main__":
    app = QApplication(sys.argv); app.setQuitOnLastWindowClosed(False)
    gadget = GadgetApp(); sys.exit(app.exec_())