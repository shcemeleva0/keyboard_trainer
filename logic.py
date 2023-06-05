"""Модуль с логической частью клавиатурного тренажера"""

from collections import defaultdict
import time

from utils import log, match, calculateSpeed, readFromJson, sendToJson, getTextFromChosenFile
from gui import KeyboardTrainApp, KeyboardListener


class KeyboardTrainer:
    """Основной класс логической части клавиатурного тренажера"""
    def __init__(self):
        """Создание приложения и его запуск"""
        self.app = KeyboardTrainApp(self)
        self.app.run()
        self.keyboardInput = None

    def newInput(self, instance):
        """Начинает новую фазу ввода с текстом из текстовой области"""
        log('new')
        insertedText = self.app.TextInputWidget.text
        print (insertedText)
        log('insertedText', insertedText)

        if len(insertedText) == 0:
            return

        self.keyboardInput = KeyboardInput(insertedText,
                                           self.app, self.endInput)
        self.app.newPhrase(self.keyboardInput, insertedText)

    def endInput(self, textLen, totalClicks, inputTime, wrongLetters):
        """Переместить текущие данные в файл со статистикой
        и показать меню со статистикой"""
        nowSpeed = calculateSpeed(textLen, inputTime)
        nowMistakes = totalClicks - textLen

        data = readFromJson()
        if 'totalClicks' in data and data['totalClicks'] != 0:
            data['averageSpeed'] *= data['totalClicks']
            data['averageSpeed'] += totalClicks * nowSpeed
            data['totalClicks'] += totalClicks
            data['averageSpeed'] /= data['totalClicks']
            newWrongLetters = defaultdict(int)
            for letter in data['wrongLetters']:
                newWrongLetters[letter] = data['wrongLetters'][letter]
            for letter in wrongLetters:
                newWrongLetters[letter] += wrongLetters[letter]
            data['wrongLetters'] = newWrongLetters
        else:
            data['averageSpeed'] = nowSpeed
            data['totalClicks'] = totalClicks
            data['wrongLetters'] = wrongLetters
        sendToJson(data)

        log('Your speed:', nowSpeed)
        log('Your time:', round(inputTime, 1))
        log('Your mistakes:', nowMistakes)
        log('Your average speed:', data['averageSpeed'])

        self.keyboardInput = None
        self.app.endMenu(nowSpeed, nowMistakes, data['averageSpeed'])

    def interupt(self, instance):
        """Прерывает входные данные"""
        self.keyboardInput.interupt()

    def reset(self, instance):
        """Удалить всю сохраненную статистику"""
        sendToJson({})
        self.endInput(0, 0, 10, {})

    def loadText(self, instance):
        """Открыть окно для выбора файла и загрузить из него текст для обучения"""
        log('загрузить текст')
        text = getTextFromChosenFile()
        if text is None:
            pass
        else:
            self.app.TextInputWidget.text = text
            #print (self.app.TextInputWidget.text)

class KeyboardInput:
    """Класс фазы одного ввода. Получение входных данных и возврат их в приложение"""
    letterNumber = 0
    startTime = 0
    totalClicks = 0
    needToUnbind = False
    wrongLetters = defaultdict(int)

    def __init__(self, text, app, endFunc):
        """Настройка объекта и привязка слушателя клавиатуры"""
        self.text = text
        self.app = app
        self.endFunc = endFunc
        self.listener = KeyboardListener(self.onKeyDown)

    def onKeyDown(self, keycode, text, modifiers):
        """Срабатывает при событии нажатия клавиши.
        Собирает новую статистику и начинает перерисовывать окно"""
        log('The key', keycode, 'have been pressed')
        log(' - modifiers are %r' % modifiers)
        if self.needToUnbind:
            return True

        if self.startTime == 0:
            self.startTime = time.time()

        if keycode[1] == 'enter':
            text = '\n'
        if keycode[1] == 'tab':
            text = '\t'

        if len(keycode[1]) == 1 or keycode[1] == 'spacebar' or\
           keycode[1] == 'tab' or keycode[1] == 'enter':
            self.totalClicks += 1

        if match(text, self.text[self.letterNumber], modifiers):
            log('Right letter')
            self.letterNumber += 1
            self.app.addLetter(self.letterNumber, self.text)
        else:
            log('Wrong letter', text,
                'I needed:', (self.text[self.letterNumber],))
            self.wrongLetters[self.text[self.letterNumber]] += 1

        if len(self.text) == self.letterNumber:
            self.endInput()
            return True
        return False

    def interupt(self):
        """Прервать ввод и установить необходимость отвязки клавиатуры"""
        self.needToUnbind = True
        self.endInput()

    def endInput(self):
        """Запускает функцию триггера для конца ввода"""
        endTime = time.time()
        self.endFunc(self.letterNumber, self.totalClicks,
                     endTime - self.startTime, self.wrongLetters)