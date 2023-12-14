from kivy.core.window import Window
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.screenmanager import ScreenManager, Screen
from matplotlib import pyplot as plt
from kivy.uix.popup import Popup
from datetime import datetime
from scipy import stats
import sqlite3
import numpy


class ArticleScreen(Screen):
    def __init__(self, article_text, **kwargs):
        super(ArticleScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        scroll_view = ScrollView()
        self.label = Label(text=article_text, size_hint_y=None, valign='top')
        self.label.bind(width=lambda *x: setattr(self.label, 'text_size', (self.label.width, None)))
        scroll_view.add_widget(self.label)
        layout.add_widget(scroll_view)
        back_button = Button(text='Назад')
        back_button.bind(on_press=lambda instance: setattr(self.manager, 'current', 'main'))
        layout.add_widget(back_button)
        self.add_widget(layout)

    def on_window_resize(self, window, width, height):
        self.scroll_view.size = (width, height)


class ExhalationApp(App):
    def build(self):
        self.data = []
        self.diary_entries = []
        self.dates = []
        self.database = 'exhalation.db'
        self.initialize_database()
        self.load_data()
        self.screen_manager = ScreenManager()

        # Главный экран и TabbedPanel
        main_screen = Screen(name='main')
        tabbed_panel = TabbedPanel(do_default_tab=False)
        main_screen.add_widget(tabbed_panel)

        # Разделы (вкладки)
        input_tab, history_tab, diary_tab, info_tab = self.create_tabs()

        # Добавление вкладок в tabbed_panel
        tabbed_panel.add_widget(input_tab)
        tabbed_panel.add_widget(history_tab)
        tabbed_panel.add_widget(diary_tab)
        tabbed_panel.add_widget(info_tab)

        # Добавление главного экрана в ScreenManager
        self.screen_manager.add_widget(main_screen)

        # Экраны для статей
        self.create_article_screens()

        return self.screen_manager

    def create_tabs(self):
        # Раздел с вводом данных
        input_tab = TabbedPanelItem(text='Измерения')
        input_layout = BoxLayout(orientation='vertical')
        self.input = TextInput(hint_text='Введите значение силы выдоха', multiline=False)
        self.add_button = Button(text='Добавить измерение')
        self.add_button.bind(on_press=self.add_measurement)
        self.clear_last_button = Button(text='Очистить последнее измерение')
        self.clear_last_button.bind(on_press=self.clear_last_measurement)
        input_layout.add_widget(self.input)
        input_layout.add_widget(self.add_button)
        input_layout.add_widget(self.clear_last_button)
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
        history_layout.add_widget(self.history_scrollview)
        history_layout.add_widget(self.clear_all_button)
        history_layout.add_widget(self.stats_label)
        history_layout.add_widget(self.graph_image)
        history_tab.add_widget(history_layout)

        # Раздел дневника
        diary_tab = TabbedPanelItem(text='Дневник')
        diary_layout = BoxLayout(orientation='vertical')
        self.diary_input = TextInput(hint_text='Запишите свои ощущения или изменения в образе жизни', multiline=True)
        save_diary_button = Button(text='Сохранить запись')
        save_diary_button.bind(on_press=self.save_diary_entry)
        self.diary_display = ScrollView()
        self.diary_label = Label(size_hint_y=None, text_size=(Window.width + 200, None), valign='top')
        self.diary_label.bind(texture_size=self.diary_label.setter('size'))
        self.diary_display.add_widget(self.diary_label)
        diary_layout.add_widget(self.diary_input)
        diary_layout.add_widget(save_diary_button)
        diary_layout.add_widget(self.diary_display)
        diary_tab.add_widget(diary_layout)

        # Раздел с Информацией
        info_tab = TabbedPanelItem(text='Информация')
        info_layout = BoxLayout(orientation='vertical')
        info_scroll_view = ScrollView()
        for i in range(1, 6):
            button = Button(text=f'Статья {i}')
            button.bind(on_press=lambda instance, x=i: self.show_article(x))
            info_layout.add_widget(button)
        info_tab.add_widget(info_layout)

        return input_tab, history_tab, diary_tab, info_tab

    def create_article_screens(self):
        articles = {
            1: "Техника дыхания\nБутейко Этот метод включает в себя упражнения на контроль дыхания для снижения гипервентиляции. Он ориентирован на уменьшение объема дыхания и поддержание спокойного, медленного ритма.",
            2: "Диафрагмальное дыхание\nТакже известное как дыхание животом. Это упражнение помогает использовать диафрагму более эффективно, улучшая воздушный поток и уменьшая усилия при дыхании.",
            3: "Техника дыхания Папворта\nЭта техника сочетает в себе релаксацию и контролируемое дыхание, помогая уменьшить стресс и улучшить дыхание.",
            4: "Йогическое дыхание (пранаяма)\nРазличные формы дыхательных упражнений из йоги, такие как уддияна бандха или анулома-вилома, могут способствовать расслаблению и улучшению контроля дыхания.",
            5: "Упражнения с открытым ртом\nУпражнения, направленные на улучшение дыхания через открытый ртом, могут быть особенно полезными в моменты обострения астмы, так как они помогают уменьшить одышку."
        }
        for i, text in articles.items():
            article_screen = ArticleScreen(text, name=f'article_{i}')
            self.screen_manager.add_widget(article_screen)

    def initialize_database(self):
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS measurements (date TEXT, value REAL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS diary (date TEXT, entry TEXT)''')
        conn.commit()
        conn.close()

    def add_measurement_to_db(self, date, value):
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO measurements (date, value) VALUES (?, ?)', (date, value))
        conn.commit()
        conn.close()

    def add_diary_entry_to_db(self, date, entry):
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO diary (date, entry) VALUES (?, ?)', (date, entry))
        conn.commit()
        conn.close()

    def load_data(self):
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM measurements')
        measurements = cursor.fetchall()
        self.data = [item[1] for item in measurements]
        self.dates = [item[0] for item in measurements]

        cursor.execute('SELECT * FROM diary')
        diary_entries = cursor.fetchall()
        self.diary_entries = [f"[{item[0]}] {item[1]}" for item in diary_entries]

        conn.close()

    def add_measurement(self, instance):
        try:
            value = float(self.input.text)
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.add_measurement_to_db(current_time, value)
            self.data.append(value)
            self.dates.append(current_time)
            self.update_history_label()
            self.update_stats()
            self.update_graph()
            self.input.text = ''
        except ValueError:
            self.input.text = ''
            self.show_error_popup()

    def show_error_popup(self):
        popup = Popup(title='Ошибка ввода',
                      content=Label(text='Введите корректное числовое значение'),
                      size_hint=(None, None),
                      size=(400, 200))
        popup.open()

    def clear_last_measurement(self, instance):
        if self.data:
            self.remove_last_measurement_from_db()
            self.data.pop()
            self.dates.pop()
            self.update_history_label()
            self.update_stats()
            self.update_graph()

    def remove_last_measurement_from_db(self):
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM measurements WHERE rowid = (SELECT MAX(rowid) FROM measurements)')
        conn.commit()
        conn.close()

    def clear_all_measurements_from_db(self):
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM measurements')
        conn.commit()
        conn.close()

    def save_diary_entry(self, instance):
        entry_text = self.diary_input.text.strip()
        if entry_text:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            entry = f"[{timestamp}] {entry_text}"
            self.diary_entries.append(entry)
            self.update_diary_display()
            self.diary_input.text = ''

    def update_history_label(self):
        self.history_label.text = '\n'.join(f'{date}: {value}' for date, value in zip(self.dates, self.data))

    def update_diary_display(self):
        self.diary_label.text = '\n\n'.join(self.diary_entries)

    def clear_all_measurements(self, instance):
        self.clear_all_measurements_from_db()
        self.data.clear()
        self.dates.clear()
        self.update_history_label()
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
            self.graph_image.source = ''
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

    def show_article(self, article_number):
        self.screen_manager.current = f'article_{article_number}'


if __name__ == '__main__':
    ExhalationApp().run()
