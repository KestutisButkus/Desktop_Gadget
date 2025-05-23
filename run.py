import tkinter as tk
from datetime import datetime

from PIL import Image, ImageTk
import news
import meteo_lt
import nordpool
import time
from news import lines_news as lines
print("naujienų eilutės: ", lines, ", tipas: ", type(lines))

# Funkcija laiko formatavimui
def format_time(seconds):
    mins, secs = divmod(seconds, 60)
    return f"{mins:02d}:{secs:02d}"

# Sukuriame pagrindinį langą
root = tk.Tk()
root.title("Informacijos langas")
root.geometry("420x700")
root.attributes('-alpha', 0.0)
root.overrideredirect(True)
root.configure(bg="black")

wrap_length = 400

# Pozicija
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_position = screen_width - 420 - 20
y_position = 40
root.geometry(f"+{x_position}+{y_position}")

# === ORO LANGAS ===
weather_window = tk.Toplevel(root)
weather_window.geometry(f"420x140+{x_position + 10}+{y_position + 20}")
weather_window.attributes('-alpha', 0.7)
weather_window.overrideredirect(True)
weather_window.configure(bg="white")

weather_frame = tk.Frame(weather_window, bg="white")
weather_frame.grid(row=0, column=0, pady=5, padx=10)

weather_timer_label = tk.Label(weather_window, text="", font=("Helvetica", 7), bg="white", fg="gray")
weather_timer_label.grid(row=1, column=0, sticky="e", padx=10)


# === NORDPOOL LANGAS ===
nordpool_window = tk.Toplevel(root)
nordpool_window.geometry(f"420x75+{x_position + 10}+{y_position + 170}")
nordpool_window.attributes('-alpha', 0.6)
nordpool_window.overrideredirect(True)
nordpool_window.configure(bg="black")
nordpool_window.columnconfigure(0, weight=1)
nordpool_window.rowconfigure(0, weight=1)
nordpool_window.rowconfigure(1, weight=1)

nordpool_label = tk.Label(nordpool_window, font=("Helvetica", 8, "bold"), bg="black", fg="white", justify=tk.LEFT)
nordpool_label.grid(row=0, column=0, rowspan=2, pady=10, padx=10, sticky="nsew")

nordpool_label_name = tk.Label(nordpool_window, text="NordPool", font=("Helvetica", 16, "bold"), fg="steel blue", bg="black")
nordpool_label_name.grid(row=0, column=1, padx=30, pady=10)

# nordpool_timer_label = tk.Label(nordpool_window, text="", font=("Helvetica", 7), bg="black", fg="gray")
# nordpool_timer_label.grid(row=1, column=1, columnspan=2, padx=10, sticky="e")


# === NAUJIENŲ LANGAS ===
news_window = tk.Toplevel(root)
news_window.geometry(f"420x{180+(lines * 100)}+{x_position + 10}+{y_position + 255}")
news_window.attributes('-alpha', 0.7)
news_window.overrideredirect(True)
news_window.configure(bg="white")

news_timer_label = tk.Label(news_window, text="", font=("Helvetica", 7), bg="white", fg="gray")
news_timer_label.grid(row=99, column=0, sticky="e", padx=10)

def update_weather():
    print("Atnaujinama orų informacija")
    weather_city, weather_info_top, weather_info_left, weather_info_right, weather_icon_path = meteo_lt.get_weather_data()

    for widget in weather_frame.winfo_children():
        widget.destroy()

    tk.Label(weather_frame, text=weather_city, font=("Helvetica", 12, "bold"),
             fg="dodger blue", bg="white").grid(row=0, column=0, columnspan=2, padx=30, sticky=tk.W)

    tk.Label(weather_frame, text=weather_info_top, font=("Helvetica", 18, "bold"),
             fg="teal", bg="white").grid(row=2, column=1, columnspan=2, sticky=tk.E)

    tk.Label(weather_frame, text=weather_info_left, justify=tk.LEFT, font=("Helvetica", 8),
             fg="black", bg="white").grid(row=1, column=0, rowspan=2)

    tk.Label(weather_frame, text=weather_info_right, justify=tk.RIGHT, font=("Helvetica", 8),
             fg="black", bg="white").grid(row=0, column=2, rowspan=2)

    if weather_icon_path:
        icon_data = Image.open(weather_icon_path)
        icon_image = ImageTk.PhotoImage(icon_data)
        icon_label = tk.Label(weather_frame, image=icon_image, bg="white")
        icon_label.image = icon_image
        icon_label.grid(row=0, column=1, rowspan=2, pady=10, padx=30)



