# библиотеки
import tkinter as tk
from PIL import Image, ImageTk  # Библиотека для работы с изображениями
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
        self.horn_sound = pygame.mixer.Sound("resources/horn.mp3")
        self.emergency_braking_sound = pygame.mixer.Sound("resources/emergency_braking (1).mp3")
        self.wheels_fast_sound = pygame.mixer.Sound("resources/wheels_fast.mp3")
        self.wheels_slow_sound = pygame.mixer.Sound("resources/wheels_slow.mp3")

        # Статусы
        self.doors_open = False
        self.lights_on = False
        self.heater_on = False
        self.compressor_on=False
        self.wiper_on=False
        self.cabin_lights_on=False
        self.pad_heater_on=False
        self.speed = 0
        self.current_gear = "Тормоз"
        self.target_speed = 0  # Целевая скорость
        self.is_accelerating = False  # Флаг для отслеживания процесса разгона
        self.mileage = 0  # Пробег в км
        self.fuel = 500  # Топливо в литрах (начальное значение)
        self.range_left = self.calculate_range()  # Запас хода в км
        self.fuel_empty = False  # Флаг для проверки, что топливо закончилось
        self.brake_line = 0
        self.brake_cylinder = 0

        # Создаем основную рамку для трех колонок
        main_frame = tk.Frame(self.root, bg="#85898A")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Создаем три колонки
        self.create_left_panel(main_frame)
        self.create_center_panel(main_frame)
        self.create_right_panel(main_frame)

        # Запуск потока обновления скорости и пробега
        self.running = True
        self.update_speed_thread = threading.Thread(target=self.update_speed)
        self.update_speed_thread.start()

    ################################################################################################

    def create_left_panel(self, parent):
        """Создаем левую колонку с заголовком, изображениями и авторами"""
        left_frame = tk.Frame(parent, bg="#85898A", bd=2, relief=tk.RAISED)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Заголовок
        title_label = tk.Label(left_frame, text="Пульт управления Локомотивом", font=("Arial", 18, "bold"),
                               bg="#85898A", fg="black")
        title_label.pack(pady=10)

        # Загрузка изображения РЖД
        rzd_image = Image.open("resources/ржд.png")
        rzd_image = rzd_image.resize((200, 100), Image.Resampling.LANCZOS)  # Изменяем размер изображения
        self.rzd_photo = ImageTk.PhotoImage(rzd_image)
        rzd_label = tk.Label(left_frame, image=self.rzd_photo, bg="#85898A")
        rzd_label.pack(pady=10)

        # Загрузка изображения электровоза
        locomotive_image = Image.open("resources/электровоз.png")
        locomotive_image = locomotive_image.resize((200, 150), Image.Resampling.LANCZOS)  # Изменяем размер изображения
        self.locomotive_photo = ImageTk.PhotoImage(locomotive_image)
        locomotive_label = tk.Label(left_frame, image=self.locomotive_photo, bg="#85898A")
        locomotive_label.pack(pady=10)

        # Авторы
        authors_label = tk.Label(left_frame, text="Авторы:\nМузейный Справочник", font=("Arial", 14), bg="#85898A",
                                 fg="black")
        authors_label.pack(pady=10)

    def create_center_panel(self, parent):
        """Панель управления (центральная колонка)"""
        center_frame = tk.Frame(parent, bg="#85898A", bd=2, relief=tk.RAISED)
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.control_frame = tk.Label(center_frame, text="Панель управления", font=("Arial", 16), bg="#85898A",
                                      fg="black")
        self.control_frame.pack(pady=10)

        # Выбор направления движения
        direction_frame = tk.Frame(center_frame, bg="#85898A")
        direction_frame.pack(pady=10)

        self.direction_label = tk.Label(direction_frame, text="Направление движения:", font=("Arial", 14), bg="#85898A")
        self.direction_label.pack(side=tk.LEFT, padx=10)

        self.direction_var = tk.StringVar(value="-")
        self.direction_option_menu = tk.OptionMenu(direction_frame, self.direction_var, "-", "НАЗ", "ВП")
        self.direction_option_menu.pack(side=tk.LEFT, padx=10)

        # Выбор хода
        gear_frame = tk.Frame(center_frame, bg="#85898A")
        gear_frame.pack(pady=10)

        self.gear_label = tk.Label(gear_frame, text="Выберите ход:", font=("Arial", 14), bg="#85898A")
        self.gear_label.pack(side=tk.LEFT, padx=10)

        self.gear_var = tk.StringVar(value="Тормоз")
        self.gear_option_menu = tk.OptionMenu(gear_frame, self.gear_var, "Тормоз", "Ход 1", "Ход 2", "Ход 3",
                                              command=self.change_gear)
        self.gear_option_menu.pack(side=tk.LEFT, padx=10)

        # Кнопка Экстренный тормоз
        self.emergency_brake_button = tk.Button(center_frame, text="Экстренный тормоз", command=self.emergency_brake,
                                                font=("Arial", 12), bg="#DEDEDC", relief="raised", width=20)
        self.emergency_brake_button.pack(pady=10)

        # Кнопка Гудок
        self.horn_button = tk.Button(center_frame, text="Гудок", command=self.horn,
                                     font=("Arial", 12), bg="#DEDEDC", relief="raised", width=20)
        self.horn_button.pack(pady=10)

        # Кнопка Открыть/Закрыть дверь
        self.door_button = tk.Button(center_frame, text="Открыть/Закрыть дверь", command=self.toggle_door,
                                     font=("Arial", 12), bg="#DEDEDC", relief="raised", width=20)
        self.door_button.pack(pady=10)

        # Кнопка Включить/выключить фары
        self.lights_button = tk.Button(center_frame, text="Включить/выключить фары", command=self.toggle_lights,
                                       font=("Arial", 12), bg="#DEDEDC", relief="raised", width=20)
        self.lights_button.pack(pady=10)

        # Кнопка Компрессор вкл/выкл
        self.compressor_button = tk.Button(center_frame, text="Компрессор вкл/выкл", command=self.toggle_compressor,
                                           font=("Arial", 12), bg="#DEDEDC", relief="raised", width=20)
        self.compressor_button.pack(pady=10)

        # Кнопка Подогрев пульта
        self.heater_button = tk.Button(center_frame, text="Подогрев пульта", command=self.toggle_heater,
                                       font=("Arial", 12), bg="#DEDEDC", relief="raised", width=20)
        self.heater_button.pack(pady=10)

        # Кнопка Освещение кабины
        self.cabin_light_button = tk.Button(center_frame, text="Освещение кабины", command=self.toggle_cabin_lights,
                                            font=("Arial", 12), bg="#DEDEDC", relief="raised", width=20)
        self.cabin_light_button.pack(pady=10)

        # Кнопка Прогрев колодок
        self.pad_heater_button = tk.Button(center_frame, text="Прогрев колодок", command=self.toggle_pad_heater,
                                           font=("Arial", 12), bg="#DEDEDC", relief="raised", width=20)
        self.pad_heater_button.pack(pady=10)

        # Кнопка Стеклоочиститель
        self.wiper_button = tk.Button(center_frame, text="Стеклоочиститель", command=self.toggle_wiper,
                                      font=("Arial", 12), bg="#DEDEDC", relief="raised", width=20)
        self.wiper_button.pack(pady=10)

    def create_right_panel(self, parent):
        """Информационный монитор (правая колонка)"""
        right_frame = tk.Frame(parent, bg="#85898A", bd=2, relief=tk.RAISED)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.monitor_label = tk.Label(right_frame, text="Информационный монитор", font=("Arial", 16), bg="#85898A",
                                      fg="black")
        self.monitor_label.pack(pady=10)

        # Индикатор двери
        self.door_indicator = tk.Label(right_frame, text="Двери: Закрыты", font=("Arial", 14), bg="#85898A",
                                       fg="gray")
        self.door_indicator.pack()

        # Индикатор фар
        self.lights_indicator = tk.Label(right_frame, text="Фары: Выключены", font=("Arial", 14), bg="#85898A",
                                         fg="gray")
        self.lights_indicator.pack()

        # Индикатор состояния компрессора
        self.compressor_status_label = tk.Label(right_frame, text="Компрессор: Выключен", font=("Arial", 14),
                                                bg="#85898A", fg="gray")
        self.compressor_status_label.pack(pady=5)

        # Индикатор подогрева пульта
        self.heater_status_label = tk.Label(right_frame, text="Подогрев пульта: Выключен", font=("Arial", 14),
                                            bg="#85898A", fg="gray")
        self.heater_status_label.pack(pady=5)

        # Индикатор освещения кабины
        self.cabin_lights_status_label = tk.Label(right_frame, text="Освещение кабины: Выключено", font=("Arial", 14),
                                                  bg="#85898A", fg="gray")
        self.cabin_lights_status_label.pack(pady=5)

        # Индикатор прогрева колодок
        self.pad_heater_status_label = tk.Label(right_frame, text="Прогрев колодок: Выключен", font=("Arial", 14),
                                                bg="#85898A", fg="gray")
        self.pad_heater_status_label.pack(pady=5)

        # Индикатор стеклоочистителя
        self.wiper_status_label = tk.Label(right_frame, text="Стеклоочиститель: Выключен", font=("Arial", 14),
                                           bg="#85898A", fg="gray")
        self.wiper_status_label.pack(pady=5)

        # Тормозная магистраль
        self.mileage_indicator = tk.Label(right_frame, text=f"Тормозная магистраль: {self.brake_line} км",
                                          font=("Arial", 14),
                                          bg="#85898A")
        self.mileage_indicator.pack()

        # Тормозной цилиндр
        self.mileage_indicator = tk.Label(right_frame, text=f"Тормозной цилиндр: {self.brake_cylinder} км",
                                          font=("Arial", 14),
                                          bg="#85898A")
        self.mileage_indicator.pack()

        # Пробег
        self.mileage_indicator = tk.Label(right_frame, text=f"Пробег: {self.mileage} км", font=("Arial", 14),
                                          bg="#85898A")
        self.mileage_indicator.pack()

        # Запас хода
        self.range_indicator = tk.Label(right_frame, text=f"Запас хода: {self.range_left} км", font=("Arial", 14),
                                        bg="#85898A")
        self.range_indicator.pack()

        # Количество топлива
        self.fuel_indicator = tk.Label(right_frame, text=f"Топливо: {self.fuel} л", font=("Arial", 14),
                                       bg="#85898A")
        self.fuel_indicator.pack()

        # Индикатор направления движения
        self.status_label = tk.Label(right_frame, text="Направление движения:ВП", font=("Arial", 14), bg="#85898A",
                                     fg="black")
        self.status_label.pack(pady=5)

        # Индикатор скорости
        self.speed_indicator = tk.Label(right_frame, text=f"Скорость: {self.speed} км/ч", font=("Arial", 14),
                                        bg="#85898A")
        self.speed_indicator.pack()

        # Строка спидометра
        self.speed_display_bar(right_frame)

    ################################################################################################
    def speed_display_bar(self, parent):
        """Строка спидометра"""
        self.figure = Figure(figsize=(4, 0.5), facecolor="#85898A")  # Уменьшенный размер
        self.subplot = self.figure.add_subplot(111)
        self.subplot.set_xlim(0, 100)
        self.subplot.set_ylim(0, 1)
        self.subplot.axis('off')
        self.figure.tight_layout()

        # Полоска для отображения скорости
        self.speed_bar = self.subplot.barh(0, self.speed, height=0.5, color='green', edgecolor='black')

        # Разлиновка скорости
        for i in range(0, 101, 10):
            self.subplot.text(i, 0.05, str(i), ha='center', va='bottom', fontsize=8,
                              color='black')  # Отображение значения скорости
            self.subplot.axvline(x=i, color='black', linewidth=0.5, linestyle='--')  # Вертикальная линия

        self.canvas = FigureCanvasTkAgg(self.figure, master=parent)
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
        """Запускаем процесс разгона"""
        self.target_speed = target_speed
        if target_speed == 30 or target_speed == 60:
            self.wheels_fast_sound.stop()
            self.wheels_slow_sound.play()
        if target_speed == 90:
            self.wheels_slow_sound.stop()
            self.wheels_fast_sound.play()
        if target_speed == 0:
            self.wheels_slow_sound.stop()
            self.wheels_fast_sound.stop()
            self.emergency_braking_sound.play()
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
        if target_speed == 30 or target_speed == 60:
            self.wheels_fast_sound.stop()
            self.wheels_slow_sound.play()
        if target_speed == 90:
            self.wheels_slow_sound.stop()
            self.wheels_fast_sound.play()
        if target_speed == 0:
            self.wheels_slow_sound.stop()
            self.wheels_fast_sound.stop()
            self.emergency_braking_sound.play()
        self.slow_down()  # Запускаем процесс торможения

    def slow_down(self):
        """Метод для плавного снижения скорости"""
        if self.speed > self.target_speed:
            self.set_speed(max(self.target_speed, self.speed - 2))  # Плавное снижение скорости
            self.root.after(100, self.slow_down)  # Повторяем через 100 мс

    def start_emergency_slow_down(self, target_speed):
        """Запускаем процесс экстренного торможения"""
        self.target_speed = target_speed
        self.wheels_fast_sound.stop()
        self.emergency_braking_sound.play()
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

    def toggle_compressor(self):
        """Переключение состояния компрессора"""
        self.compressor_on = not self.compressor_on
        if self.compressor_on:
            self.compressor_status_label.config(text="Компрессор: Включен", fg="yellow")
        else:
            self.compressor_status_label.config(text="Компрессор: Выключен", fg="gray")

    def toggle_heater(self):
        """Переключение состояния подогрева пульта"""
        self.heater_on = not self.heater_on
        if self.heater_on:
            self.heater_status_label.config(text="Подогрев пульта: Включен", fg="yellow")
        else:
            self.heater_status_label.config(text="Подогрев пульта: Выключен", fg="gray")

    def toggle_cabin_lights(self):
        """Переключение состояния подогрева пульта"""
        self.cabin_lights_on = not self.cabin_lights_on
        if self.cabin_lights_on:
            self.cabin_lights_status_label.config(text="Освещение кабины: Включено", fg="yellow")
        else:
            self.cabin_lights_status_label.config(text="Освещение кабины: Выключено", fg="gray")


    def toggle_pad_heater(self):
        """Переключение состояния подогрева пульта"""
        self.pad_heater_on = not self.pad_heater_on
        if self.pad_heater_on:
            self.pad_heater_status_label.config(text="Прогрев колодок: Включен", fg="yellow")
        else:
            self.pad_heater_status_label.config(text="Прогрев колодок: Выключен", fg="gray")

    def toggle_wiper(self):
        """Переключение состояния подогрева пульта"""
        self.wiper_on = not self.wiper_on
        if self.wiper_on:
            self.wiper_status_label.config(text="Стеклоочиститель: Включен", fg="yellow")
        else:
            self.wiper_status_label.config(text="Стеклоочиститель: Выключен", fg="gray")


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
            self.fuel -= (self.speed / 3600) / 5  # Расход топлива (5 литров на 1 км)
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
