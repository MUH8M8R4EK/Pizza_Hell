import random as r
import time
import json
import tkinter as tk
from tkinter import messagebox

# Константы
BASE_COST = 10  # Базовая стоимость пиццы
DEMON_PATIENCE = 3  # Максимальное количество отказов, после которого демоны прогонят повара
LEVEL_UP_THRESHOLD = [250, 500, 1000, 2000]  # Суммы денег для повышения уровня
UPGRADE_COST = 20  # Базовая стоимость улучшения оборудования
WIN_LEVEL = 5  # Уровень, на котором игра заканчивается

# Начальные значения для MAX_TIME и количества ингредиентов
INITIAL_MAX_TIME = 30  # Время для приготовления одной пиццы
INITIAL_INGREDIENTS_COUNT_MIN = 2
INITIAL_INGREDIENTS_COUNT_MAX = 4

# Ингредиенты
ingredients = [
    ["Огненный соус", 4, 1.1],
    ["Пепперони из ада", 8, 1.5],
    ["Луковая смерть", 6, 1.3],
    ["Мученический микс", 9, 1.6],
    ["Четыре мира", 7, 1.4],
    ["Ядовитая моцарелла", 5, 1.2],
    ["Валькири шейк", 3, 1.7],
]

# Список новых ингредиентов для открытия
new_ingredients = [
    ["Двойной Данте", 10, 1.4],
    ["Сибирская язва", 7, 1.3],
    ["Ведьмин костер", 12, 1.5],
    ["Нектар преисподней", 9, 1.6],
    ["Костлявые конфеты", 8, 1.4]
]

# Демоны и их заказы
demons = [
    "Баал", "Левиафан", "Астарот", "Лилит", "Маммон", "Агамон", "Адонис", "Бельфегор", "Асмодей", "Вельзевул", "Левиафан"
]

def random_demon_order(level):
    min_ingredients = INITIAL_INGREDIENTS_COUNT_MIN + level // 2
    max_ingredients = INITIAL_INGREDIENTS_COUNT_MAX + level // 2
    return r.sample(ingredients, r.randint(min_ingredients, max_ingredients))

class StartScreen:
    def __init__(self, root, game):
        self.root = root
        self.game = game
        self.root.title("Адская пиццерия - Вход")
        
        # Создаем и размещаем элементы стартового экрана
        self.name_label = tk.Label(root, text="Введите ваше имя:", font=("Arial", 12))
        self.name_label.pack(pady=10)
        
        self.name_entry = tk.Entry(root, font=("Arial", 12))
        self.name_entry.pack(pady=5)
        self.name_entry.bind('<Return>', lambda event: self.start_game())  # Добавляем обработчик нажатия Enter

        
        self.start_button = tk.Button(root, text="Начать игру", command=self.start_game)
        self.start_button.pack(pady=10)
        
    def start_game(self):
        player_name = self.name_entry.get().strip()
        
        # Проверка на пустое имя
        if not player_name:
            messagebox.showerror("Ошибка", "Пожалуйста, введите имя!")
            return
            
        # Проверка на существующее имя в таблице лидеров
        try:
            with open('leaderboard.json', 'r') as f:
                leaderboard = json.load(f)
                if any(entry[0] == player_name for entry in leaderboard):
                    if not messagebox.askyesno("Предупреждение", 
                        "Игрок с таким именем уже существует. Хотите продолжить?"):
                        return
        except FileNotFoundError:
            pass
            
        # Удаляем стартовый экран
        self.name_label.destroy()
        self.name_entry.destroy()
        self.start_button.destroy()
        
        # Запускаем основную игру
        self.game.player_name = player_name
        self.game.start_time = time.time()
        print(f"Добро пожаловать в адскую пиццерию, {player_name}!")
        GameGUI(self.root, self.game)

