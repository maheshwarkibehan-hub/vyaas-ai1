import sys, math, random, time
from datetime import datetime
try:
    # सिस्टम के आँकड़े प्राप्त करने के लिए psutil लाइब्रेरी
    import psutil
except Exception:
    psutil = None

from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QLinearGradient, QRadialGradient, QFontDatabase
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy, QGridLayout

# एक मान को न्यूनतम और अधिकतम सीमा के बीच रखने के लिए हेल्पर फ़ंक्शन
def clamp(v, lo, hi):
    return max(lo, min(hi, v))

# स्मूथ ट्रांज़िशन के लिए हेल्पर फ़ंक्शन
def smoothstep(edge0, edge1, x):
    t = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3 - 2 * t)

# खंडों के लिए एक कस्टम शीर्षक लेबल
class SectionTitle(QLabel):
    def __init__(self, text):
        super().__init__(text.upper())
        # नया स्टाइल: चमकदार सियान रंग, बोल्ड फ़ॉन्ट, और अक्षरों के बीच दूरी
        self.setStyleSheet("color:#00FFFF; font-weight:700; font-size:14px; letter-spacing:2.5px;")

# एक नियॉन-स्टाइल प्रगति बार विजेट (अब सियान/ब्लू थीम में)
class NeonBar(QWidget):
    def __init__(self, title, init=0.0, style='cyan'):
        super().__init__()
        self.title = title
        self.value = float(init)
        self.unit = ""
        self.setMinimumHeight(56)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.style = style

    def setValue(self, v):
        # मान सेट करें और विजेट को फिर से बनाने के लिए अपडेट करें
        self.value = clamp(float(v), 0.0, 100.0)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = self.rect().adjusted(8, 8, -8, -8)

        # पृष्ठभूमि
        p.setPen(Qt.NoPen)
        # नया कार्ड बैकग्राउंड: हल्का पारदर्शी नीला
        p.setBrush(QColor(10, 25, 45, 200)) 
        p.drawRoundedRect(self.rect(), 8, 8) # गोल कोनों को थोड़ा बढ़ाया

        # शीर्षक टेक्स्ट
        p.setPen(QColor(224, 255, 255)) # Light Cyan text
        p.setFont(QFont("Segoe UI", 10, QFont.Bold))
        p.drawText(r.x(), r.y() - 2, r.width(), 16, Qt.AlignLeft | Qt.AlignTop, self.title.upper())

        # बार की पृष्ठभूमि
        bar = QRectF(r.x(), r.y() + 20, r.width(), 14) # बार को थोड़ा चौड़ा किया
        p.setBrush(QColor(20, 35, 60, 220)) # गहरा बार बैकग्राउंड
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(bar, 7, 7)

        # भरा हुआ बार (मान के आधार पर)
        w = bar.width() * (self.value / 100.0)
        fill = QRectF(bar.x(), bar.y(), w, bar.height())
        
        # शैली के आधार पर ग्रेडिएंट रंग (सियान/ब्लू)
        grad = QLinearGradient(fill.topLeft(), fill.topRight())
        if self.style == 'cyan' or self.style == 'amber' or self.style == 'gold':
            grad.setColorAt(0.0, QColor(0, 255, 255)) # Bright Cyan start
            grad.setColorAt(1.0, QColor(0, 180, 255)) # Bright Blue end
        elif self.style == 'magenta' or self.style == 'red':
            grad.setColorAt(0.0, QColor(255, 69, 0)) # Red (Warning for critical stats)
            grad.setColorAt(1.0, QColor(200, 0, 0))

        p.setBrush(grad)
        p.drawRoundedRect(fill, 7, 7)

        # हाइलाइट लाइन
        p.setPen(QPen(QColor(255, 255, 255, 150), 1.0)) # Brighter highlight
        p.drawLine(bar.topLeft() + QPointF(0, 1), bar.topRight() + QPointF(0, 1))

        # प्रतिशत टेक्स्ट
        p.setPen(QColor(255, 255, 255))
        p.setFont(QFont("Consolas", 11, QFont.DemiBold)) # Slightly larger font
        txt = f"{int(self.value)}{self.unit if self.unit else '%'}"
        p.drawText(r, Qt.AlignRight | Qt.AlignVCenter, txt)

