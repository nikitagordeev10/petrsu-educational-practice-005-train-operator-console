# библиотеки
import tkinter as tk
from PIL import Image, ImageTk  # Библиотека для работы с изображениями
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pygame
import threading
import time

class ControlPanel:
    ############################ TrainControlPanel #############################
    def __init__(self, root):
        """Окно Пульт машиниста"""
        self.root = root
        self.initialize_window()
        self.initialize_sounds()
        self.initialize_statuses()
        self.create_main_frame()

        # Запуск потока обновления скорости и пробега
        self.running = True
        self.update_speed_thread = threading.Thread(target=self.update_speed)
        self.update_speed_thread.start()

    def initialize_window(self):
        """Инициализация окна приложения"""
        self.root.title("Пульт управления локомотивом")
        self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
        self.root.configure(bg="#85898A")

    def initialize_sounds(self):
        """Инициализация звуков для управления локомотивом"""
        pygame.init()
        pygame.mixer.init()
        self.horn_sound = pygame.mixer.Sound("resources/horn.mp3")
        self.emergency_braking_sound = pygame.mixer.Sound("resources/emergency_braking (1).mp3")
        self.wheels_fast_sound = pygame.mixer.Sound("resources/wheels_fast.mp3")
        self.wheels_slow_sound = pygame.mixer.Sound("resources/wheels_slow.mp3")

    def initialize_statuses(self):
        """Инициализация статусов для управления локомотивом"""
        self.doors_open = False
        self.lights_on = False
        self.heater_on = False
        self.compressor_on = False
        self.wiper_on = False
        self.cabin_lights_on = False
        self.pad_heater_on = False
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

    def create_main_frame(self):
        """Создание основной рамки и колонок интерфейса"""
        main_frame = tk.Frame(self.root, bg="#85898A")
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.machinist_tools_panel(main_frame)
        self.system_status_panel(main_frame)
        self.train_control_panel(main_frame)