class Pizza:
    def __init__(self):
        self.ingredients = []
        self.cost = BASE_COST
        self.multiplier = 1.0
        self.time_multiplier = 1.0
        self.cost_multiplier = 1.0

    def add_ingredient(self, ingredient):
        self.ingredients.append(ingredient[0])
        self.cost += ingredient[1]
        self.multiplier *= ingredient[2]

    def calculate_price(self):
        return round(self.cost * self.multiplier * self.cost_multiplier, 2)

    def get_preparation_time(self, base_time):
        return base_time * self.time_multiplier

class Chef:
    def __init__(self):
        self.money = 50
        self.reputation = 3
        self.level = 1
        self.successful_orders = 0
        self.equipment = {
            "oven": 1,
            "tools": 1,
            "fridge": 1
        }
        self.next_level_cost = LEVEL_UP_THRESHOLD[0]  # Стоимость следующего уровня

    def show_stats(self):
        return (
            f"Деньги: {self.money} | Репутация: {self.reputation} | Уровень: {self.level}\n"
            f"Уровень печи: {self.equipment['oven']} | Уровень инструментов: {self.equipment['tools']} | Уровень холодильника: {self.equipment['fridge']}"
        )

    def lose_reputation(self):
        self.reputation -= 1
        if self.reputation <= 0:
            print("Демоны прогнали вас из кухни ада! Игра окончена.")
            return False
        return True

    def earn_money(self, amount):
        self.money += amount

    def level_up(self):
        if self.money >= self.next_level_cost and self.level < WIN_LEVEL:
            self.money -= self.next_level_cost
            self.level += 1
            if self.level < WIN_LEVEL:
                self.next_level_cost = LEVEL_UP_THRESHOLD[self.level - 1]
            else:
                self.next_level_cost = 0  # На последнем уровне нет стоимости
            return True
        return False

    def upgrade_equipment(self, equipment_type):
        upgrade_cost = UPGRADE_COST + (self.equipment["oven"] + self.equipment["tools"] + self.equipment["fridge"] - 3) * 10
        if self.money >= upgrade_cost:
            self.money -= upgrade_cost
            self.equipment[equipment_type] += 1
            return True
        return False

    def apply_equipment_effects(self, pizza):
        pizza.time_multiplier = max(0.5, 1 - (self.equipment["oven"] * 0.1))
        pizza.cost_multiplier = max(0.5, 1 - (self.equipment["tools"] * 0.1))