# आँकड़ों के लिए एक कंटेनर कार्ड (सियान बॉर्डर के साथ)
class StatCard(QFrame):
    def __init__(self, title, bars):
        super().__init__()
        # स्टाइल: गहरा नीला पृष्ठभूमि, गोल कोने और हल्का सियान बॉर्डर (होलोग्राफिक लुक)
        self.setStyleSheet("""
            QFrame { 
                background: rgba(10, 25, 45, 200); /* Lighter transparent blue */
                border-radius:8px; 
                border:1px solid rgba(0, 255, 255, 100); /* Bright Cyan border */
            }
        """)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(8)
        lay.addWidget(SectionTitle(title))
        for b in bars:
            lay.addWidget(b)
        lay.addStretch()

# नेटवर्क आँकड़ों के लिए कार्ड (नए सियान स्टाइल में)
class NetworkStats(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QFrame { 
                background: rgba(10, 25, 45, 200); 
                border-radius:8px; 
                border:1px solid rgba(0, 255, 255, 100); 
            }
            QLabel { color:#E0FFFF; font-size:13px; font-weight:500; }
        """)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(8)
        lay.addWidget(SectionTitle("NETWORK STATISTICS"))
        
        # डेटा लेबल का एक कस्टम स्टाइल
        data_style = "color:#00FFFF; font-size:16px; font-weight:bold; letter-spacing:1px;" # Brighter Cyan, larger font
        
        ip_lbl = QLabel("IP Address:")
        self.ip = QLabel("0.0.0.0")
        self.ip.setStyleSheet(data_style)
        
        up_lbl = QLabel("Upload (MB/s):")
        self.up = QLabel("0.0")
        self.up.setStyleSheet(data_style)
        
        down_lbl = QLabel("Download (MB/s):")
        self.down = QLabel("0.0")
        self.down.setStyleSheet(data_style)

        # एक ग्रिड लेआउट में नेटवर्क विवरण डालें
        net_grid = QGridLayout()
        net_grid.addWidget(ip_lbl, 0, 0)
        net_grid.addWidget(self.ip, 0, 1, Qt.AlignRight)
        net_grid.addWidget(up_lbl, 1, 0)
        net_grid.addWidget(self.up, 1, 1, Qt.AlignRight)
        net_grid.addWidget(down_lbl, 2, 0)
        net_grid.addWidget(self.down, 2, 1, Qt.AlignRight)
        
        lay.addLayout(net_grid)
        lay.addStretch()

# घड़ी के लिए कार्ड (नए सियान स्टाइल में)
class ClockCard(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QFrame { 
                background: rgba(10, 25, 45, 200); 
                border-radius:8px; 
                border:1px solid rgba(0, 255, 255, 100); 
            }
            QLabel { color:#E0FFFF; }
        """)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 12, 12, 12)
        
        self.timeLbl = QLabel("--:--:--")
        self.timeLbl.setStyleSheet("font-size:48px; font-weight:900; color:#00FFFF;") # Larger, brighter time
        
        self.logLbl = QLabel("SYSTEM BOOTING...")
        self.logLbl.setStyleSheet("color:#FF4500; font-size:14px; font-weight:bold; letter-spacing:1px;") # Keep log red/warning
        
        lay.addWidget(SectionTitle("SYSTEM STATUS"))
        lay.addWidget(self.timeLbl, alignment=Qt.AlignCenter)
        lay.addWidget(self.logLbl, alignment=Qt.AlignRight)

    def tick(self):
        now = datetime.now()
        self.timeLbl.setText(now.strftime("%H:%M:%S"))

