import json

import easygui
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

from config import e2E, e2r, e2R, DEBUG, STAT_FILE_NAME, MAX_SPEED
from char_map import get_all_pixels, get_coords


def log(*args):
    if DEBUG:
        print(*args)


def match(key, target, mod):
    """Совпадает ли нажатая клавиша с целевой буквой"""
    if key == target:
        return True
    if key not in e2E:
        return False
    if ('shift' in mod) ^ ('capslock' in mod):
        return target in (e2R[key], e2E[key])
    return target in (key, e2r[key])


def calculateSpeed(lettersNumber, time):
    """Вычислить скорость по количеству вводимых букв и времени ввода"""
    return 60 * lettersNumber / time


def readFromJson():
    """Считать статистику из файла и вернуть ее в виде словаря"""
    file = open(STAT_FILE_NAME, 'r')
    data = json.load(file)
    file.close()
    return data


def sendToJson(data):
    """Взять словарь с новой статистикой и записать его в файл"""
    file = open(STAT_FILE_NAME, 'w')
    json.dump(data, file)
    file.close()


def formSpeed(speed):
    """Ограничивает скорость для красивого вывода"""
    if speed < MAX_SPEED:
        return str(round(speed, 1))
    return '>' + str(MAX_SPEED)


def getFrequencies(contents):
    """Получение частоты нажатия определенных клавиш в словаре."""
    heatmapData = np.asarray([[0] * 57] * 21)

    for char in contents:
        coords = get_coords(char)
        if coords:
            for coord in coords:
                x, y = coord
                heatmapData[x][y] += contents[char]

    total = np.sum(heatmapData)
    if total != 0:
        heatmapData = heatmapData / total

    for pixel in get_all_pixels(((18, 18), (19, 34))):
        x, y = pixel
        heatmapData[x][y] *= 0.3

    return heatmapData[::-1]


def blendAndShow(contents):
    """Построение тепловой карты, увеличение ее масштаба для клавиатуры
    и вывод смешанного изображения."""
    heatmapData = getFrequencies(contents)
    img = mpimg.imread('keyboard.png')

    plt.clf()
    plt.xticks([])
    plt.yticks([])
    plt.axis('off')

    plt.imshow(heatmapData, interpolation='lanczos', zorder=1,
               cmap='viridis', alpha=0.8)
    plt.imshow(img, extent=(0, 57, 0, 21))
    plt.show()


def getTextFromChosenFile():
    """Загрузка текста из выбранного файла, возвращает None, если файл не был выбран"""
    file_name = easygui.fileopenbox()
    if file_name is None:
        return None
    file = open(file_name, 'r', encoding='utf-8')
    text = file.read()
    file.close()
    return text


def mostMissButtons():
    """Вернуть список с клавишами
    с наибольшим количеством ошибок из статистического файла"""
    data = readFromJson()
    if 'wrongLetters' in data:
        heatmap = [(-c, l) for (l, c) in data['wrongLetters'].items()]
        heatmap.sort()
        return ' '.join([str(x[1]) for x in heatmap][:5])
    return 'No statistics yet'

def showHeatmap(instance):
    """Составить тепловую карту ошибочных кнопок и показать ее"""
    data = readFromJson()
    blendAndShow(data['wrongLetters'])