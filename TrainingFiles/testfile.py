import csv
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
import matplotlib.pyplot as plt
from kivy.uix.image import Image
from kivy.core.window import Window
from io import BytesIO
import os
import tempfile

# Глобальные данные для упрощения примера
measurements = []


# Экран для ввода данных
class DataEntryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')

        self.input = TextInput(text='', hint_text='Введите значение силы выдоха', multiline=False)
        layout.add_widget(self.input)

        submit_button = Button(text='Записать')
        submit_button.bind(on_press=self.submit_data)
        layout.add_widget(submit_button)

        switch_button = Button(text='История измерений')
        switch_button.bind(on_press=lambda x: set_screen('history'))
        layout.add_widget(switch_button)

        self.add_widget(layout)

    def submit_data(self, instance):
        value = self.input.text
        try:
            value = float(value)
            measurements.append(value)
            self.input.text = ''
            print(f"Значение '{value}' сохранено")
        except ValueError:
            print("Введите корректное числовое значение")


# Экран истории измерений
class HistoryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.add_widget(self.layout)
        self.on_enter = self.update_history

    def update_history(self):
        self.layout.clear_widgets()
        if measurements:
            for i, value in enumerate(measurements):
                self.layout.add_widget(Label(text=f'Измерение {i + 1}: {value}'))
        else:
            self.layout.add_widget(Label(text='Нет данных для отображения'))

        switch_button = Button(text='Вернуться к вводу данных')
        switch_button.bind(on_press=lambda x: set_screen('entry'))
        self.layout.add_widget(switch_button)

        export_button = Button(text='Экспорт в CSV')
        export_button.bind(on_press=self.export_data)
        self.layout.add_widget(export_button)

        plot_button = Button(text='Показать график')
        plot_button.bind(on_press=self.show_plot)
        self.layout.add_widget(plot_button)

    def export_data(self, instance):
        with open('measurements.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Измерение', 'Значение'])
            for i, value in enumerate(measurements):
                writer.writerow([i + 1, value])
        print("Данные экспортированы в 'measurements.csv'")

    def show_plot(self, instance):
        try:
            plt.figure(figsize=(6, 4))
            plt.plot(measurements, marker='o')
            plt.title('График силы выдоха')
            plt.xlabel('Измерение')
            plt.ylabel('Значение')
            plt.grid(True)

            # Генерация пути к временному файлу
            temp_file_path = tempfile.mktemp(suffix='.png')

            # Сохранение изображения
            plt.savefig(temp_file_path)
            plt.close()

            self.layout.clear_widgets()
            self.layout.add_widget(Image(source=temp_file_path, nocache=True, keep_ratio=True, allow_stretch=True))

            switch_button = Button(text='Вернуться к истории')
            switch_button.bind(on_press=lambda x: self.update_history())
            self.layout.add_widget(switch_button)

        except Exception as e:
            print(f"Произошла ошибка: {e}")


# Функция для переключения экранов
def set_screen(name):
    sm.current = name


# Основной менеджер экранов
sm = ScreenManager()
sm.add_widget(DataEntryScreen(name='entry'))
sm.add_widget(HistoryScreen(name='history'))


class MyApp(App):
    def build(self):
        return sm


if __name__ == '__main__':
    MyApp().run()
