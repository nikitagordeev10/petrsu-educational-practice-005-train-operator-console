# библиотеки
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pygame
import threading
import time


class ControlPanel:
    def __init__(self, root):
        """Окно Пульт машиниста"""
        self.root = root
        self.root.title("Пульт управления локомотивом")
        self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
        self.root.configure(bg="#85898A")

        # Инициализация pygame для звуков
        pygame.init()
        pygame.mixer.init()
        self.horn_sound = pygame.mixer.Sound("horn.mp3")

        # Статусы
        self.doors_open = False
        self.lights_on = False
        self.speed = 0
        self.current_gear = "Тормоз"
        self.target_speed = 0  # Целевая скорость
        self.is_accelerating = False  # Флаг для отслеживания процесса разгона
        self.mileage = 0  # Пробег в км
        self.fuel = 0.1  # Топливо в литрах (начальное значение)
        self.range_left = self.calculate_range()  # Запас хода в км
        self.fuel_empty = False  # Флаг для проверки, что топливо закончилось

        # Создаем спидометр
        self.create_monitor()
        self.create_control_panel()

        # Запуск потока обновления скорости и пробега
        self.running = True
        self.update_speed_thread = threading.Thread(target=self.update_speed)
        self.update_speed_thread.start()

    def create_monitor(self):
        """Информационный монитор"""
        monitor_frame = tk.Frame(self.root, bg="#85898A")
        monitor_frame.pack(pady=10)

        self.monitor_label = tk.Label(monitor_frame, text="Информационный монитор", font=("Arial", 16), bg="#85898A",
                                      fg="black")
        self.monitor_label.pack()

        # Индикатор двери
        self.door_indicator = tk.Label(monitor_frame, text="Двери: Закрыты", font=("Arial", 14), bg="#85898A",
                                       fg="gray")
        self.door_indicator.pack()

        # Индикатор фар
        self.lights_indicator = tk.Label(monitor_frame, text="Фары: Выключены", font=("Arial", 14), bg="#85898A",
                                         fg="gray")
        self.lights_indicator.pack()

        # Индикатор скорости
        self.speed_indicator = tk.Label(monitor_frame, text=f"Скорость: {self.speed} км/ч", font=("Arial", 14),
                                        bg="#85898A")
        self.speed_indicator.pack()

        # Пробег
        self.mileage_indicator = tk.Label(monitor_frame, text=f"Пробег: {self.mileage} км", font=("Arial", 14),
                                          bg="#85898A")
        self.mileage_indicator.pack()

        # Запас хода
        self.range_indicator = tk.Label(monitor_frame, text=f"Запас хода: {self.range_left} км", font=("Arial", 14),
                                        bg="#85898A")
        self.range_indicator.pack()

        # Количество топлива
        self.fuel_indicator = tk.Label(monitor_frame, text=f"Топливо: {self.fuel} л", font=("Arial", 14),
                                       bg="#85898A")
        self.fuel_indicator.pack()

        # Строка спидометра
        self.speed_display_bar()

    def create_control_panel(self):
        """Панель управления"""
        control_frame = tk.Frame(self.root, bg="#85898A")
        control_frame.pack(pady=20)

        self.control_frame = tk.Label(control_frame, text="Панель управления", font=("Arial", 16), bg="#85898A",
                                      fg="black")
        self.control_frame.pack(padx=10)

        # Выбор хода
        self.gear_label = tk.Label(control_frame, text="Выберите ход:", font=("Arial", 14), bg="#85898A")
        self.gear_label.pack(side=tk.LEFT, padx=10)  # Используем pack вместо grid

        self.gear_var = tk.StringVar(value="Тормоз")
        self.gear_var.trace("w", self.change_gear)
        self.gear_option_menu = tk.OptionMenu(control_frame, self.gear_var, "Тормоз", "Ход 1", "Ход 2", "Ход 3")
        self.gear_option_menu.pack(side=tk.LEFT, padx=10)  # Используем pack вместо grid

        # Кнопка Экстренный тормоз
        self.emergency_brake_button = tk.Button(control_frame, text="Экстренный тормоз", command=self.emergency_brake,
                                                font=("Arial", 12), bg="#DEDEDC", relief="raised", width=20)
        self.emergency_brake_button.pack(pady=10)

        # Кнопка Гудок
        self.horn_button = tk.Button(control_frame, text="Гудок", command=self.horn,
                                     font=("Arial", 12), bg="#DEDEDC", relief="raised", width=20)
        self.horn_button.pack(pady=10)

        # Кнопка Открыть/Закрыть дверь
        self.door_button = tk.Button(control_frame, text="Открыть/Закрыть дверь", command=self.toggle_door,
                                     font=("Arial", 12), bg="#DEDEDC", relief="raised", width=20)
        self.door_button.pack(pady=10)

        # Кнопка Включить/выключить фары
        self.lights_button = tk.Button(control_frame, text="Включить/выключить фары", command=self.toggle_lights,
                                       font=("Arial", 12), bg="#DEDEDC", relief="raised", width=20)
        self.lights_button.pack(pady=10)

    def speed_display_bar(self):
        """Строка спидометра"""
        self.figure = Figure(figsize=(4, 0.5))  # Уменьшенный размер
        self.subplot = self.figure.add_subplot(111)
        self.subplot.set_xlim(0, 100)
        self.subplot.set_ylim(0, 1)
        self.subplot.axis('off')

        # Полоска для отображения скорости
        self.speed_bar = self.subplot.barh(0, self.speed, height=0.5, color='r', edgecolor='black')
        self.subplot.set_title("Спидометр", fontsize=14)

        # Разлиновка скорости
        for i in range(0, 101, 10):
            self.subplot.text(i, 0.05, str(i), ha='center', va='bottom', fontsize=8,
                              color='black')  # Отображение значения скорости
            self.subplot.axvline(x=i, color='black', linewidth=0.5, linestyle='--')  # Вертикальная линия

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.get_tk_widget().pack(pady=10)  # Размещаем спидометр под информационным монитором

        self.update_speed_display_bar()

    def update_speed_display_bar(self):
        self.speed_bar[0].set_width(self.speed)
        self.canvas.draw()

    def set_speed(self, speed):
        self.speed = speed
        self.update_speed_display_bar()
        self.speed_indicator.config(text=f"Скорость: {self.speed} км/ч")

    def change_gear(self, *args):
        if not self.fuel_empty:  # Проверяем, есть ли топливо
            self.current_gear = self.gear_var.get()

            # Определяем целевую скорость на основе текущего хода
            target_speeds = {
                "Тормоз": 0,
                "Ход 1": 30,
                "Ход 2": 60,
                "Ход 3": 90
            }
            new_target_speed = target_speeds[self.current_gear]

            if new_target_speed > self.speed:
                self.start_acceleration(new_target_speed)  # Увеличиваем скорость
            else:
                self.start_slow_down(new_target_speed)  # Понижаем скорость
        else:
            print("Топливо закончилось! Поезд не может двигаться.")

    def start_acceleration(self, target_speed):
        """Запускаем разгон"""
        self.target_speed = target_speed
        self.is_accelerating = True
        self.accelerate()  # Запускаем процесс разгона

    def accelerate(self):
        """Метод для плавного ускорения"""
        if self.is_accelerating and self.speed < self.target_speed:
            self.set_speed(min(self.target_speed, self.speed + 2))  # Плавное увеличение скорости
            self.root.after(100, self.accelerate)  # Повторяем через 100 мс
        else:
            self.is_accelerating = False

    def start_slow_down(self, target_speed):
        """Запускаем процесс торможения"""
        self.target_speed = target_speed
        self.slow_down()  # Запускаем процесс торможения

    def slow_down(self):
        """Метод для плавного снижения скорости"""
        if self.speed > self.target_speed:
            self.set_speed(max(self.target_speed, self.speed - 2))  # Плавное снижение скорости
            self.root.after(100, self.slow_down)  # Повторяем через 100 мс

    def start_emergency_slow_down(self, target_speed):
        """Запускаем процесс экстренного торможения"""
        self.target_speed = target_speed
        self.emergency_slow_down()  # Запускаем процесс торможения

    def emergency_slow_down(self):
        """Метод для экстренного торможения"""
        if self.speed > self.target_speed:
            self.set_speed(max(self.target_speed, self.speed - 4))  # Быстрое снижение скорости
            self.root.after(100, self.emergency_slow_down)  # Повторяем через 100 мс

    def toggle_door(self):
        self.doors_open = not self.doors_open
        if self.doors_open:
            self.door_indicator.config(text="Двери: Открыты", fg="yellow")
        else:
            self.door_indicator.config(text="Двери: Закрыты", fg="gray")

    def toggle_lights(self):
        self.lights_on = not self.lights_on
        if self.lights_on:
            self.lights_indicator.config(text="Фары: Включены", fg="yellow")
        else:
            self.lights_indicator.config(text="Фары: Выключены", fg="gray")

    def emergency_brake(self):
        self.start_emergency_slow_down(0)  # Экстренное торможение до 0 км/ч

    def horn(self):
        self.horn_sound.play()

    def calculate_range(self):
        """Вычисляем запас хода на основе количества топлива."""
        fuel_efficiency = 5  # Поезд тратит 5 литров на 1 км
        return self.fuel * fuel_efficiency

    def update_mileage_and_fuel(self):
        """Обновляем пробег, запас хода и количество топлива."""
        if self.speed > 0 and not self.fuel_empty:
            self.mileage += self.speed / 3600  # Пробег увеличивается с учетом скорости (км/ч)
            self.fuel -= (self.speed / 3600) / 30  # Расход топлива (5 литров на 1 км)
            self.range_left = self.calculate_range()

            # Если топливо закончилось, останавливаем поезд
            if self.fuel <= 0:
                self.fuel = 0
                self.fuel_empty = True
                self.start_emergency_slow_down(0)  # Останавливаем поезд

            # Обновляем значения на мониторе
            self.mileage_indicator.config(text=f"Пробег: {round(self.mileage, 2)} км")
            self.fuel_indicator.config(text=f"Топливо: {round(self.fuel, 2)} л")
            self.range_indicator.config(text=f"Запас хода: {round(self.range_left, 2)} км")

    def update_speed(self):
        while self.running:
            self.update_mileage_and_fuel()  # Обновляем пробег и топливо
            time.sleep(1)  # Обновляем каждую секунду

    def on_closing(self):
        self.running = False
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    control_panel = ControlPanel(root)
    root.protocol("WM_DELETE_WINDOW", control_panel.on_closing)
    root.mainloop()
