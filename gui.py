"""Модуль с графической частью клавиатурного тренажера"""

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.app import App

from config import APP_NAME, WINDOW_SIZE, HINT_TEXT, BACKGROUND_COLOR,\
                   MINIMUM_WIDTH, MINIMUM_HEIGHT
from utils import log, formSpeed, mostMissButtons, showHeatmap


Window.size = WINDOW_SIZE
Window.minimum_width = MINIMUM_WIDTH
Window.minimum_height = MINIMUM_HEIGHT
Window.title = APP_NAME
Window.clearcolor = BACKGROUND_COLOR


class KeyboardTrainApp(App):
    """Основной класс интерфейса клавиатурного тренажера"""
    def __init__(self, kt):
        """Инициализация приложения"""
        super().__init__()
        self.kt = kt
        self.MainLayout = FloatLayout()
        self.TextLabel = Label(text='',
                               markup=True,
                               color=(.0, .0, .0, 1),
                               font_size=15,
                               text_size=(500, 300),
                               pos_hint={'center_x': 0.5,
                                         'center_y': 0.8}
                               )
        self.TextInputWidget = TextInput(hint_text=HINT_TEXT, font_size=30)

    def build(self):
        """Функция запуска приложения.
        Отрисовка стартового меню."""
        self.makeMenu()

        LabelWidget = Label(text=APP_NAME,
                            pos_hint={'top': 1.3},
                            font_size=50,
                            color=(.2, .2, .2, 1))
        self.MainLayout.add_widget(LabelWidget)

        return self.MainLayout

    def newPhrase(self, KeyboardInput, text):
        """Начинается новый этап ввода текста"""
        self.MainLayout.clear_widgets()
        self.TextLabel.text = text
        print(self.TextLabel.text)
        self.MainLayout.add_widget(self.TextLabel)
        # menutext = BoxLayout(spacing=7,
        #                  orientation='vertical',
        #                  size_hint=(.3, .1),
        #                  pos_hint={'top': 0.1, 'right': 0.65})
        # self.MainLayout.add_widget(menutext)
        # menutext.add_widget(self.TextLabel)

        menu = BoxLayout(spacing=7,
                         orientation='vertical',
                         size_hint=(.3, .1),
                         pos_hint={'top': 0.3, 'right': 0.65})


        self.MainLayout.add_widget(menu)

        menu.add_widget(Button(text='В меню',
                               font_size=30,
                               on_press=self.kt.interupt))

        self.MainLayout.add_widget(KeyboardInput.listener)

    def addLetter(self, index, text):
        """Изменение цвета букв на этапе ввода"""
        log(Window.size)
        self.TextLabel.text = '[color=00ff37]' + text[:index] +\
                              '[/color]' + text[index:]
        log((self.TextLabel.text,))

    def endMenu(self, speed, mistakes, averageSpeed):
        """Нарисовать меню со статистикой"""
        self.MainLayout.clear_widgets()

        self.makeMenu()

        newText = "Скорость: " + formSpeed(speed) + '\nОшибки: ' + str(mistakes)
        newText += '\nСредняя скорость: ' + formSpeed(averageSpeed)
        newText += '\nЧасто допускаемые ошибки: ' + mostMissButtons()
        LabelWidget = Label(text=newText,
                            pos_hint={'top': 1.3},
                            font_size=30,
                            color=(.2, .2, .2, 1))
        self.MainLayout.add_widget(LabelWidget)

    def makeMenu(self):
        """Создание меню с кнопками и текстовым полем"""
        menu = BoxLayout(spacing=3,
                         orientation='vertical',
                         size_hint=(.5, .5),
                         pos_hint={'top': 0.6, 'right': 0.75})
        self.MainLayout.add_widget(menu)

        self.TextInputWidget = TextInput(hint_text=HINT_TEXT, font_size=30)
        menu.add_widget(self.TextInputWidget)
        start = BoxLayout(spacing=3,
                          orientation='horizontal')
        start.add_widget(Button(text='Старт',
                                font_size=30,
                                on_press=self.kt.newInput))
        start.add_widget(Button(text='Загрузить текст',
                                font_size=30,
                                on_press=self.kt.loadText))

        menu.add_widget(start)
        menu.add_widget(Button(text='Показать тепловую карту ошибок',
                               font_size=30,
                               on_press=showHeatmap))
        menu.add_widget(Button(text='Сброс статистики',
                               font_size=30,
                               on_press=self.kt.reset))
        menu.add_widget(Button(text='Выход',
                               font_size=30,
                               on_press=exit))

    def insertText(self, text):
        """Изменить текст в виджете ввода текста на заданный"""
        self.TextInputWidget.text = text


class KeyboardListener(Widget):
    """Создание и установка объект пользователя клавиатуры"""
    def __init__(self, triggerFunc):
        """Создание клавиатуры и привязка ее к окну"""
        super().__init__()
        self.triggerFunc = triggerFunc

        self._keyboard = Window.request_keyboard(
                        self._keyboard_closed, self, 'текст')

        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _keyboard_closed(self):
        """Отвязка клавиатуры от окна"""
        log('shutting down keyboard')
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        """Активирует функцию триггера и при необходимости отвязывает клавиатуру """
        needToRelease = self.triggerFunc(keycode, text, modifiers)
        if needToRelease:
            keyboard.release()

        return True