def update_nordpool():
    info = nordpool.get_nordpool_info()
    nordpool_label.config(text=info)

def update_news():
    news_15min.config(text=news.get_15min_news())
    news_lrt.config(text=news.get_lrt_news())
    news_delfi.config(text=news.get_delfi_news())
    news_vz_data = news.get_vz_news()

    for widget in news_links_frame.winfo_children():
        widget.destroy()

    for i, (title, link_url) in enumerate(news_vz_data):
        link = tk.Label(news_links_frame, text=f"• {title}", font=("Helvetica", 8),
                        fg="black", bg="white", justify=tk.LEFT, cursor="hand2", wraplength=wrap_length)
        link.grid(row=i, column=0, sticky=tk.W, padx=10)
        link.bind("<Button-1>", lambda e, url=link_url: callback(url))

# === LAIKMAČIAI ===

update_interval = 900  # sekundės

def countdown(label, updater_func, interval):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    def tick():
        nonlocal interval, now
        if interval <= 0:
            updater_func()
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            interval = update_interval
        label.config(text=f"Atnaujinimas po: {format_time(interval)}  (atnaujinta: {now})")
        interval -= 1
        label.after(1000, tick)
    tick()

# === NAUJIENŲ TURINYS ===

tk.Label(news_window, text="\n15min naujienos:", font=("Helvetica", 9, "bold"),
         fg="black", bg="white", justify=tk.LEFT).grid(row=0, column=0, columnspan=2, padx=10, sticky=tk.W)
news_15min = tk.Label(news_window, font=("Helvetica", 8), fg="black", bg="white", wraplength=wrap_length, justify=tk.LEFT)
news_15min.grid(row=1, column=0, columnspan=2, padx=10, sticky=tk.W)

tk.Label(news_window, text="LRT naujienos:", font=("Helvetica", 9, "bold"),
         fg="black", bg="white").grid(row=2, column=0, columnspan=2, padx=10, sticky=tk.W)

news_lrt = tk.Label(news_window, font=("Helvetica", 8), fg="black", bg="white", wraplength=wrap_length, justify=tk.LEFT)
news_lrt.grid(row=3, column=0, columnspan=2, padx=10, sticky=tk.W)

tk.Label(news_window, text="Delfi naujienos:", font=("Helvetica", 9, "bold"),
         fg="black", bg="white").grid(row=4, column=0, columnspan=2, padx=10, sticky=tk.W)

news_delfi = tk.Label(news_window, font=("Helvetica", 8), fg="black", bg="white", wraplength=wrap_length, justify=tk.LEFT)
news_delfi.grid(row=5, column=0, columnspan=2, padx=10, sticky=tk.W)

tk.Label(news_window, text="Verslo žinios:", font=("Helvetica", 9, "bold"),
         fg="black", bg="white").grid(row=6, column=0, columnspan=2, padx=10, sticky=tk.W)

news_links_frame = tk.Frame(news_window, bg="white")
news_links_frame.grid(row=7, column=0, columnspan=2, sticky="w")

def callback(url):
    import webbrowser
    webbrowser.open(url)

# === Pradinis užkrovimas ir laikmačiai ===
update_weather()
update_nordpool()
update_news()

countdown(weather_timer_label, update_weather, update_interval)
# countdown(nordpool_timer_label, update_nordpool, update_interval)
countdown(news_timer_label, update_news, update_interval)

# === Paleidžiamas ciklas ===
root.mainloop()
