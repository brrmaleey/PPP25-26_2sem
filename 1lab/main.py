import copy 
import os # Добавили библиотеку для работы с системой

# Эта строчка "будит" терминал в Windows, чтобы он начал понимать цвета (ANSI-коды)
os.system('') 

# === БАЗОВЫЕ КЛАССЫ И ООП ===

class Piece: 
    def __init__(self, color, symbol): 
        self.color = color 
        self.symbol = symbol 

    def get_moves(self, x, y, board): 
        return [] 

    def slide_moves(self, x, y, board, directions): 
        moves = []
        for dx, dy in directions: 
            nx, ny = x + dx, y + dy 
            while 0 <= nx <= 7 and 0 <= ny <= 7: 
                target = board.grid.get((nx, ny)) 
                if target is None: 
                    moves.append((nx, ny)) 
                elif target.color != self.color: 
                    moves.append((nx, ny)) 
                    break 
                else: 
                    break 
                nx += dx 
                ny += dy 
        return moves 

# === КЛАССЫ СТАНДАРТНЫХ ФИГУР ===
# Теперь мы выдаем им настоящие шахматные символы!

class Pawn(Piece): 
    def __init__(self, color): 
        super().__init__(color, '♙' if color == 'white' else '♟') 

    def get_moves(self, x, y, board): 
        moves = []
        direction = -1 if self.color == 'white' else 1 
        
        if board.grid.get((x, y + direction)) is None: 
            moves.append((x, y + direction)) 
            start_row = 6 if self.color == 'white' else 1 
            if y == start_row and board.grid.get((x, y + 2 * direction)) is None: 
                moves.append((x, y + 2 * direction)) 

        for dx in [-1, 1]: 
            target = board.grid.get((x + dx, y + direction)) 
            if target and target.color != self.color: 
                moves.append((x + dx, y + direction)) 
                
            if board.last_move: 
                last_start, last_end, last_piece = board.last_move 
                if isinstance(last_piece, Pawn) and last_end == (x + dx, y) and abs(last_start[1] - last_end[1]) == 2: 
                    moves.append((x + dx, y + direction)) 
        return moves 

class Rook(Piece): 
    def __init__(self, color): 
        super().__init__(color, '♖' if color == 'white' else '♜') 
    def get_moves(self, x, y, board): 
        return self.slide_moves(x, y, board, [(0,1), (0,-1), (1,0), (-1,0)]) 

class Bishop(Piece): 
    def __init__(self, color): 
        super().__init__(color, '♗' if color == 'white' else '♝') 
    def get_moves(self, x, y, board): 
        return self.slide_moves(x, y, board, [(1,1), (1,-1), (-1,1), (-1,-1)]) 

class Queen(Piece): 
    def __init__(self, color): 
        super().__init__(color, '♕' if color == 'white' else '♛') 
    def get_moves(self, x, y, board): 
        return self.slide_moves(x, y, board, [(0,1), (0,-1), (1,0), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)])

class Knight(Piece): 
    def __init__(self, color): 
        super().__init__(color, '♘' if color == 'white' else '♞') 
    def get_moves(self, x, y, board): 
        moves = []
        jumps = [(2,1), (1,2), (-1,2), (-2,1), (-2,-1), (-1,-2), (1,-2), (2,-1)] 
        for dx, dy in jumps: 
            nx, ny = x + dx, y + dy 
            if 0 <= nx <= 7 and 0 <= ny <= 7: 
                target = board.grid.get((nx, ny)) 
                if target is None or target.color != self.color: 
                    moves.append((nx, ny)) 
        return moves 

class King(Piece): 
    def __init__(self, color): 
        super().__init__(color, '♔' if color == 'white' else '♚') 
    def get_moves(self, x, y, board): 
        moves = []
        for dx in [-1, 0, 1]: 
            for dy in [-1, 0, 1]: 
                if dx == 0 and dy == 0: continue 
                nx, ny = x + dx, y + dy 
                if 0 <= nx <= 7 and 0 <= ny <= 7: 
                    target = board.grid.get((nx, ny)) 
                    if target is None or target.color != self.color: 
                        moves.append((nx, ny)) 
        return moves 

