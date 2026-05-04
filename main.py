import json
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle

# উইন্ডো সেটিংস
Window.softinput_mode = "below_target"
Window.clearcolor = (0.01, 0.02, 0.05, 1)

DATA_FILE = "bet_ai_config.json"

class StyledCard(BoxLayout):
    def __init__(self, bg_color=(0.07, 0.09, 0.15, 1), **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(15)
        self.spacing = dp(10)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))
        
        with self.canvas.before:
            self.color_obj = Color(*bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(15)])
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class OddsControl(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="horizontal", size_hint_y=None, height=dp(50), spacing=dp(5), **kwargs)
        self.value = 1.67
        odds_list = [f"{x/100:.2f}" for x in range(150, 501)]

        self.spinner = Spinner(
            text=str(self.value), values=odds_list, size_hint_x=0.3,
            background_normal='', background_color=(0.1, 0.2, 0.4, 1), color=(1, 1, 1, 1), font_size='14sp'
        )
        self.input = TextInput(
            text=str(self.value), multiline=False, input_filter='float',
            size_hint_x=0.4, background_normal='', background_color=(0.02, 0.03, 0.06, 1),
            foreground_color=(1, 1, 1, 1), font_size='18sp', padding=[dp(8), dp(10)]
        )
        self.minus = Button(text="-", size_hint_x=0.15, bold=True, background_normal='', background_color=(0.7, 0.2, 0.2, 1))
        self.plus = Button(text="+", size_hint_x=0.15, bold=True, background_normal='', background_color=(0.2, 0.6, 0.4, 1))

        self.minus.bind(on_press=self.dec); self.plus.bind(on_press=self.inc)
        self.spinner.bind(text=self.select_odds); self.input.bind(text=self.manual)
        self.add_widget(self.spinner); self.add_widget(self.input)
        self.add_widget(self.minus); self.add_widget(self.plus)

    def select_odds(self, instance, value): self.value = float(value); self.input.text = value
    def manual(self, instance, value):
        try: self.value = float(value)
        except: pass
    def inc(self, instance): self.value = round(self.value + 0.01, 2); self.sync()
    def dec(self, instance):
        if self.value > 1.01: self.value = round(self.value - 0.01, 2); self.sync()
    def sync(self): self.input.text = str(self.value); self.spinner.text = str(self.value)

