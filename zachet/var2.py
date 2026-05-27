import random


def choose_difficulty():
    print("\nВыберите уровень сложности:")
    print("  1 - Лёгкий   (число от 1 до 10,  5 попыток)")
    print("  2 - Средний  (число от 1 до 50,  7 попыток)")
    print("  3 - Сложный  (число от 1 до 100, 10 попыток)")
    while True:
        choice = input("Ваш выбор (1/2/3, exit - выйти): ").strip().lower()
        if choice == "exit":
            return None
        if choice == "1":
            return 10, 5
        if choice == "2":
            return 50, 7
        if choice == "3":
            return 100, 10
        print("Ошибка: нужно ввести 1, 2, 3 или exit.")


def play_game(max_number, attempts):
    secret = random.randint(1, max_number)
    print(f"\nЯ загадал число от 1 до {max_number}. У вас {attempts} попыток.")
    used = 0
    while used < attempts:
        left = attempts - used
        prompt = f"Попытка {used + 1}/{attempts} (осталось {left}). Введите число (restart/exit): "
        guess_str = input(prompt).strip().lower()

        if guess_str == "exit":
            return "exit"
        if guess_str == "restart":
            return "restart"

        try:
            guess = int(guess_str)
        except ValueError:
            print("Ошибка: нужно ввести целое число.")
            continue

        if guess < 1 or guess > max_number:
            print(f"Ошибка: число должно быть от 1 до {max_number}.")
            continue

        used += 1
        if guess == secret:
            print(f"Поздравляю! Вы угадали число {secret} за {used} попыток.")
            return "win"
        if guess < secret:
            print("Загаданное число больше.")
        else:
            print("Загаданное число меньше.")

    print(f"Попытки закончились. Загаданное число было: {secret}.")
    return "lose"


def ask_play_again():
    while True:
        answer = input("\nСыграть ещё? (restart - да, exit - нет): ").strip().lower()
        if answer == "restart":
            return True
        if answer == "exit":
            return False
        print("Ошибка: введите restart или exit.")


def main():
    print("=== Игра 'Угадай число' ===")
    wins = 0
    loses = 0

    while True:
        difficulty = choose_difficulty()
        if difficulty is None:
            break
        max_number, attempts = difficulty

        result = play_game(max_number, attempts)

        if result == "win":
            wins += 1
        elif result == "lose":
            loses += 1
        elif result == "exit":
            break
        elif result == "restart":
            print("Начинаем заново...")
            continue

        if not ask_play_again():
            break

    print(f"\nИтоги: побед — {wins}, поражений — {loses}. До свидания!")


if __name__ == "__main__":
    main()