class GameGUI:
    def __init__(self, root, game):
        self.root = root
        self.game = game
        self.root.title("Адская пиццерия")

        # Создание элементов интерфейса
        self.game_time_label = tk.Label(root, text=f"Общее время: {self.game.start_time:.2f} сек.", font=("Arial", 12), fg="red")
        self.game_time_label.pack(pady=10)

        self.stats_label = tk.Label(root, text="Статистика", font=("Arial", 12), justify="left")
        self.stats_label.pack(pady=10)

        # Кнопка "Принять заказ"
        self.accept_order_button = tk.Button(root, text="Принять заказ", command=self.accept_order)
        self.accept_order_button.pack(pady=10)
        self.accept_order_button.bind("<Enter>", self.on_enter)
        self.accept_order_button.bind("<Leave>", self.on_leave)

        # Кнопка "Улучшить оборудование"
        self.upgrade_button = tk.Button(root, text="Улучшить оборудование", command=self.upgrade_equipment)
        self.upgrade_button.pack(pady=10)
        self.upgrade_button.bind("<Enter>", self.on_enter)
        self.upgrade_button.bind("<Leave>", self.on_leave)

        # Кнопка "Выход"
        self.exit_button = tk.Button(root, text="Выход", command=self.end_game)
        self.exit_button.pack(pady=10)
        self.exit_button.bind("<Enter>", self.on_enter)
        self.exit_button.bind("<Leave>", self.on_leave)

        # Элементы для заказа (скрыты изначально)
        self.order_frame = tk.Frame(root)
        self.order_label = tk.Label(self.order_frame, text="Заказ демона:", font=("Arial", 12))
        self.timer_label = tk.Label(self.order_frame, text="Оставшееся время:", font=("Arial", 12))
        self.ingredients_buttons = []  # Список кнопок для ингредиентов
        
        # Метка для поздравления
        self.congrats_label = tk.Label(root, text="", font=("Arial", 14), fg="green")
        
        # Метка для случайного события
        self.event_label = tk.Label(root, text="", font=("Arial", 14), fg="orange")

        # Элементы для улучшения оборудования (скрыты изначально)
        self.upgrade_frame = tk.Frame(root)
        self.upgrade_labels = {}
        self.upgrade_buttons = {}

        # Скрываем фреймы заказа и улучшения
        self.order_frame.pack_forget()
        self.upgrade_frame.pack_forget()

        # Инициализация таймера игры
        self.start_time = time.time()
        self.update_game_time()

        # Список выбранных ингредиентов
        self.selected_ingredients = []
        
        # Текущий заказ и время на его выполнение
        self.current_order = None
        self.preparation_time = None
        self.order_start_time = None

    def update_game_time(self):
        elapsed_time = time.time() - self.start_time
        self.game_time_label.config(text=f"Общее время: {elapsed_time:.2f} сек.")
        self.root.after(1000, self.update_game_time)

    def on_enter(self, event):
        event.widget.config(bg='lightblue')

    def on_leave(self, event):
        event.widget.config(bg='SystemButtonFace')  # Возвращаем стандартный цвет кнопки

    def update_stats(self):
        stats_text = self.game.chef.show_stats()
        self.stats_label.config(text=stats_text)

    def show_random_event(self, event_text, time_adjustment, stolen_ingredient=None):
        # Скрываем все элементы
        self.stats_label.pack_forget()
        self.accept_order_button.pack_forget()
        self.upgrade_button.pack_forget()
        self.exit_button.pack_forget()
        
        # Показываем описание случайного события
        if stolen_ingredient:
            self.event_label.config(text=f"СЛУЧАЙНОЕ СОБЫТИЕ:\n{event_text}\nУкраден ингредиент: {stolen_ingredient[0]}")
        else:
            self.event_label.config(text=f"СЛУЧАЙНОЕ СОБЫТИЕ:\n{event_text}")
        self.event_label.pack(pady=20)
        
        # Через 2 секунды продолжаем с заказом
        self.root.after(2000, lambda: self.continue_after_event(time_adjustment))

    def continue_after_event(self, time_adjustment):
        # Скрываем описание события
        self.event_label.pack_forget()
        
        # Продолжаем с обычным заказом
        self.preparation_time += time_adjustment if isinstance(time_adjustment, int) else 0
        self.start_order_ui()

    def accept_order(self):
        # Скрываем начальные кнопки
        self.accept_order_button.pack_forget()
        self.upgrade_button.pack_forget()
        self.exit_button.pack_forget()

        # Очищаем список выбранных ингредиентов
        self.selected_ingredients = []

        # Генерируем новый заказ демона
        demon = r.choice(demons)
        self.current_order = random_demon_order(self.game.chef.level)
        
        # Рассчитываем время на выполнение заказа
        self.preparation_time = max(INITIAL_MAX_TIME - (self.game.chef.level - 1) * 2, 5)

        # Если уровень >= 2, генерируем случайное событие
        if self.game.chef.level >= 2:
            events = [
                ("Духи украли ингредиенты!", self.game.steal_ingredient),
                ("Печь перегрелась!", lambda: -10),
                ("Демон требует пиццу из редких ингредиентов!", self.game.increase_ingredient_prices),
                ("Бонус: Вы нашли монеты!", lambda: self.game.chef.earn_money(r.randint(10, 30)))
            ]
            event_name, effect = r.choice(events)
            if event_name == "Духи украли ингредиенты!":
                stolen_ingredient = effect()
                self.show_random_event(event_name, 0, stolen_ingredient)
            else:
                time_adjustment = effect()
                self.show_random_event(event_name, time_adjustment)
        else:
            self.start_order_ui()

    def start_order_ui(self):
        self.update_order(self.current_order)
        
        # Устанавливаем время начала заказа
        self.order_start_time = time.time()
        self.update_timer()

        # Показываем фрейм заказа
        self.order_frame.pack(pady=10)
        self.create_ingredient_buttons(ingredients)

        # Запускаем обновление таймера
        self.root.after(100, self.check_timer)

    def update_order(self, order):
        order_text = ", ".join([x[0] for x in order])
        self.order_label.config(text=f"Заказ демона: {order_text}")
        self.order_label.pack()

    def create_ingredient_buttons(self, ingredients_list):
        # Удаляем предыдущие кнопки ингредиентов
        for button in self.ingredients_buttons:
            button.destroy()
        self.ingredients_buttons.clear()

        # Создаем новые кнопки для каждого ингредиента
        for i, ing in enumerate(ingredients_list):
            button = tk.Button(
                self.order_frame,
                text=f"{i} - {ing[0]} (Цена: {ing[1]}, Множитель: {ing[2]:.2f})",
                command=lambda idx=i: self.select_ingredient(idx)
            )
            button.pack(pady=2)
            button.bind("<Enter>", self.on_enter)
            button.bind("<Leave>", self.on_leave)
            self.ingredients_buttons.append(button)

    def select_ingredient(self, index):
        ingredient = ingredients[index]
        self.selected_ingredients.append(ingredient[0])
        print(f"Добавлен ингредиент: {ingredient[0]}")

        # Проверяем соответствие с заказом
        order_ingredients = [x[0] for x in self.current_order]
        if len(self.selected_ingredients) == len(order_ingredients):
            if self.selected_ingredients == order_ingredients:
                # Создаем пиццу для расчета стоимости
                pizza = Pizza()
                for ing in self.current_order:
                    pizza.add_ingredient(ing)
                
                earnings = pizza.calculate_price()
                
                # Скрываем все элементы кроме счетчика времени
                self.stats_label.pack_forget()
                self.order_frame.pack_forget()
                
                # Показываем поздравление
                congrats_text = f"Отлично! Заказ собран правильно!\nВы заработали {earnings} монет!"
                self.congrats_label.config(text=congrats_text)
                self.congrats_label.pack(pady=20)
                
                # Обновляем данные игрока
                self.game.chef.earn_money(earnings)
                if self.game.chef.level_up():
                    self.congrats_label.config(text=f"{congrats_text}\nПоздравляем! Вы достигли уровня {self.game.chef.level}!")
                
                # Через 2 секунды возвращаем интерфейс в исходное состояние
                self.root.after(2000, self.reset_after_success)
            else:
                print(f"Демон разгневан, пицца неправильная!")
                if not self.game.chef.lose_reputation():
                    self.end_game()
                self.reset_order_ui()

    def reset_after_success(self):
        # Скрываем поздравление
        self.congrats_label.pack_forget()
        
        # Показываем основные элементы
        self.stats_label.pack(pady=10)
        self.update_stats()
        
        # Сбрасываем UI заказа и показываем основные кнопки
        self.reset_order_ui()

    def update_timer(self):
        if self.order_start_time is not None:
            elapsed_time = time.time() - self.order_start_time
            time_left = max(0, self.preparation_time - elapsed_time)
            self.timer_label.config(text=f"Оставшееся время: {time_left:.2f} сек.")
            self.timer_label.pack()

    def check_timer(self):
        if self.order_start_time is not None:
            elapsed_time = time.time() - self.order_start_time
            if elapsed_time > self.preparation_time:
                # Скрываем все элементы кроме счетчика времени
                self.stats_label.pack_forget()
                self.order_frame.pack_forget()
                
                # Показываем сообщение о проигрыше
                self.congrats_label.config(text="Время вышло!\nДемон ушел голодным.", fg="red")
                self.congrats_label.pack(pady=20)
                
                if not self.game.chef.lose_reputation():
                    self.root.after(2000, self.end_game)
                else:
                    self.root.after(2000, self.reset_after_success)
            else:
                self.update_timer()
                self.root.after(100, self.check_timer)

    def reset_order_ui(self):
        # Скрываем фрейм заказа
        self.order_frame.pack_forget()

        # Очищаем список выбранных ингредиентов
        self.selected_ingredients = []
        
        # Сбрасываем текущий заказ и время
        self.current_order = None
        self.preparation_time = None
        self.order_start_time = None

        # Показываем начальные кнопки
        self.accept_order_button.pack(pady=10)
        self.upgrade_button.pack(pady=10)
        self.exit_button.pack(pady=10)

    def upgrade_equipment(self):
        # Скрываем начальные кнопки
        self.accept_order_button.pack_forget()
        self.upgrade_button.pack_forget()
        self.exit_button.pack_forget()

        # Рассчитываем текущую стоимость улучшения
        upgrade_cost = UPGRADE_COST + (self.game.chef.equipment["oven"] + self.game.chef.equipment["tools"] + self.game.chef.equipment["fridge"] - 3) * 10

        # Создаем кнопки для улучшения оборудования
        self.upgrade_labels["oven"] = tk.Label(self.upgrade_frame, text=f"Печь увеличивает скорость приготовления пиццы на 10% (Уровень: {self.game.chef.equipment['oven']} | Стоимость: {upgrade_cost} монет)")
        self.upgrade_labels["oven"].pack(pady=5)
        self.upgrade_buttons["oven"] = tk.Button(self.upgrade_frame, text="Улучшить печь", command=lambda: self.upgrade("oven", upgrade_cost))
        self.upgrade_buttons["oven"].pack(pady=5)
        self.upgrade_buttons["oven"].bind("<Enter>", self.on_enter)
        self.upgrade_buttons["oven"].bind("<Leave>", self.on_leave)

        self.upgrade_labels["tools"] = tk.Label(self.upgrade_frame, text=f"Снижает стоимость пиццы на 10% (Уровень: {self.game.chef.equipment['tools']} | Стоимость: {upgrade_cost} монет)")
        self.upgrade_labels["tools"].pack(pady=5)
        self.upgrade_buttons["tools"] = tk.Button(self.upgrade_frame, text="Улучшить инструменты", command=lambda: self.upgrade("tools", upgrade_cost))
        self.upgrade_buttons["tools"].pack(pady=5)
        self.upgrade_buttons["tools"].bind("<Enter>", self.on_enter)
        self.upgrade_buttons["tools"].bind("<Leave>", self.on_leave)

        self.upgrade_labels["fridge"] = tk.Label(self.upgrade_frame, text=f"Холодильник увеличивает количество ингредиентов на 1 (Уровень: {self.game.chef.equipment['fridge']} | Стоимость: {upgrade_cost} монет)")
        self.upgrade_labels["fridge"].pack(pady=5)
        self.upgrade_buttons["fridge"] = tk.Button(self.upgrade_frame, text="Улучшить холодильник", command=lambda: self.upgrade("fridge", upgrade_cost))
        self.upgrade_buttons["fridge"].pack(pady=5)
        self.upgrade_buttons["fridge"].bind("<Enter>", self.on_enter)
        self.upgrade_buttons["fridge"].bind("<Leave>", self.on_leave)

        # Добавляем кнопку возврата в главное меню
        self.back_button = tk.Button(self.upgrade_frame, text="Вернуться в главное меню", command=self.reset_upgrade_ui)
        self.back_button.pack(pady=10)
        self.back_button.bind("<Enter>", self.on_enter)
        self.back_button.bind("<Leave>", self.on_leave)

        # Показываем фрейм улучшений
        self.upgrade_frame.pack(pady=10)

    def upgrade(self, equipment_type, cost):
        if self.game.chef.upgrade_equipment(equipment_type):
            # Скрываем все элементы кроме счетчика времени
            self.upgrade_frame.pack_forget()
            self.stats_label.pack_forget()
            
            # Создаем текст для отображения изменений
            upgrade_text = f"Улучшение {equipment_type.capitalize()} успешно!\n"
            
            if equipment_type == "fridge" and new_ingredients:
                new_ing = new_ingredients.pop(0)
                ingredients.append(new_ing)
                upgrade_text += f"Открыт новый ингредиент: {new_ing[0]}!"
            elif equipment_type == "oven":
                upgrade_text += "Скорость приготовления увеличена на 10%!"
            elif equipment_type == "tools":
                upgrade_text += "Стоимость пиццы снижена на 10%!"
                
            # Показываем сообщение об улучшении
            self.event_label.config(text=upgrade_text, fg="green")
            self.event_label.pack(pady=20)
            
            # Через 2 секунды возвращаем интерфейс в исходное состояние
            self.root.after(2000, self.reset_upgrade_ui)
        else:
            messagebox.showerror("Ошибка", f"Недостаточно денег для улучшения! Текущая стоимость: {cost} монет.")
            self.reset_upgrade_ui()

    def reset_upgrade_ui(self):
        # Скрываем фрейм улучшений и сообщение
        self.upgrade_frame.pack_forget()
        self.event_label.pack_forget()

        # Очищаем фрейм
        for widget in self.upgrade_frame.winfo_children():
            widget.destroy()

        # Показываем основные элементы
        self.stats_label.pack(pady=10)
        self.update_stats()
        
        # Показываем начальные кнопки
        self.accept_order_button.pack(pady=10)
        self.upgrade_button.pack(pady=10)
        self.exit_button.pack(pady=10)

    def end_game(self):
        print("Игра окончена!")
        self.root.quit()

