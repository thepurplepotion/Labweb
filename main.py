import io
import base64

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    
    '''
    Функция обработки и представления веб-интерфейса
    '''
    
    graphs = None  # Инициализация переменной графиков
    encoded_img = None  # Инициализация переменной изображения
    
    if request.method == 'POST':
        order = request.form.getlist('order')
        
        img = Image.open('static/images/sample.jpg') # Использование изображения из директории images
        img_arr = np.array(img)
        original_img_arr = img_arr.copy() # Создание копии для сброса изображения
        
        # Изменение порядка цветовых каналов
        if order == ['rbg']:
            img_arr = img_arr[..., ::-1]
        elif order == ['grb']:
            img_arr = img_arr[..., [1, 0, 2]]
        elif order == ['gbr']:
            img_arr = img_arr[..., [1, 2, 0]]
        elif order == ['bgb']:
            img_arr = img_arr[..., [0, 2, 1]]
        elif order == ['bgr']:
            img_arr = img_arr[..., [0, 1, 2]]
        elif order == ['rgb']:
            img_arr = original_img_arr
        else:
            pass  # Порядок не изменяется
            
        # Разделение изображения на цветовые каналы
        r, g, b = img_arr[:, :, 0], img_arr[:, :, 1], img_arr[:, :, 2]
        
        out = io.BytesIO()
        Image.fromarray(img_arr).save(out, format="JPEG")
        out.seek(0)
        encoded_img = base64.b64encode(out.read()).decode('utf-8')
        
        # Генерация графиков
        fig, ax = plt.subplots(2, 2, figsize=(10, 10))
        
        # Гистограммы для каждого цветового канала
        hist_r = ax[0][0].hist(r.flatten(), bins=256, range=(0, 255), density=True, color='r')
        hist_g = ax[0][0].hist(g.flatten(), bins=256, range=(0, 255), density=True, color='g')
        hist_b = ax[0][0].hist(b.flatten(), bins=256, range=(0, 255), density=True, color='b')
        
        ax[0][0].set_title('Distribution of Colors (RGB)')
        
        means_vert = [img_arr[:, i].mean() for i in range(img_arr.shape[1])]
        means_horiz = [img_arr[i, :].mean() for i in range(img_arr.shape[0])]
        
        # Преобразование изображения в двумерный массив
        img_arr_flat = img_arr.reshape(-1, img_arr.shape[-1])
        
        # Нормализация значений пикселей (0-255 -> 0-1)
        norm_img_arr = img_arr_flat / 255
        
        # Создание цветовой карты
        means_colors = [norm_img_arr[:, i].mean() for i in range(norm_img_arr.shape[1])]
        
        ax[0][1].plot(means_vert, label='Vertical Mean', marker='o')
        ax[0][1].set_title('Mean Color Vertically')
        ax[1][0].plot(means_horiz, label='Horizontal Mean', marker='o')
        ax[1][0].set_title('Mean Color Horizontally')
        ax[1][1].plot(means_colors, color='gray', linewidth=3)
        ax[1][1].set_title('Color Map')
        plt.legend()
        
        graph_png = io.BytesIO()
        plt.savefig(graph_png, format='png')
        graph_png.seek(0)
        encoded_graph1 = base64.b64encode(graph_png.read()).decode('utf-8')
        
        graphs = [encoded_graph1]  # Обновление переменной перед возвратом функции
    
    return render_template('index.html', original_img=encoded_img, graphs=graphs)

if __name__ == '__main__':
    app.run(debug=True) # debug запуск