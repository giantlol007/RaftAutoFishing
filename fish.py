import pyautogui 
import cv2
import numpy as np
import time
import threading
from pynput import keyboard
from win10toast import ToastNotifier
import logging
import sys

# Путь к скриншотам
rod_template_path = "C:\\Users\\dimas\\Pictures\\rod_with_durability.png"
lmb_template_path = "C:\\Users\\dimas\\Pictures\\lmb_text.png"
water_template_path = "C:\\Users\\dimas\\Pictures\\water_level.png"
food_template_path = "C:\\Users\\dimas\\Pictures\\food_level.png"

# Логирование ошибок
logging.basicConfig(filename='fish_script_errors.log', level=logging.ERROR, format='%(asctime)s - %(message)s')

# Шаблоны
rod_template = cv2.imread(rod_template_path, cv2.IMREAD_GRAYSCALE)
lmb_template = cv2.imread(lmb_template_path, cv2.IMREAD_GRAYSCALE)
water_template = cv2.imread(water_template_path, cv2.IMREAD_GRAYSCALE)  
food_template = cv2.imread(food_template_path, cv2.IMREAD_GRAYSCALE)

slots = [
    (599, 1011, 662, 1070),
    (674, 1011, 737, 1070),
    (746, 1011, 811, 1070),
    (820, 1011, 884, 1070),
    (892, 1011, 958, 1070),
    (965, 1011, 1031, 1070),
    (1040, 1011, 1106, 1070)
]

slots_without_rod = []

is_paused = False
toaster = ToastNotifier()

def show_message_on_screen(message):
    toaster.show_toast("Уведомление", message, duration=1, threaded=True)

def check_slot_for_rod(slot):
    x1, y1, x2, y2 = slot
    screenshot = pyautogui.screenshot(region=(x1, y1, x2 - x1, y2 - y1))
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)

    result = cv2.matchTemplate(screenshot, rod_template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)

    print(f"Слот: {slot}, совпадение: {max_val}")
    return max_val >= 0.45

def check_lmb_text():
    screenshot = pyautogui.screenshot(region=(935, 445, 51, 28))
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)

    result = cv2.matchTemplate(screenshot, lmb_template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)
    return max_val >= 0.8

def check_water_level():
    screenshot = pyautogui.screenshot(region=(62, 911, 227, 24))
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)

    result = cv2.matchTemplate(screenshot, water_template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)
    print(f"Уровень воды: {max_val}")
    return max_val

def check_food_level():
    screenshot = pyautogui.screenshot(region=(62, 965, 227, 28))
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2GRAY)

    result = cv2.matchTemplate(screenshot, food_template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)
    print(f"Уровень еды: {max_val}")
    return max_val

def change_slot(slot_number):
    if 1 <= slot_number <= 9:
        pyautogui.press(str(slot_number))
    elif slot_number == 10:
        pyautogui.press('0')
    else:
        print("Неверный номер слота.")
    print(f"Перешли в слот {slot_number}")
    time.sleep(1)

def find_working_rod():
    for i, slot in enumerate(slots, 1):
        if i not in slots_without_rod:
            print(f"Проверка слота {i}...")
            if check_slot_for_rod(slot):
                print(f"В слоте {i} есть удочка.")
                return i
            else:
                print(f"В слоте {i} нет удочки. Перехожу к следующему слоту.")
                slots_without_rod.append(i)
    print("Не найдено рабочей удочки.")
    save_and_exit()
    return None

def save_and_exit():
    show_message_on_screen("Не нашёл удочку. Через 20 секунд сохраню игру и выйду в главное меню! Нажмите F3 если хотите приостановить.")
    time.sleep(20)
    show_message_on_screen("Сохраняю игру и выхожу в Главное меню!")
    pyautogui.press('esc')
    time.sleep(1)   
    pyautogui.click(956, 445)
    time.sleep(1)
    pyautogui.click(955, 616)
    time.sleep(1)
    pyautogui.click(900, 574)
    sys.exit()


def drink_water():
    print("Пью...")
    change_slot(9)
    pyautogui.click()
    time.sleep(1)
    pyautogui.click()
    time.sleep(1)

def eat_food():
    print("Кушаю...")
    change_slot(10)
    pyautogui.click()
    time.sleep(1)
    pyautogui.click()
    time.sleep(1)

