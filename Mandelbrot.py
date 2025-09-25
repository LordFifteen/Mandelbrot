import tkinter as tk
import numpy as np
from PIL import Image, ImageTk
import time

class FastMandelbrot:
    def __init__(self, width=800, height=600):
        self.root = tk.Tk()
        self.root.title("Мандельброт")
        self.root.geometry(f"{width}x{height}")
        
        self.width = width
        self.height = height
        self.max_iter = 50  # Меньше итераций для скорости
        
        # Начальная область
        self.x_min, self.x_max = -2.5, 1.5
        self.y_min, self.y_max = -1.5, 1.5
        
        # Создаем интерфейс
        self.canvas = tk.Canvas(self.root, width=width, height=height, bg='black')
        self.canvas.pack()
        
        # Элементы управления
        self.create_controls()
        
        # Привязываем события
        self.canvas.bind("<Button-1>", self.zoom_in)
        self.canvas.bind("<Button-3>", self.zoom_out)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        
        self.drag_start = None
        self.drag_rect = None
        
        # Первая отрисовка
        self.draw_super_fast()
    
    def create_controls(self):
        """Создание быстрых элементов управления"""
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill=tk.X)
        
        tk.Button(control_frame, text="Сброс", command=self.reset, 
                 bg='lightblue', font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_frame, text="Быстрая (50 итер)", command=lambda: self.set_iterations(50),
                 bg='lightgreen', font=('Arial', 9)).pack(side=tk.LEFT, padx=2)
        
        tk.Button(control_frame, text="Качественная (100 итер)", command=lambda: self.set_iterations(100),
                 bg='lightyellow', font=('Arial', 9)).pack(side=tk.LEFT, padx=2)
        
        tk.Button(control_frame, text="Детальная (200 итер)", command=lambda: self.set_iterations(200),
                 bg='lightcoral', font=('Arial', 9)).pack(side=tk.LEFT, padx=2)
        
        self.status = tk.Label(control_frame, text="Готово! Кликайте для зума", 
                              font=('Arial', 10), fg='green')
        self.status.pack(side=tk.RIGHT, padx=10)
    
    def set_iterations(self, iterations):
        """Быстрая смена качества"""
        self.max_iter = iterations
        self.status.config(text=f"Отрисовка {iterations} итераций...")
        self.root.update()
        self.draw_super_fast()
        self.status.config(text="Готово! Кликайте для зума")
    
    def mandelbrot_fast(self, c, max_iter):
        """Векторизованный расчет Мандельброта"""
        z = np.zeros_like(c)
        diverge = np.zeros(c.shape, dtype=bool)
        iterations = np.zeros(c.shape, dtype=int)
        
        for i in range(max_iter):
            z[diverge == False] = z[diverge == False]**2 + c[diverge == False]
            new_diverge = np.abs(z) > 2
            diverge_now = new_diverge & (diverge == False)
            iterations[diverge_now] = i
            diverge = diverge | new_diverge
            
            # Ранний выход если все точки дивергировали
            if np.all(diverge):
                break
                
        iterations[diverge == False] = max_iter
        return iterations
    
    def draw_super_fast(self):
        """СУПЕР БЫСТРАЯ отрисовка с использованием numpy"""
        start_time = time.time()
        
        # Создаем сетку координат
        x = np.linspace(self.x_min, self.x_max, self.width)
        y = np.linspace(self.y_min, self.y_max, self.height)
        X, Y = np.meshgrid(x, y)
        C = X + Y * 1j
        
        # Векторизованный расчет
        iterations = self.mandelbrot_fast(C, self.max_iter)
        
        # Быстрая цветовая схема
        colors = np.zeros((iterations.shape[0], iterations.shape[1], 3), dtype=np.uint8)
        
        # Маска для точек внутри множества
        inside = iterations == self.max_iter
        colors[inside] = [0, 0, 0]  # Черный
        
        # Цвета для точек вне множества
        outside = ~inside
        t = iterations[outside] / self.max_iter
        
        # Быстрая цветовая схема
        r = (np.sin(t * 10) * 127 + 128).astype(np.uint8)
        g = (np.sin(t * 10 + 2) * 127 + 128).astype(np.uint8)
        b = (np.sin(t * 10 + 4) * 127 + 128).astype(np.uint8)
        
        colors[outside] = np.stack([r, g, b], axis=1)
        
        # Создаем изображение PIL и отображаем
        image = Image.fromarray(colors, 'RGB')
        self.photo = ImageTk.PhotoImage(image)
        
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        
        # Показываем время отрисовки
        draw_time = time.time() - start_time
        self.root.title(f"⚡ Мандельброт - {draw_time:.2f} сек")
    
    def on_drag(self, event):
        """Показываем область зума"""
        if self.drag_start is None:
            self.drag_start = (event.x, event.y)
            self.drag_rect = self.canvas.create_rectangle(
                event.x, event.y, event.x, event.y, outline='red', width=2
            )
        else:
            self.canvas.coords(
                self.drag_rect, 
                self.drag_start[0], self.drag_start[1], 
                event.x, event.y
            )
    
    def on_release(self, event):
        """Зум в выделенную область"""
        if self.drag_rect:
            x1, y1, x2, y2 = self.canvas.coords(self.drag_rect)
            self.canvas.delete(self.drag_rect)
            self.drag_rect = None
            
            # Преобразуем в координаты Мандельброта
            x_min_new = self.x_min + min(x1, x2) * (self.x_max - self.x_min) / self.width
            x_max_new = self.x_min + max(x1, x2) * (self.x_max - self.x_min) / self.width
            y_min_new = self.y_min + min(y1, y2) * (self.y_max - self.y_min) / self.height
            y_max_new = self.y_min + max(y1, y2) * (self.y_max - self.y_min) / self.height
            
            self.x_min, self.x_max = x_min_new, x_max_new
            self.y_min, self.y_max = y_min_new, y_max_new
            
            self.status.config(text="Зумируем...")
            self.root.update()
            self.draw_super_fast()
            self.status.config(text="Готово! Кликайте для зума")
        
        self.drag_start = None
    
    def zoom_in(self, event):
        """Быстрое увеличение"""
        center_x = self.x_min + event.x * (self.x_max - self.x_min) / self.width
        center_y = self.y_min + event.y * (self.y_max - self.y_min) / self.height
        
        width = (self.x_max - self.x_min) / 2
        height = (self.y_max - self.y_min) / 2
        
        self.x_min = center_x - width / 2
        self.x_max = center_x + width / 2
        self.y_min = center_y - height / 2
        self.y_max = center_y + height / 2
        
        self.status.config(text="Увеличиваем...")
        self.root.update()
        self.draw_super_fast()
        self.status.config(text="Готово! Кликайте для зума")
    
    def zoom_out(self, event):
        """Быстрое уменьшение"""
        center_x = self.x_min + event.x * (self.x_max - self.x_min) / self.width
        center_y = self.y_min + event.y * (self.y_max - self.y_min) / self.height
        
        width = (self.x_max - self.x_min) * 2
        height = (self.y_max - self.y_min) * 2
        
        self.x_min = center_x - width / 2
        self.x_max = center_x + width / 2
        self.y_min = center_y - height / 2
        self.y_max = center_y + height / 2
        
        # Ограничения чтобы не уйти слишком далеко
        self.x_min = max(self.x_min, -10)
        self.x_max = min(self.x_max, 10)
        self.y_min = max(self.y_min, -10)
        self.y_max = min(self.y_max, 10)
        
        self.status.config(text="Уменьшаем...")
        self.root.update()
        self.draw_super_fast()
        self.status.config(text="Готово! Кликайте для зума")
    
    def reset(self):
        """Сброс к начальному виду"""
        self.x_min, self.x_max = -2.5, 1.5
        self.y_min, self.y_max = -1.5, 1.5
        self.max_iter = 50
        
        self.status.config(text="Сбрасываем...")
        self.root.update()
        self.draw_super_fast()
        self.status.config(text="Готово! Кликайте для зума")
    
    def run(self):
        self.root.mainloop()

# Запуск
if __name__ == "__main__":
    print("Левый клик - увеличение")
    print("Правый клик - уменьшение") 
    print("Зажмите и тяните - выделение области")
    
    app = FastMandelbrot(800, 600)
    app.run()