# एनिमेटेड घूमने वाली रिंग्स (अधिक जटिल, हाई-फाई लुक)
class AnimatedRings(QWidget):
    def __init__(self):
        super().__init__()
        self.phase = 0.0
        self.setMinimumSize(520, 520)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        rect = self.rect()
        cx, cy = rect.center().x(), rect.center().y()
        radius = min(rect.width(), rect.height()) * 0.42

        # पृष्ठभूमि ग्रेडिएंट
        bg = QRadialGradient(QPointF(cx, cy), radius * 1.8)
        bg.setColorAt(0.0, QColor(10, 20, 35, 150))
        bg.setColorAt(1.0, QColor(6, 8, 12, 0))
        p.fillRect(rect, bg)
        
        # रिंग्स की परिभाषा (त्रिज्या, चौड़ाई, ऑफ़सेट, रंग) - सियान/सफ़ेद
        rings = [
            (radius * 1.05, 12.0, 0.00, QColor(0, 255, 255, 240)),  # Bright Cyan
            (radius * 0.90, 8.0, 0.19, QColor(0, 180, 255, 220)),    # Bright Blue
            (radius * 0.75, 5.0, 0.36, QColor(240, 255, 255, 200)), # White
            (radius * 0.60, 3.0, 0.54, QColor(0, 255, 255, 180)),
        ]
        for r, w, off, col in rings:
            self._draw_segmented_ring(p, QPointF(cx, cy), r, w, off, col)
            
        # केंद्र विज़ुअलाइज़ेशन: एक केंद्रीय गोलाकार कोर जो पल्स करता है
        center = QPointF(cx, cy)
        pulse_alpha = 150 + 100 * math.sin(self.phase * 2 * math.pi * 3)
        p.setBrush(QColor(0, 255, 255, int(pulse_alpha)))
        p.setPen(QPen(QColor(0, 255, 255), 2))
        p.drawEllipse(center, radius * 0.2, radius * 0.2)
        
        # मुख्य शीर्षक
        p.setPen(QColor(255, 255, 255))
        p.setFont(QFont("Consolas", 52, QFont.Black))
        p.drawText(rect, Qt.AlignCenter, "AGENT_01")

        # स्थिति
        p.setFont(QFont("Consolas", 14, QFont.DemiBold))
        p.setPen(QColor(0, 255, 255)) # Cyan status
        online_rect = rect.adjusted(0, 140, 0, 0)
        p.drawText(online_rect, Qt.AlignHCenter | Qt.AlignVCenter, "STATUS: ONLINE [LIVE FEED]")

    def _draw_segmented_ring(self, p, center, radius, width, offset, color):
        # एक खंडित, कोणीय रिंग बनाने के लिए
        base = (self.phase * 0.5 + offset) % 1.0 # धीमी रोटेशन
        segments = 24 # खंडों की संख्या बढ़ाई
        gap_deg = 8.0 # अंतर को थोड़ा कम किया

        for i in range(segments):
            # प्रत्येक सेगमेंट के लिए शुरू और अवधि (Start and Span) की गणना करें
            angle_per_segment = 360.0 / segments
            start_angle = (i * angle_per_segment + base * 360.0)
            span_angle = angle_per_segment - gap_deg
            
            # चमक के लिए: फ़ेज़ पर आधारित चमक (Pulsing effect)
            t_pulse = (i / segments + self.phase * 1.5) % 1.0
            alpha = 100 + 155 * smoothstep(0.0, 0.5, math.sin(t_pulse * 2 * math.pi))
            
            pen = QPen(QColor(color.red(), color.green(), color.blue(), int(alpha)), width)
            pen.setCapStyle(Qt.FlatCap)
            p.setPen(pen)
            
            rect = QRectF(center.x() - radius, center.y() - radius, radius * 2, radius * 2)
            # drawArc में कोण को 16 से गुणा करें
            p.drawArc(rect, int(-start_angle * 16), int(-span_angle * 16))
        
        # केंद्र में एक छोटा डॉट
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(255, 255, 255, 150))
        p.drawEllipse(center, 4, 4)