def pause_check():
    if check_water_level() > 0.8 or check_food_level() > 0.8:
        show_message_on_screen("Рыбалка приостановлена, так как уровень воды или еды не пришёл в норму. Через 20 секунд сохраню игру и выйду в главное меню.")
        time.sleep(20)
        if check_water_level() > 0.8 or check_food_level() > 0.8:
            show_message_on_screen("Сохраняю игру и выхожу в Главное меню!")
            pyautogui.press('esc')
            time.sleep(1)
            pyautogui.click(956, 445)
            time.sleep(1)
            pyautogui.click(955, 616)
            time.sleep(1)
            pyautogui.click(900, 574)
            sys.exit()

def fishing_script():
    global slots_without_rod  # Добавим ссылку на глобальную переменную

    while True:
        if is_paused:
            show_message_on_screen("Скрипт был приостановлен.")
            while is_paused:
                time.sleep(1)
            show_message_on_screen("Скрипт возобновлён.")
            
            # Очищаем список слотов без удочки при возобновлении
            slots_without_rod = []

        # Найти рабочую удочку перед началом
        slot = find_working_rod()
        if not slot:
            print("Не удалось найти рабочую удочку. Завершаю скрипт.")
            save_and_exit()
            return

        change_slot(slot)

        while not is_paused:
            print(f"Текущий слот: {slot}, проверяю состояние удочки...")

            if not check_slot_for_rod(slots[slot - 1]):
                print(f"Удочка в слоте {slot} сломалась. Ищу новую.")
                slots_without_rod.append(slot)
                slot = find_working_rod()
                if not slot:
                    print("Не удалось найти рабочую удочку. Завершаю скрипт.")
                    save_and_exit()
                    return
                change_slot(slot)

            print("Кликаю ЛКМ...")  
            pyautogui.click()
            time.sleep(1)

            print("Ожидаю появления надписи 'LMB'...")
            while not check_lmb_text() and not is_paused:
                time.sleep(1)

            if is_paused:
                break

            print("Найдена надпись 'LMB'. Кликаю ЛКМ...")
            pyautogui.click()
            time.sleep(1)

            # Проверка уровней воды и еды
            if check_water_level() > 0.8:
                show_message_on_screen("Уровень воды низкий, пью!")
                drink_water()
                drink_water()
                print("Проверяю состояние удочки после питья...")

                # После питья проверяем уровень и при необходимости ставим на паузу
                pause_check()
                
                slot = find_working_rod()  # Ищем слот с удочкой заново
                if slot:
                    print(f"Удочка найдена в слоте {slot} после питья. Переключаюсь.")
                    change_slot(slot)  # Переключаемся на слот с удочкой
                else:
                    print("Не удалось найти рабочую удочку после питья. Завершаю скрипт.")
                    save_and_exit()
                    return

            if check_food_level() > 0.8:
                show_message_on_screen("Уровень еды низкий, кушаю!")
                eat_food()
                eat_food()
                print("Проверяю состояние удочки после еды...")

                # После еды проверяем уровень и при необходимости ставим на паузу
                pause_check()

                slot = find_working_rod()  # Ищем слот с удочкой заново
                if slot:
                    print(f"Удочка найдена в слоте {slot} после еды. Переключаюсь.")
                    change_slot(slot)  # Переключаемся на слот с удочкой
                else:
                    print("Не удалось найти рабочую удочку после еды. Завершаю скрипт.")
                    save_and_exit()
                    return

def on_press(key):
    global is_paused
    try:
        if key == keyboard.Key.f1:
            print("Нажата клавиша F1, запускаю скрипт...")
            show_message_on_screen("Скрипт был запущен. Ожидайте 5 секунд.")
            time.sleep(5)
            threading.Thread(target=fishing_script, daemon=True).start()
        elif key == keyboard.Key.f2:
            is_paused = not is_paused
            if is_paused:   
                show_message_on_screen("Скрипт приостановлен.")
            else:
                show_message_on_screen("Скрипт возобновлён.")
        elif key == keyboard.Key.f3:
            show_message_on_screen("Скрипт завершился.")
            time.sleep(2)
            sys.exit()
    except AttributeError:
        pass

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