class BetAIPro(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=dp(15), spacing=dp(15), size_hint_y=None, **kwargs)
        self.bind(minimum_height=self.setter('height'))

        # টাইটেল
        header = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50))
        header.add_widget(Label(text="SR BET AI PRO v2.2", font_size='22sp', bold=True, color=(0.2, 0.7, 1, 1), halign="left"))
        self.save_status = Label(text="● ONLINE", font_size='10sp', color=(0.2, 0.8, 0.4, 1), size_hint_x=0.3)
        header.add_widget(self.save_status)
        self.add_widget(header)
        
        # কার্ড ১: টিম ও অডস
        card1 = StyledCard()
        card1.add_widget(Label(text="LIVE ODDS INPUT", bold=True, color=(0.4, 0.6, 1, 1), size_hint_y=None, height=dp(20), font_size='12sp'))
        self.t1 = self.styled_input("Team 1 Name")
        self.o1 = OddsControl()
        self.t2 = self.styled_input("Team 2 Name")
        self.o2 = OddsControl()
        card1.add_widget(self.t1); card1.add_widget(self.o1)
        card1.add_widget(self.t2); card1.add_widget(self.o2)
        self.add_widget(card1)

        # কার্ড ২: ইনভেস্টমেন্ট
        card2 = StyledCard()
        self.amount = self.styled_input("Total Investment Amount", 'float')
        self.extra = self.styled_input("Extra Margin (Recovery)", 'float')
        card2.add_widget(self.amount); card2.add_widget(self.extra)
        self.add_widget(card2)

        # কার্ড ৩: রেজাল্ট
        self.res_card = StyledCard(bg_color=(0.1, 0.12, 0.2, 1))
        self.signal = Label(text="SCANNING...", font_size='24sp', bold=True, size_hint_y=None, height=dp(45))
        self.summary = Label(text="Enter values to start AI analysis", font_size='16sp', size_hint_y=None, height=dp(30), color=(0.6, 0.7, 0.8, 1))
        self.p_bar = Label(text="[ -------------------- ]", font_size='14sp', color=(0.3, 0.4, 0.6, 1), size_hint_y=None, height=dp(20))
        self.details = Label(text="", halign="center", font_size='15sp', size_hint_y=None, height=dp(170), color=(0.9, 0.9, 0.9, 1))
        self.res_card.add_widget(self.signal); self.res_card.add_widget(self.summary); self.res_card.add_widget(self.p_bar); self.res_card.add_widget(self.details)
        self.add_widget(self.res_card)

        # লোড ডাটা এবং বাইন্ডিং
        self.load_data()
        for field in [self.amount, self.extra, self.t1, self.t2, self.o1.input, self.o2.input]:
            field.bind(text=self.calculate)

    def styled_input(self, hint, filt=None):
        return TextInput(hint_text=hint, input_filter=filt, multiline=False, size_hint_y=None, height=dp(48),
                         background_normal='', background_color=(0.02, 0.04, 0.08, 1),
                         foreground_color=(1, 1, 1, 1), padding=[dp(12), dp(12)], font_size='16sp')

    def save_data(self, *args):
        data = {"t1": self.t1.text, "t2": self.t2.text, "amount": self.amount.text, "extra": self.extra.text, "o1": self.o1.value, "o2": self.o2.value}
        with open(DATA_FILE, "w") as f: json.dump(data, f)

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    data = json.load(f)
                    self.t1.text = data.get("t1", ""); self.t2.text = data.get("t2", "")
                    self.amount.text = data.get("amount", ""); self.extra.text = data.get("extra", "")
                    self.o1.value = data.get("o1", 1.67); self.o1.sync()
                    self.o2.value = data.get("o2", 1.67); self.o2.sync()
            except: pass

    def calculate(self, *args):
        self.save_data()
        try:
            # টিমের নাম ধরা
            name1 = self.t1.text.strip() if self.t1.text.strip() else "Team 1"
            name2 = self.t2.text.strip() if self.t2.text.strip() else "Team 2"
            
            o1, o2 = float(self.o1.value), float(self.o2.value)
            T_base = float(self.amount.text)
            extra = float(self.extra.text) if self.extra.text else 0

            # ক্যালকুলেশন
            b1 = (T_base * o2) / (o1 + o2)
            b2 = (T_base * o1) / (o1 + o2) + extra
            T_total = T_base + extra
            
            r1 = b1 * o1
            r2 = b2 * o2
            min_r = min(r1, r2)
            net = min_r - T_total
            arb = (1/o1) + (1/o2)

            # সিগন্যাল লজিক
            if arb < 1: 
                sig, col, bar = "PROFIT CONFIRMED", (0.2, 0.9, 0.4, 1), "[ ##########---------- ]"
            elif abs(arb - 1) < 0.01: 
                sig, col, bar = "BREAK EVEN", (1, 0.8, 0.2, 1), "[ #####--------------- ]"
            else: 
                sig, col, bar = "RISK DETECTED", (1, 0.3, 0.3, 1), "[ #------------------- ]"

            self.signal.text = sig; self.signal.color = col
            self.p_bar.text = bar; self.p_bar.color = col
            self.summary.text = f"{name1}: {round(b1)} TK | {name2}: {round(b2)} TK"
            
            # ডায়নামিক রিপোর্ট (টিমের নামসহ)
            self.details.text = (f"--- AI FINANCIAL REPORT ---\n\n"
                                 f"{name1} Return: {round(r1)} TK\n"
                                 f"{name2} Return: {round(r2)} TK\n"
                                 f"TOTAL RETURN: {round(min_r)} TK\n"
                                 f"NET PROFIT: {round(net)} TK\n"
                                 f"TOTAL STAKE: {round(T_total)} TK\n"
                                 f"RETURN RATE: {round((min_r/T_total)*100, 2)}%\n"
                                 f"MARKET EFFICIENCY: {round(arb, 3)}")
        except:
            self.signal.text = "AWAITING DATA"; self.p_bar.text = "[ -------------------- ]"

class BetApp(App):
    def build(self):
        root = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        root.add_widget(BetAIPro())
        return root

if __name__ == "__main__":
    BetApp().run()