# === ДОП. ЗАДАНИЕ 1: ТРИ НОВЫЕ ФИГУРЫ ===
# Для них нет официальных иконок, поэтому оставляем стильные буквы

class Archbishop(Piece): 
    def __init__(self, color): 
        super().__init__(color, 'A' if color == 'white' else 'a') 
    def get_moves(self, x, y, board): 
        moves = Bishop(self.color).get_moves(x, y, board) 
        moves += Knight(self.color).get_moves(x, y, board) 
        return moves 

class Chancellor(Piece): 
    def __init__(self, color): 
        super().__init__(color, 'C' if color == 'white' else 'c') 
    def get_moves(self, x, y, board): 
        moves = Rook(self.color).get_moves(x, y, board) 
        moves += Knight(self.color).get_moves(x, y, board) 
        return moves 

class Jester(Piece): 
    def __init__(self, color): 
        super().__init__(color, 'J' if color == 'white' else 'j') 
    def get_moves(self, x, y, board): 
        moves = []
        jumps = [(0,2), (0,-2), (2,0), (-2,0), (2,2), (2,-2), (-2,2), (-2,-2)] 
        for dx, dy in jumps: 
            nx, ny = x + dx, y + dy 
            if 0 <= nx <= 7 and 0 <= ny <= 7: 
                target = board.grid.get((nx, ny)) 
                if target is None or target.color != self.color: 
                    moves.append((nx, ny)) 
        return moves 

# === КЛАСС ДОСКИ И ИГРЫ ===

class Board: 
    def __init__(self): 
        self.grid = {} 
        self.history = [] 
        self.last_move = None 
        self.setup() 

    def setup(self): 
        for x in range(8): 
            self.grid[(x, 1)] = Pawn('black') 
            self.grid[(x, 6)] = Pawn('white') 

        self.grid[(1, 6)], self.grid[(2, 6)], self.grid[(5, 6)] = Archbishop('white'), Chancellor('white'), Jester('white')
        self.grid[(1, 1)], self.grid[(2, 1)], self.grid[(5, 1)] = Archbishop('black'), Chancellor('black'), Jester('black')

        placement = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook] 
        for x, piece_class in enumerate(placement): 
            self.grid[(x, 0)] = piece_class('black') 
            self.grid[(x, 7)] = piece_class('white') 

    def display(self): 
        print("\n    a  b  c  d  e  f  g  h") # Отступ для верхних букв
        for y in range(8): 
            row_str = f" {8 - y} " # Номер строки слева
            for x in range(8): 
                piece = self.grid.get((x, y)) 
                
                # Чередуем цвета клеток (математическая магия: сумма четная = светлая клетка)
                if (x + y) % 2 == 0:
                    bg_color = "\033[47m" # Светло-серый фон (ANSI-код)
                else:
                    bg_color = "\033[100m" # Темно-серый фон (ANSI-код)
                
                if piece: 
                    # Делаем белые фигуры ярко-белыми, а черные - черными
                    text_color = "\033[97m" if piece.color == 'white' else "\033[30m"
                    # Склеиваем: Фон + Цвет текста + Пробел + Фигура + Пробел + Сброс цветов
                    row_str += f"{bg_color}{text_color} {piece.symbol} \033[0m"
                else: 
                    # Пустая клетка (просто три пробела с цветным фоном)
                    row_str += f"{bg_color}   \033[0m"
                    
            print(row_str + f" {8 - y}") # Выводим готовую строку с номером справа
        print("    a  b  c  d  e  f  g  h\n") # Буквы снизу

    def move_piece(self, start, end): 
        piece = self.grid.get(start) 
        if not piece: return False 
        
        valid_moves = piece.get_moves(start[0], start[1], self) 
        if end not in valid_moves: return False 

        backup_grid = copy.deepcopy(self.grid)
        backup_last_move = copy.deepcopy(self.last_move)

        if isinstance(piece, Pawn) and end not in self.grid and start[0] != end[0]: 
            del self.grid[(end[0], start[1])] 

        self.grid[end] = piece 
        del self.grid[start] 
        
        if isinstance(piece, Pawn) and (end[1] == 0 or end[1] == 7): 
            self.grid[end] = Queen(piece.color) 

        my_king_pos = None
        for pos, p in self.grid.items(): 
            if isinstance(p, King) and p.color == piece.color:
                my_king_pos = pos
                break
                
        if my_king_pos: 
            for pos, enemy in self.grid.items():
                if enemy.color != piece.color:
                    if my_king_pos in enemy.get_moves(pos[0], pos[1], self):
                        self.grid = backup_grid 
                        self.last_move = backup_last_move
                        return "check" 

        self.history.append({
            'grid': backup_grid,
            'last_move': backup_last_move
        })
        self.last_move = (start, end, piece) 

        return True 

    def undo(self): 
        if self.history: 
            state = self.history.pop() 
            self.grid = state['grid'] 
            self.last_move = state['last_move'] 
            print("Ход отменен!") 
            return True 
        else: 
            print("Нечего отменять.") 
            return False 

