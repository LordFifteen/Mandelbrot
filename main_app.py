import tkinter as tk  # Импорт библиотеки для создания графического интерфейса
import numpy as np  # Импорт библиотеки для работы с массивами и математическими операциями
from PIL import Image, ImageTk  # Импорт библиотеки для работы с изображениями
import time  # Импорт модуля для работы со временем

class FastMandelbrot:
    def __init__(self, width=800, height=600):
        self.root = tk.Tk()  # Создание главного окна приложения
        self.root.title("Мандельброт")  # Установка заголовка окна
        self.root.geometry(f"{width}x{height}")  # Установка размеров окна
        
        self.width = width  # Сохранение ширины области рисования
        self.height = height  # Сохранение высоты области рисования
        self.max_iter = 50  # Установка максимального количества итераций по умолчанию
        
        # Установка начальной области отображения фрактала
        self.x_min, self.x_max = -2.5, 1.5
        self.y_min, self.y_max = -1.5, 1.5
        
        # Создание холста для рисования
        self.canvas = tk.Canvas(self.root, width=width, height=height, bg='black')
        self.canvas.pack()  # Размещение холста в окне
        
        # Создание элементов управления
        self.create_controls()
        
        # Привязка обработчиков событий мыши
        self.canvas.bind("<Button-1>", self.zoom_in)  # Левая кнопка мыши - увеличение
        self.canvas.bind("<Button-3>", self.zoom_out)  # Правая кнопка мыши - уменьшение
        self.canvas.bind("<B1-Motion>", self.on_drag)  # Перетаскивание с левой кнопкой
        self.canvas.bind("<ButtonRelease-1>", self.on_release)  # Отпускание левой кнопки
        
        self.drag_start = None  # Переменная для хранения начальной точки перетаскивания
        self.drag_rect = None  # Переменная для хранения прямоугольника выделения
        
        # Первоначальная отрисовка фрактала
        self.draw_super_fast()
    
    def create_controls(self):
        """Создание панели управления с кнопками"""
        control_frame = tk.Frame(self.root)  # Создание фрейма для элементов управления
        control_frame.pack(fill=tk.X)  # Размещение фрейма с заполнением по ширине
        
        # Кнопка сброса к начальному виду
        tk.Button(control_frame, text="Сброс", command=self.reset, 
                 bg='lightblue', font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        
        # Кнопка для быстрой отрисовки (50 итераций)
        tk.Button(control_frame, text="Быстрая (50 итер)", command=lambda: self.set_iterations(50),
                 bg='lightgreen', font=('Arial', 9)).pack(side=tk.LEFT, padx=2)
        
        # Кнопка для качественной отрисовки (100 итераций)
        tk.Button(control_frame, text="Качественная (100 итер)", command=lambda: self.set_iterations(100),
                 bg='lightyellow', font=('Arial', 9)).pack(side=tk.LEFT, padx=2)
        
        # Кнопка для детальной отрисовки (200 итераций)
        tk.Button(control_frame, text="Детальная (200 итер)", command=lambda: self.set_iterations(200),
                 bg='lightcoral', font=('Arial', 9)).pack(side=tk.LEFT, padx=2)
        
        # Метка для отображения статуса
        self.status = tk.Label(control_frame, text="Готово! Кликайте для зума", 
                              font=('Arial', 10), fg='green')
        self.status.pack(side=tk.RIGHT, padx=10)
    
    def set_iterations(self, iterations):
        """Установка нового количества итераций и перерисовка"""
        self.max_iter = iterations  # Обновление максимального количества итераций
        self.status.config(text=f"Отрисовка {iterations} итераций...")  # Обновление статуса
        self.root.update()  # Принудительное обновление интерфейса
        self.draw_super_fast()  # Перерисовка фрактала
        self.status.config(text="Готово! Кликайте для зума")  # Возврат статуса
    
    def mandelbrot_fast(self, c, max_iter):
        """Векторизованный расчет множества Мандельброта"""
        z = np.zeros_like(c)  # Инициализация массива z нулями
        diverge = np.zeros(c.shape, dtype=bool)  # Массив для отслеживания расходящихся точек
        iterations = np.zeros(c.shape, dtype=int)  # Массив для хранения количества итераций
        
        for i in range(max_iter):  # Цикл по итерациям
            z[diverge == False] = z[diverge == False]**2 + c[diverge == False]  # Формула Мандельброта
            new_diverge = np.abs(z) > 2  # Проверка на расхождение
            diverge_now = new_diverge & (diverge == False)  # Новые расходящиеся точки
            iterations[diverge_now] = i  # Запись номера итерации для новых расходящихся точек
            diverge = diverge | new_diverge  # Обновление массива расходящихся точек
            
            # Ранний выход если все точки дивергировали
            if np.all(diverge):
                break
                
        iterations[diverge == False] = max_iter  # Точки внутри множества получают max_iter
        return iterations  # Возврат массива с количеством итераций
    
    def draw_super_fast(self):
        """Быстрая отрисовка фрактала с использованием векторизации"""
        start_time = time.time()  # Засекаем время начала отрисовки
        
        # Создание сетки координат в комплексной плоскости
        x = np.linspace(self.x_min, self.x_max, self.width)
        y = np.linspace(self.y_min, self.y_max, self.height)
        X, Y = np.meshgrid(x, y)  # Создание матриц координат
        C = X + Y * 1j  # Преобразование в комплексные числа
        
        # Расчет множества Мандельброта
        iterations = self.mandelbrot_fast(C, self.max_iter)
        
        # Создание массива для цветов
        colors = np.zeros((iterations.shape[0], iterations.shape[1], 3), dtype=np.uint8)
        
        # Маска для точек внутри множества Мандельброта
        inside = iterations == self.max_iter
        colors[inside] = [0, 0, 0]  # Черный цвет для точек внутри множества
        
        # Обработка точек вне множества
        outside = ~inside  # Инверсия маски
        t = iterations[outside] / self.max_iter  # Нормализация итераций
        
        # Создание цветовой схемы на основе тригонометрических функций
        r = (np.sin(t * 10) * 127 + 128).astype(np.uint8)  # Красный канал
        g = (np.sin(t * 10 + 2) * 127 + 128).astype(np.uint8)  # Зеленый канал
        b = (np.sin(t * 10 + 4) * 127 + 128).astype(np.uint8)  # Синий канал
        
        colors[outside] = np.stack([r, g, b], axis=1)  # Объединение цветовых каналов
        
        # Создание изображения из массива
        image = Image.fromarray(colors, 'RGB')
        self.photo = ImageTk.PhotoImage(image)  # Преобразование для Tkinter
        
        self.canvas.delete("all")  # Очистка холста
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)  # Отображение изображения
        
        # Обновление заголовка окна с временем отрисовки
        draw_time = time.time() - start_time
        self.root.title(f"⚡ Мандельброт - {draw_time:.2f} сек")
    
    def on_drag(self, event):
        """Обработка перетаскивания мыши для выделения области"""
        if self.drag_start is None:  # Если перетаскивание только началось
            self.drag_start = (event.x, event.y)  # Сохранение начальной точки
            # Создание прямоугольника выделения
            self.drag_rect = self.canvas.create_rectangle(
                event.x, event.y, event.x, event.y, outline='red', width=2
            )
        else:  # Если перетаскивание продолжается
            # Обновление координат прямоугольника
            self.canvas.coords(
                self.drag_rect, 
                self.drag_start[0], self.drag_start[1], 
                event.x, event.y
            )
    
    def on_release(self, event):
        """Обработка отпускания кнопки мыши после выделения области"""
        if self.drag_rect:  # Если был создан прямоугольник выделения
            # Получение координат прямоугольника
            x1, y1, x2, y2 = self.canvas.coords(self.drag_rect)
            self.canvas.delete(self.drag_rect)  # Удаление прямоугольника
            self.drag_rect = None
            
            # Преобразование координат экрана в координаты фрактала
            x_min_new = self.x_min + min(x1, x2) * (self.x_max - self.x_min) / self.width
            x_max_new = self.x_min + max(x1, x2) * (self.x_max - self.x_min) / self.width
            y_min_new = self.y_min + min(y1, y2) * (self.y_max - self.y_min) / self.height
            y_max_new = self.y_min + max(y1, y2) * (self.y_max - self.y_min) / self.height
            
            # Обновление области отображения
            self.x_min, self.x_max = x_min_new, x_max_new
            self.y_min, self.y_max = y_min_new, y_max_new
            
            self.status.config(text="Зумируем...")  # Обновление статуса
            self.root.update()  # Обновление интерфейса
            self.draw_super_fast()  # Перерисовка фрактала
            self.status.config(text="Готово! Кликайте для зума")  # Возврат статуса
        
        self.drag_start = None  # Сброс начальной точки перетаскивания
    
    def zoom_in(self, event):
        """Увеличение в точке клика"""
        # Вычисление центра увеличения в координатах фрактала
        center_x = self.x_min + event.x * (self.x_max - self.x_min) / self.width
        center_y = self.y_min + event.y * (self.y_max - self.y_min) / self.height
        
        # Уменьшение области просмотра в 2 раза
        width = (self.x_max - self.x_min) / 2
        height = (self.y_max - self.y_min) / 2
        
        # Обновление области отображения
        self.x_min = center_x - width / 2
        self.x_max = center_x + width / 2
        self.y_min = center_y - height / 2
        self.y_max = center_y + height / 2
        
        self.status.config(text="Увеличиваем...")  # Обновление статуса
        self.root.update()  # Обновление интерфейса
        self.draw_super_fast()  # Перерисовка фрактала
        self.status.config(text="Готово! Кликайте для зума")  # Возврат статуса
    
    def zoom_out(self, event):
        """Уменьшение в точке клика"""
        # Вычисление центра уменьшения в координатах фрактала
        center_x = self.x_min + event.x * (self.x_max - self.x_min) / self.width
        center_y = self.y_min + event.y * (self.y_max - self.y_min) / self.height
        
        # Увеличение области просмотра в 2 раза
        width = (self.x_max - self.x_min) * 2
        height = (self.y_max - self.y_min) * 2
        
        # Обновление области отображения
        self.x_min = center_x - width / 2
        self.x_max = center_x + width / 2
        self.y_min = center_y - height / 2
        self.y_max = center_y + height / 2
        
        # Ограничения чтобы не уйти слишком далеко
        self.x_min = max(self.x_min, -10)
        self.x_max = min(self.x_max, 10)
        self.y_min = max(self.y_min, -10)
        self.y_max = min(self.y_max, 10)
        
        self.status.config(text="Уменьшаем...")  # Обновление статуса
        self.root.update()  # Обновление интерфейса
        self.draw_super_fast()  # Перерисовка фрактала
        self.status.config(text="Готово! Кликайте для зума")  # Возврат статуса
    
    def reset(self):
        """Сброс к начальному виду"""
        self.x_min, self.x_max = -2.5, 1.5  # Восстановление начальной области
        self.y_min, self.y_max = -1.5, 1.5
        self.max_iter = 50  # Сброс количества итераций
        
        self.status.config(text="Сбрасываем...")  # Обновление статуса
        self.root.update()  # Обновление интерфейса
        self.draw_super_fast()  # Перерисовка фрактала
        self.status.config(text="Готово! Кликайте для зума")  # Возврат статуса
    
    def run(self):
        """Запуск главного цикла приложения"""
        self.root.mainloop()  # Запуск цикла обработки событий

# Запуск приложения
if __name__ == "__main__":
    print("Левый клик - увеличение")  # Инструкция по использованию
    print("Правый клик - уменьшение") 
    print("Зажмите и тяните - выделение области")
    
    app = FastMandelbrot(800, 600)  # Создание экземпляра приложения
    app.run()  # Запуск приложения