class Game:
    def __init__(self):
        self.chef = Chef()
        self.start_time = None
        self.leaderboard = []
        self.current_pizza = None
        self.player_name = None

    def load_leaderboard(self):
        try:
            with open('leaderboard.json', 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    self.leaderboard = data
                else:
                    print("Ошибка: Формат файла leaderboard.json некорректен.")
                    self.leaderboard = []
        except FileNotFoundError:
            self.leaderboard = []

    def save_leaderboard(self):
        with open('leaderboard.json', 'w') as f:
            json.dump(self.leaderboard, f)

    def display_leaderboard(self):
        self.load_leaderboard()
        print("\nТаблица лидеров:")
        self.leaderboard.sort(key=lambda x: x[1])
        for rank, (name, time_taken) in enumerate(self.leaderboard, start=1):
            print(f"{rank}. {name} - {time_taken:.2f} секунд")

    def random_event(self):
        events = [
            ("Духи украли ингредиенты!", self.steal_ingredient),
            ("Печь перегрелась!", lambda: -10),
            ("Демон требует пиццу из редких ингредиентов!", self.increase_ingredient_prices),
            ("Бонус: Вы нашли монеты!", lambda: self.chef.earn_money(r.randint(10, 30)))
        ]
        event_name, effect = r.choice(events)
        print(f"\nСЛУЧАЙНОЕ СОБЫТИЕ: {event_name}\n")
        return effect()

    def steal_ingredient(self):
        if ingredients and len(ingredients) > 1:
            stolen_index = r.randint(0, len(ingredients) - 1)
            stolen_ingredient = ingredients.pop(stolen_index)
            new_ingredients.append(stolen_ingredient)
            print(f"Духи украли ингредиент: {stolen_ingredient[0]}!")
            return stolen_ingredient
        else:
            print("Все доступные ингредиенты уже украдены!")
            return None

    def increase_ingredient_prices(self):
        price_increase_factor = 1.1  # Коэффициент увеличения цены на 10%
        for ing in ingredients:
            ing[1] *= price_increase_factor

    def play(self, root):
        StartScreen(root, self)

if __name__ == "__main__":
    root = tk.Tk()
    game = Game()
    game.play(root)
    root.mainloop()