############################################################################################
    ########################## MachinistTools #########################
    def create_machinist_tools_frame(self, parent):
        """Создание основной рамки для панели инструментов машиниста"""
        frame = tk.Frame(parent, bg="#85898A", bd=2, relief=tk.RAISED)
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        return frame

    def add_title(self, frame):
        """Добавление заголовка на панель инструментов"""
        title_label = tk.Label(frame, text="Инструменты машиниста", font=("Arial", 16),
                               bg="#85898A", fg="black")
        title_label.pack(pady=10)

    def add_locomotive_image(self, frame):
        """Добавление изображения электровоза на панель инструментов"""
        locomotive_frame = tk.Frame(frame, bg="#85898A", relief=tk.SOLID)
        locomotive_frame.pack(pady=10, fill=tk.X)

        locomotive_image = self.load_image("resources/электровоз.png", (200, 150))
        locomotive_label = tk.Label(locomotive_frame, image=locomotive_image, bg="#85898A")
        locomotive_label.image = locomotive_image  # Сохранение ссылки на изображение
        locomotive_label.pack(pady=10)

    def load_image(self, image_path, size):
        """Загрузка и изменение размера изображения"""
        image = Image.open(image_path)
        image = image.resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(image)

    def add_buttons(self, frame):
        """Добавление кнопок на панель инструментов"""
        self.create_button(frame, "Справочник", self.open_guide)
        self.create_button(frame, "Голосовое управление", self.voice_control)

    def create_button(self, parent, text, command):
        """Создание кнопки с заданным текстом и командой"""
        button_frame = tk.Frame(parent, bg="#85898A")
        button_frame.pack(pady=2, padx=10, fill=tk.X)

        button = tk.Button(button_frame, text=text, command=command,
                           font=("Arial", 10), bg="#DEDEDC", relief="raised", width=20)
        button.pack(fill=tk.X, pady=10)
































    def machinist_tools_panel(self, parent):
        """Создание панели инструментов машиниста"""
        machinist_tools_frame = self.create_machinist_tools_frame(parent)
        self.add_title(machinist_tools_frame)
        self.add_locomotive_image(machinist_tools_frame)
        self.add_buttons(machinist_tools_frame)

    def train_control_panel(self, parent):
        """Панель управления (правая колонка)"""
        center_frame = self.train_control_frame(parent)
        self.add_control_title(center_frame)
        self.add_direction_selection(center_frame)
        self.add_gear_selection(center_frame)
        self.add_emergency_brake_button(center_frame)
        self.add_horn_button(center_frame)
        self.add_door_button(center_frame)
        self.add_lights_button(center_frame)
        self.add_compressor_button(center_frame)
        self.add_heater_button(center_frame)
        self.add_cabin_light_button(center_frame)
        self.add_pad_heater_button(center_frame)
        self.add_wiper_button(center_frame)



    ################################ SystemStatuses ################################################################
    def system_status_panel(self, parent):
        """Состояние системы"""
        right_frame = tk.Frame(parent, bg="#85898A", bd=2, relief=tk.RAISED)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.monitor_label = tk.Label(right_frame, text="Состояние системы", font=("Arial", 16), bg="#85898A",
                                      fg="black")
        self.monitor_label.pack(pady=10)

        # Индикатор двери
        self.door_frame = tk.Frame(right_frame, bg="white", bd=2, relief=tk.SUNKEN)  # Сохраняем door_frame
        self.door_frame.pack(fill=tk.X, padx=5, pady=5)
        self.door_indicator = tk.Label(self.door_frame, text="Двери: Закрыты", font=("Arial", 10),
                                       fg="black")
        self.door_indicator.pack(padx=10, pady=5)

        # Индикатор фар
        self.lights_frame = tk.Frame(right_frame, bg="white", bd=2, relief=tk.SUNKEN)
        self.lights_frame.pack(fill=tk.X, padx=5, pady=5)
        self.lights_indicator = tk.Label(self.lights_frame, text="Фары: Выключены", font=("Arial", 10),
                                         fg="black")
        self.lights_indicator.pack(padx=10, pady=5)

        # Индикатор состояния компрессора
        self.compressor_frame = tk.Frame(right_frame, bg="white", bd=2, relief=tk.SUNKEN)
        self.compressor_frame.pack(fill=tk.X, padx=5, pady=5)
        self.compressor_indicator = tk.Label(self.compressor_frame, text="Компрессор: Выключен", font=("Arial", 10),
                                                fg="black")
        self.compressor_indicator.pack(padx=10, pady=5)

        # Индикатор подогрева пульта
        self.heater_frame = tk.Frame(right_frame, bg="white", bd=2, relief=tk.SUNKEN)
        self.heater_frame.pack(fill=tk.X, padx=5, pady=5)
        self.heater_indicator = tk.Label(self.heater_frame, text="Подогрев пульта: Выключен", font=("Arial", 10),
                                           fg="black")
        self.heater_indicator.pack(padx=10, pady=5)

        # Индикатор освещения кабины
        self.cabin_lights_frame = tk.Frame(right_frame, bg="white", bd=2, relief=tk.SUNKEN)
        self.cabin_lights_frame.pack(fill=tk.X, padx=5, pady=5)
        self.cabin_lights_indicator = tk.Label(self.cabin_lights_frame, text="Освещение кабины: Выключено",
                                                  font=("Arial", 10), fg="black")
        self.cabin_lights_indicator.pack(padx=10, pady=5)

        # Индикатор прогрева колодок
        self.pad_heater_frame = tk.Frame(right_frame, bg="white", bd=2, relief=tk.SUNKEN)
        self.pad_heater_frame.pack(fill=tk.X, padx=5, pady=5)
        self.pad_heater_indicator = tk.Label(self.pad_heater_frame, text="Прогрев колодок: Выключен", font=("Arial", 10),
                                                bg="white", fg="black")
        self.pad_heater_indicator.pack(padx=10, pady=5)

        # Индикатор стеклоочистителя
        self.wiper_frame = tk.Frame(right_frame, bg="white", bd=2, relief=tk.SUNKEN)
        self.wiper_frame.pack(fill=tk.X, padx=5, pady=5)
        self.wiper_indicator = tk.Label(self.wiper_frame, text="Стеклоочиститель: Выключен", font=("Arial", 10),
                                           fg="black")
        self.wiper_indicator.pack(padx=10, pady=5)

        # Тормозная магистраль
        self.mileage_frame = tk.Frame(right_frame, bg="white", bd=2, relief=tk.SUNKEN)
        self.mileage_frame.pack(fill=tk.X, padx=5, pady=5)
        self.mileage_indicator = tk.Label(self.mileage_frame, text=f"Тормозная магистраль: {self.brake_line} МПа",
                                          font=("Arial", 10), fg="black")
        self.mileage_indicator.pack(padx=10, pady=5)

        # Тормозной цилиндр
        self.brake_cylinder_frame = tk.Frame(right_frame, bg="white", bd=2, relief=tk.SUNKEN)
        self.brake_cylinder_frame.pack(fill=tk.X, padx=5, pady=5)
        self.brake_cylinder_indicator = tk.Label(self.brake_cylinder_frame,
                                                 text=f"Тормозной цилиндр: {self.brake_cylinder} МПа",
                                                 font=("Arial", 10),fg="black")
        self.brake_cylinder_indicator.pack(padx=10, pady=5)

        # Пробег
        self.mileage_frame = tk.Frame(right_frame, bg="white", bd=2, relief=tk.SUNKEN)
        self.mileage_frame.pack(fill=tk.X, padx=5, pady=5)
        self.mileage_indicator = tk.Label(self.mileage_frame, text=f"Пробег: {self.mileage} км", font=("Arial", 10),
                                           fg="black")
        self.mileage_indicator.pack(padx=10, pady=5)

        # Запас хода
        self.range_frame = tk.Frame(right_frame, bg="white", bd=2, relief=tk.SUNKEN)
        self.range_frame.pack(fill=tk.X, padx=5, pady=5)
        self.range_indicator = tk.Label(self.range_frame, text=f"Запас хода: {self.range_left} км", font=("Arial", 10),
                                         fg="black")
        self.range_indicator.pack(padx=10, pady=5)

        # Количество топлива
        fuel_frame = tk.Frame(right_frame, bg="white", bd=2, relief=tk.SUNKEN)
        fuel_frame.pack(fill=tk.X, padx=5, pady=5)
        self.fuel_indicator = tk.Label(fuel_frame, text=f"Топливо: {self.fuel} л", font=("Arial", 10),
                                       fg="black")
        self.fuel_indicator.pack(padx=10, pady=5)

        # Индикатор направления движения
        status_frame = tk.Frame(right_frame, bg="white", bd=2, relief=tk.SUNKEN)
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        self.indicator = tk.Label(status_frame, text="Направление движения: ВП", font=("Arial", 10),
                                     fg="black")
        self.indicator.pack(padx=10, pady=5)

        # Индикатор скорости
        speed_frame = tk.Frame(right_frame, bg="white", bd=2, relief=tk.SUNKEN)
        speed_frame.pack(fill=tk.X, padx=5, pady=5)
        self.speed_indicator = tk.Label(speed_frame, text=f"Скорость: {self.speed} км/ч", font=("Arial", 10),
                                         fg="black")
        self.speed_indicator.pack(padx=10, pady=5)

        # Строка спидометра
        self.speed_display_bar(right_frame)

        ########################### TrainControl ###########################
        def train_control_frame(self, parent):
            """Создание основной рамки для панели управления поездом"""
            frame = tk.Frame(parent, bg="#85898A", bd=2, relief=tk.RAISED)
            frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
            return frame

        def add_control_title(self, frame):
            """Добавление заголовка на панель управления"""
            title_label = tk.Label(frame, text="Управление поездом", font=("Arial", 16), bg="#85898A", fg="black")
            title_label.pack(pady=10)

        def add_direction_selection(self, frame):
            """Добавление выбора направления движения"""
            direction_frame = tk.Frame(frame, bg="#85898A")
            direction_frame.pack(pady=2, padx=10, fill=tk.X)

            direction_label = tk.Label(direction_frame, text="Направление движения:", font=("Arial", 10), bg="#85898A")
            direction_label.pack(side=tk.LEFT, padx=10)

            self.direction_var = tk.StringVar(value="-")
            self.direction_option_menu = tk.OptionMenu(direction_frame, self.direction_var, "-", "НАЗ", "ВП")
            self.direction_option_menu.pack(side=tk.LEFT, padx=10)

        def add_gear_selection(self, frame):
            """Добавление выбора хода"""
            gear_frame = tk.Frame(frame, bg="#85898A")
            gear_frame.pack(pady=2, padx=10, fill=tk.X)

            gear_label = tk.Label(gear_frame, text="Выберите ход:", font=("Arial", 10), bg="#85898A")
            gear_label.pack(side=tk.LEFT, padx=10)

            self.gear_var = tk.StringVar(value="Тормоз")
            self.gear_option_menu = tk.OptionMenu(gear_frame, self.gear_var, "Тормоз", "Ход 1", "Ход 2", "Ход 3",
                                                  command=self.change_gear)
            self.gear_option_menu.pack(side=tk.LEFT, padx=10)

        def add_emergency_brake_button(self, frame):
            """Добавление кнопки экстренного тормоза"""
            self.create_button(frame, "Экстренный тормоз", self.emergency_brake)

        def add_horn_button(self, frame):
            """Добавление кнопки гудка"""
            self.create_button(frame, "Гудок", self.horn)

        def add_door_button(self, frame):
            """Добавление кнопки открытия/закрытия двери"""
            self.create_button(frame, "Открыть/Закрыть дверь", self.toggle_door)

        def add_lights_button(self, frame):
            """Добавление кнопки включения/выключения фар"""
            self.create_button(frame, "Включить/выключить фары", self.toggle_lights)

        def add_compressor_button(self, frame):
            """Добавление кнопки включения/выключения компрессора"""
            self.create_button(frame, "Включить/выключить компрессор", self.toggle_compressor)

        def add_heater_button(self, frame):
            """Добавление кнопки подогрева пульта"""
            self.create_button(frame, "Подогрев пульта", self.toggle_heater)

        def add_cabin_light_button(self, frame):
            """Добавление кнопки освещения кабины"""
            self.create_button(frame, "Освещение кабины", self.toggle_cabin_lights)

        def add_pad_heater_button(self, frame):
            """Добавление кнопки прогрева колодок"""
            self.create_button(frame, "Прогрев колодок", self.toggle_pad_heater)

        def add_wiper_button(self, frame):
            """Добавление кнопки стеклоочистителя"""
            self.create_button(frame, "Стеклоочиститель", self.toggle_wiper)

        def create_button(self, parent, text, command):
            """Создание кнопки с заданным текстом и командой"""
            button_frame = tk.Frame(parent, bg="#85898A")
            button_frame.pack(pady=2, padx=10, fill=tk.X)

            button = tk.Button(button_frame, text=text, command=command,
                               font=("Arial", 10), bg="#DEDEDC", relief="raised", width=20)
            button.pack(fill=tk.X, pady=10)


    def on_closing(self):
        self.running = False
        self.root.destroy()

    def toggle_door(self):
        self.doors_open = not self.doors_open
        if self.doors_open:
            self.door_frame.config(bg="yellow")  # Меняем цвет фона фрейма
            self.door_indicator.config(text="Двери: Открыты")
        else:
            self.door_frame.config(bg="white")  # Возвращаем цвет фона фрейма обратно
            self.door_indicator.config(text="Двери: Закрыты")

    def toggle_lights(self):
        self.lights_on = not self.lights_on
        if self.lights_on:
            self.lights_frame.config(bg="yellow")  # Меняем цвет фона фрейма
            self.lights_indicator.config(text="Фары: Включены")
        else:
            self.lights_frame.config(bg="white")  # Возвращаем цвет фона фрейма обратно
            self.lights_indicator.config(text="Фары: Выключены")

    def toggle_compressor(self):
        """Переключение состояния компрессора"""
        self.compressor_on = not self.compressor_on
        if self.compressor_on:
            self.compressor_frame.config(bg="yellow")  # Меняем цвет фона фрейма
            self.compressor_indicator.config(text="Компрессор: Включен")
        else:
            self.compressor_frame.config(bg="white")  # Возвращаем цвет фона фрейма обратно
            self.compressor_indicator.config(text="Компрессор: Выключен")

    def toggle_heater(self):
        """Переключение состояния подогрева пульта"""
        self.heater_on = not self.heater_on
        if self.heater_on:
            self.heater_frame.config(bg="yellow")  # Меняем цвет фона фрейма
            self.heater_indicator.config(text="Подогрев пульта: Включен")
        else:
            self.heater_frame.config(bg="white")  # Возвращаем цвет фона фрейма обратно
            self.heater_indicator.config(text="Подогрев пульта: Выключен")

    def toggle_cabin_lights(self):
        """Переключение состояния подогрева пульта"""
        self.cabin_lights_on = not self.cabin_lights_on
        if self.cabin_lights_on:
            self.cabin_lights_frame.config(bg="yellow")  # Меняем цвет фона фрейма
            self.cabin_lights_indicator.config(text="Освещение кабины: Включено")
        else:
            self.cabin_lights_frame.config(bg="white")  # Возвращаем цвет фона фрейма обратно
            self.cabin_lights_indicator.config(text="Освещение кабины: Выключено")

    def toggle_pad_heater(self):
        """Переключение состояния подогрева пульта"""
        self.pad_heater_on = not self.pad_heater_on
        if self.pad_heater_on:
            self.pad_heater_frame.config(bg="yellow")  # Меняем цвет фона фрейма
            self.pad_heater_indicator.config(text="Прогрев колодок: Включен")
        else:
            self.pad_heater_frame.config(bg="white")  # Возвращаем цвет фона фрейма обратно
            self.pad_heater_indicator.config(text="Прогрев колодок: Выключен")

    def toggle_wiper(self):
        """Переключение состояния подогрева пульта"""
        self.wiper_on = not self.wiper_on
        if self.wiper_on:
            self.wiper_frame.config(bg="yellow")  # Меняем цвет фона фрейма
            self.wiper_indicator.config(text="Стеклоочиститель: Включен")
        else:
            self.wiper_frame.config(bg="white")  # Возвращаем цвет фона фрейма обратно
            self.wiper_indicator.config(text="Освещение кабины: Выключено")

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

    def voice_control(self):
        pass

    ############################################ Guide ####################################################
    def open_guide(self):
        """Открывает новое окно со справочной информацией."""
        if self.guide_window is None or not self.guide_window.winfo_exists():
            self.guide_window = tk.Toplevel(self.root)
            self.guide_window.title("Справочник")
            self.guide_window.geometry("600x400")
            self.guide_window.configure(bg="#85898A")

            # Заголовок справочника
            guide_title = tk.Label(self.guide_window, text="Справочник", font=("Arial", 18, "bold"), bg="#85898A",
                                   fg="black")
            guide_title.pack(pady=10)

            # Текстовая информация
            guide_text = tk.Text(self.guide_window, wrap=tk.WORD, font=("Arial", 10), bg="#DEDEDC", fg="black")
            guide_text.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

            # Добавление содержимого справочника
            guide_content = """Добро пожаловать в справочник по управлению локомотивом. 
    Здесь вы найдете основную информацию по элементам управления:

    1. Пульт управления — содержит все важные элементы для контроля движения локомотива.
    2. Тормозная система — отвечает за управление скоростью и остановкой локомотива.
    3. Освещение — управление фарами и освещением кабины машиниста.
    4. Компрессор — необходим для работы пневматических систем локомотива.
    5. Стеклоочистители — используются для поддержания видимости в плохую погоду.

    Более подробную информацию вы найдете в соответствующих разделах документации."""

            guide_text.insert(tk.END, guide_content)
            guide_text.config(state=tk.DISABLED)  # Запретить редактирование текста

            # Кнопка закрытия справочника
            close_button = tk.Button(self.guide_window, text="Закрыть", command=self.guide_window.destroy,
                                     font=("Arial", 10), bg="#DEDEDC", relief="raised", width=20)
            close_button.pack(pady=10)

        else:
            # Если окно уже открыто, активируем его
            self.guide_window.lift()
