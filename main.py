from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from matplotlib import pyplot as plt
from kivy.uix.popup import Popup
from datetime import datetime
from scipy import stats
import numpy


class ExhalationApp(App):
    def build(self):
        self.data = []
        self.diary_entries = []
        self.dates = []

        tabbed_panel = TabbedPanel(do_default_tab=False)

        # Раздел с вводом данных
        input_tab = TabbedPanelItem(text='Измерения')
        input_layout = BoxLayout(orientation='vertical')
        self.input = TextInput(hint_text='Введите значение силы выдоха', multiline=False)
        self.add_button = Button(text='Добавить измерение')
        self.add_button.bind(on_press=self.add_measurement)
        input_layout.add_widget(self.input)
        input_layout.add_widget(self.add_button)
        input_tab.add_widget(input_layout)

        # Раздел с историей и графиком
        history_tab = TabbedPanelItem(text='История')
        history_layout = BoxLayout(orientation='vertical')
        self.history_label = Label(size_hint_y=None)
        self.history_scrollview = ScrollView()
        self.history_scrollview.add_widget(self.history_label)
        self.clear_all_button = Button(text='Очистить все измерения')
        self.clear_all_button.bind(on_press=self.clear_all_measurements)
        self.graph_image = Image()
        self.stats_label = Label()
        х
        history_layout.add_widget(self.history_scrollview)
        history_layout.add_widget(self.clear_all_button)
        history_layout.add_widget(self.stats_label)
        history_layout.add_widget(self.graph_image)
        history_tab.add_widget(history_layout)

        # Раздел с Информацией
        info_tab = TabbedPanelItem(text='Информация')
        info_scroll_view = ScrollView()
        info_label = Label(text='Здесь будет информация о том, как правильно измерять силу выдоха, '
                                'влияние различных факторов на показатели и методы их улучшения.',
                           size_hint_y=None,
                           text_size=(tabbed_panel.width + 400, None),
                           valign='center')
        info_label.bind(texture_size=info_label.setter('size'))  # Обновление размера метки при изменении текста
        info_scroll_view.add_widget(info_label)
        info_tab.add_widget(info_scroll_view)

        # Раздел дневника
        diary_tab = TabbedPanelItem(text='Дневник')
        diary_layout = BoxLayout(orientation='vertical')
        self.diary_input = TextInput(hint_text='Запишите свои ощущения или изменения в образе жизни', multiline=True)
        save_diary_button = Button(text='Сохранить запись')
        save_diary_button.bind(on_press=self.save_diary_entry)
        self.diary_display = ScrollView()
        self.diary_label = Label(size_hint_y=None,
                                 text_size=(tabbed_panel.width + 200, None),
                                 valign='top')
        self.diary_label.bind(texture_size=self.diary_label.setter('size'))
        self.diary_display.add_widget(self.diary_label)
        diary_layout.add_widget(self.diary_input)
        diary_layout.add_widget(save_diary_button)
        diary_layout.add_widget(self.diary_display)
        diary_tab.add_widget(diary_layout)

        tabbed_panel.add_widget(input_tab)
        tabbed_panel.add_widget(history_tab)
        tabbed_panel.add_widget(info_tab)
        tabbed_panel.add_widget(diary_tab)

        return tabbed_panel

    # Сохрание значений и проверка на число
    def add_measurement(self, instance):
        try:
            value = float(self.input.text)
            self.data.append(value)
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.dates.append(current_time)
            self.history_label.text += f'\n{current_time}: {value}'
        except ValueError:
            # Если введенное значение не является числом
            self.input.text = ''
            self.show_error_popup

    def show_error_popup(self):
        popup = Popup(title='Ошибка ввода',
                      content=Label(text='Введите корректное числовое значение'),
                      size_hint=(None, None),
                      size=(400, 200))
        popup.open()

    # Сохранение записей в дневник
    def save_diary_entry(self, instance):
        entry_text = self.diary_input.text.strip()
        if entry_text:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            entry = f"[{timestamp}] {entry_text}"
            self.diary_entries.append(entry)
            self.update_diary_display()
            self.diary_input.text = ''  # Очистка поля ввода после сохранения

    def update_diary_display(self):
        self.diary_label.text = '\n\n'.join(self.diary_entries)

    # Очистка вмех записей
    def clear_all_measurements(self, instance):
        self.data.clear()
        self.history_label.text = ''
        self.stats_label.text = ''
        self.update_graph()

    # Очистка последнего измерения
    def clear_last_measurement(self, instance):
        if self.data:
            self.data.pop()
            history = self.history_label.text.split('\n')
            if len(history) > 1:
                self.history_label.text = '\n'.join(history[:-1])
            else:
                self.history_label.text = ''
            self.update_stats()
            self.update_graph()

    def update_stats(self):
        if self.data:
            mean = stats.tmean(self.data)
            median = numpy.median(self.data)
            variance = stats.tvar(self.data)
            self.stats_label.text = f'Среднее: {mean:.2f}, Медиана: {median}, Дисперсия: {variance:.2f}'
        else:
            self.stats_label.text = ''

    def update_graph(self):
        if not self.data:
            self.graph_image.source = ''  # Очистка графика, если нет данных
            return

        plt.figure(figsize=(12, 8))
        plt.plot(self.data, marker='o')
        plt.xlabel('Измерение')
        plt.ylabel('Сила выдоха')
        plt.tight_layout()

        graph_filename = 'temp_graph.png'
        plt.savefig(graph_filename)
        plt.close()

        self.graph_image.source = graph_filename
        self.graph_image.reload()


if __name__ == '__main__':
    ExhalationApp().run()