# विंडो के लिए शीर्षक बार (नए स्टाइल में)
class TitleBar(QFrame):
    def __init__(self, title):
        super().__init__()
        self.setStyleSheet("""
            QFrame{ 
                background: rgba(12, 16, 22, 200); 
                border-bottom:2px solid rgba(0, 255, 255, 100); /* सियान बॉटम बॉर्डर */
            } 
            QLabel{ 
                color:#00FFFF; /* सियान शीर्षक */
                font-weight:700; 
                letter-spacing:2px; /* अधिक स्पेसिंग */
            }
        """)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(15, 8, 15, 8) # थोड़ा अधिक पैडिंग
        lbl = QLabel(title)
        lbl.setFont(QFont("Consolas", 14, QFont.Bold))
        lay.addWidget(lbl)
        lay.addStretch()

# मुख्य विंडो
class NovaHUD(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AGENT_01 Vision HUD (Redesigned)")
        self.resize(1200, 800) # विंडो का आकार थोड़ा बढ़ाया
        # गहरा नीला पृष्ठभूमि रंग
        self.setStyleSheet("background-color: #0A1423;")

        top = TitleBar("ADVANCED SYSTEM DIAGNOSTICS INTERFACE")
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(10)
        root.addWidget(top)

        body = QGridLayout()
        body.setSpacing(15) # स्पेसिंग बढ़ाई
        root.addLayout(body, 1)

        # बायां कॉलम (नेटवर्क + घड़ी)
        leftColumn = QVBoxLayout()
        leftColumn.setSpacing(15)
        self.clock = ClockCard()
        self.net = NetworkStats()
        
        # बायां कॉलम को एक रैपर में डाला ताकि ग्रिड में स्ट्रेच हो सके
        leftWrap = QWidget()
        leftWrap.setLayout(leftColumn)
        leftColumn.addWidget(self.clock, 1) # घड़ी को ऊपर ज़्यादा जगह
        leftColumn.addWidget(self.net, 1)

        body.addWidget(leftWrap, 0, 0, 2, 1) # बायां कॉलम 2 पंक्तियों तक फैला हुआ

        # केंद्र: एनिमेटेड रिंग्स
        self.rings = AnimatedRings()
        body.addWidget(self.rings, 0, 1, 2, 1) # केंद्र कॉलम 2 पंक्तियों तक फैला हुआ

        # दायां ऊपरी कार्ड (सिस्टम प्रोफाइल: CPU, TEMP, BATT)
        self.cpu_util = NeonBar("CPU CORE UTILIZATION", init=65, style='cyan') # Cyan
        self.cpu_temp = NeonBar("CPU TEMPERATURE", init=62, style='red') # Critical Red
        self.battery = NeonBar("POWER SUPPLY LEVEL", init=72, style='cyan') # Cyan
        rightUpperCard = StatCard("CRITICAL SYSTEM PROFILES", [self.cpu_util, self.cpu_temp, self.battery])
        body.addWidget(rightUpperCard, 0, 2, 1, 1)

        # दायां निचला कार्ड (स्टोरेज आँकड़े: MEM, DISK)
        self.mem = NeonBar("VOLATILE MEMORY USAGE", init=50, style='red') # Critical Red
        self.disk = NeonBar("PERSISTENT DISK USAGE", init=75, style='cyan') # Cyan
        rightLowerCard = StatCard("STORAGE/MEMORY STATS", [self.mem, self.disk])
        body.addWidget(rightLowerCard, 1, 2, 1, 1)

        # ग्रिड लेआउट को फैलाएं (असममित विभाजन)
        body.setColumnStretch(0, 1)
        body.setColumnStretch(1, 3) # केंद्र विज़ुअलाइज़ेशन को ज़्यादा जगह दी
        body.setColumnStretch(2, 1)
        body.setRowStretch(0, 1)
        body.setRowStretch(1, 1)

        # टाइमर
        self.animTimer = QTimer(self)
        self.animTimer.timeout.connect(self.animate)
        self.animTimer.start(16) # ~60 FPS

        self.statTimer = QTimer(self)
        self.statTimer.timeout.connect(self.sampleStats)
        self.statTimer.start(1000) # हर सेकंड

        self.clockTimer = QTimer(self)
        self.clockTimer.timeout.connect(self.tick)
        self.clockTimer.start(1000) # हर सेकंड

        self.last_bytes = None
        self.sampleStats()
        self.tick()

    def update_log(self, message):
        # लॉग संदेश को अपडेट करें
        if self and hasattr(self, 'clock') and self.clock:
            self.clock.logLbl.setText(str(message).upper())

    def animate(self):
        # रिंग्स एनीमेशन को अपडेट करें
        self.rings.phase = (self.rings.phase + 0.0075) % 1.0
        self.rings.update()

    def tick(self):
        # घड़ी को अपडेट करें
        self.clock.tick()

    def sampleStats(self):
        # सिस्टम आँकड़े प्राप्त करें और UI को अपडेट करें
        
        # CPU उपयोगिता
        try:
            cpu = psutil.cpu_percent(interval=None) if psutil else random.uniform(8, 88)
        except:
            cpu = random.uniform(8, 88)
        self.cpu_util.setValue(cpu)

        # CPU तापमान
        temp_c = None
        if psutil:
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    for k, v in temps.items():
                        if v:
                            temp_c = v[0].current
                            break
            except:
                temp_c = None
        if temp_c is None:
            temp_c = 48 + 12 * math.sin(time.time() / 6.5) + random.uniform(-2, 2)
        # तापमान मान के साथ बार को अपडेट करें
        self.cpu_temp.setValue(clamp((temp_c / 100.0) * 100, 0, 100))

        # बैटरी स्तर
        batt_pct = None
        if psutil and hasattr(psutil, "sensors_battery"):
            try:
                b = psutil.sensors_battery()
                if b: batt_pct = b.percent
            except:
                batt_pct = None
        if batt_pct is None:
            batt_pct = 70 + 8 * math.sin(time.time() / 10.0) + random.uniform(-4, 4)
        self.battery.setValue(clamp(batt_pct, 0, 100))

        # मेमोरी उपयोग
        try:
            mem_pct = psutil.virtual_memory().percent if psutil else random.uniform(22, 86)
        except:
            mem_pct = random.uniform(22, 86)
        self.mem.setValue(mem_pct)

        # डिस्क उपयोग
        try:
            disk_pct = psutil.disk_usage('/').percent if psutil else random.uniform(12, 88)
        except:
            disk_pct = random.uniform(12, 88)
        self.disk.setValue(disk_pct)

        # नेटवर्क आँकड़े
        if psutil:
            try:
                addrs = psutil.net_if_addrs()
                ip = "0.0.0.0"
                for _, arr in addrs.items():
                    for a in arr:
                        # केवल IPv4 एड्रेस को फ़िल्टर करें जो 169.254 से शुरू नहीं होते हैं
                        if getattr(a, 'family', None) and str(getattr(a, 'address', '')).count('.') == 3 and not a.address.startswith("169.254"):
                            ip = a.address
                            break
                    if ip != "0.0.0.0":
                        break
                self.net.ip.setText(f"{ip}")
            except:
                self.net.ip.setText("0.0.0.0")

            try:
                io = psutil.net_io_counters()
                nowb = (io.bytes_sent, io.bytes_recv)
                if self.last_bytes:
                    # पिछले मान से अंतर निकालकर दर (rate) की गणना करें
                    up = (nowb[0] - self.last_bytes[0]) / 1024.0 / 1024.0
                    down = (nowb[1] - self.last_bytes[1]) / 1024.0 / 1024.0
                    self.net.up.setText(f"{up:.1f}")
                    self.net.down.setText(f"{down:.1f}")
                self.last_bytes = nowb
            except:
                pass
        else:
            # psutil के बिना रैंडम मान
            self.net.ip.setText("192.168.1.101")
            self.net.up.setText(f"{random.uniform(0.4, 3.2):.1f}")
            self.net.down.setText(f"{random.uniform(3.3, 18.3):.1f}")

def main():
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    # फॉन्ट लोड करने का प्रयास
    # font_id = QFontDatabase.addApplicationFont("path/to/your/font.ttf")
    # if font_id != -1:
    #     font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
    #     app.setFont(QFont(font_family))
        
    win = NovaHUD()
    win.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