class Game: 
    def __init__(self): 
        self.board = Board() 
        self.current_turn = 'white' 

    def parse_pos(self, pos_str): 
        if len(pos_str) != 2: return None 
        x = ord(pos_str[0]) - ord('a') 
        y = 8 - int(pos_str[1]) 
        if 0 <= x <= 7 and 0 <= y <= 7: 
            return (x, y) 
        return None 

    def show_hints(self, pos_str): 
        pos = self.parse_pos(pos_str) 
        if not pos: return print("Неверная клетка!") 
        piece = self.board.grid.get(pos) 
        if not piece: return print("Клетка пуста.") 
        moves = piece.get_moves(pos[0], pos[1], self.board) 
        move_strs = [f"{chr(x + ord('a'))}{8 - y}" for x, y in moves] 
        print(f"Фигура {piece.symbol} может пойти (без учета защиты короля) на: {', '.join(move_strs) if move_strs else 'Никуда'}") 

    def show_threats(self): 
        threatened = [] 
        is_check = False 
        
        for (ex, ey), enemy in self.board.grid.items(): 
            if enemy.color != self.current_turn: 
                moves = enemy.get_moves(ex, ey, self.board) 
                for mx, my in moves: 
                    target = self.board.grid.get((mx, my)) 
                    if target and target.color == self.current_turn: 
                        if isinstance(target, King): 
                            is_check = True
                        else:
                            threatened.append(f"{target.symbol} на {chr(mx + ord('a'))}{8 - my}") 
                            
        if is_check:
            print("\n⚠️ ВАМ ШАХ! ⚠️\n") 
            
        print("Ваши фигуры под ударом: " + (", ".join(set(threatened)) if threatened else "Угроз нет.")) 

    def play(self): 
        print("Добро пожаловать в красивые ООП-Шахматы!") 
        print("Новые фигуры: A(Архиепископ), C(Канцлер), J(Шут)") 
        while True: 
            self.board.display() 
            print(f"Ход: {'Белых' if self.current_turn == 'white' else 'Черных'}") 
            print("Команды: 'e2 e4' или 'e2-e4', 'undo', 'hint e2', 'threats', 'quit'") 
            
            raw_input = input("> ").strip().lower()
            cmd = raw_input.replace('-', ' ').split() 

            if not cmd: continue 
            if cmd[0] == 'quit': break 
            elif cmd[0] == 'undo': 
                if self.board.undo(): 
                    self.current_turn = 'black' if self.current_turn == 'white' else 'white' 
            elif cmd[0] == 'hint' and len(cmd) == 2: 
                self.show_hints(cmd[1]) 
            elif cmd[0] == 'threats': 
                self.show_threats() 
            elif len(cmd) == 2: 
                start, end = self.parse_pos(cmd[0]), self.parse_pos(cmd[1]) 
                if not start or not end: 
                    print("Неверные координаты.") 
                    continue 
                
                piece = self.board.grid.get(start) 
                if not piece or piece.color != self.current_turn: 
                    print("Это не ваша фигура или клетка пуста!") 
                    continue 
                
                result = self.board.move_piece(start, end)
                if result == "check":
                    print("Недопустимый ход: ваш король останется под шахом!")
                elif result: 
                    self.current_turn = 'black' if self.current_turn == 'white' else 'white' 
                else: 
                    print("Недопустимый ход по правилам фигуры.") 
            else: 
                print("Неизвестная команда.") 

if __name__ == "__main__": 
    Game().play()
