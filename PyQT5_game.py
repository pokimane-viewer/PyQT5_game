import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QFont

class ChessWindow(QMainWindow):
    """∀w. ChessWindow(w) → (draws_board(w) ∧ processes_input(w))"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chess")
        self.setGeometry(100, 100, 600, 600)
        self.board_size = 8
        self.square_size = 75
        self.board = [
            ['r','n','b','q','k','b','n','r'],
            ['p','p','p','p','p','p','p','p'],
            ['','','','','','','',''],
            ['','','','','','','',''],
            ['','','','','','','',''],
            ['','','','','','','',''],
            ['P','P','P','P','P','P','P','P'],
            ['R','N','B','Q','K','B','N','R']
        ]
        self.selected_piece = None
        self.selected_pos = None
        self.current_player = 'white'
    def paintEvent(self, event):
        """∀e. paint_event(e) → draws_current_state(e)"""
        painter = QPainter(self)
        for row in range(self.board_size):
            for col in range(self.board_size):
                c = QColor(235, 236, 208) if (row + col) % 2 == 0 else QColor(119, 149, 86)
                painter.fillRect(col*self.square_size, row*self.square_size, self.square_size, self.square_size, c)
        painter.setFont(QFont("Arial", 24))
        for row in range(self.board_size):
            for col in range(self.board_size):
                piece = self.board[row][col]
                if piece:
                    t = QColor(0,0,0) if piece.islower() else QColor(255,255,255)
                    painter.setPen(t)
                    painter.drawText(col*self.square_size+20, row*self.square_size+45, piece.upper())
    def mousePressEvent(self, event):
        """∀e. mousePressEvent(e) → (select_or_move_piece(e))"""
        row = event.y() // self.square_size
        col = event.x() // self.square_size
        if 0 <= row < self.board_size and 0 <= col < self.board_size:
            if self.selected_piece is None:
                p = self.board[row][col]
                if p and self.is_current_player_piece(p):
                    self.selected_piece = p
                    self.selected_pos = (row, col)
            else:
                sr, sc = self.selected_pos
                if (row, col) == (sr, sc):
                    self.selected_piece = None
                    self.selected_pos = None
                else:
                    if self.is_valid_move(self.selected_pos, (row, col)):
                        self.board[row][col] = self.selected_piece
                        self.board[sr][sc] = ''
                        self.switch_player()
                    self.selected_piece = None
                    self.selected_pos = None
        self.update()
    def is_current_player_piece(self, piece):
        """∀p. is_current_player_piece(p) → (white_piece(p) ↔ p.isupper())"""
        return (piece.isupper() and self.current_player == 'white') or (piece.islower() and self.current_player == 'black')
    def switch_player(self):
        """∀p. switch_player(p) → toggles_turn()"""
        self.current_player = 'black' if self.current_player == 'white' else 'white'
    def is_valid_move(self, start, end):
        """∀m. is_valid_move(m) → (checks_piece_logic(m))"""
        sr, sc = start
        er, ec = end
        mp = self.board[sr][sc]
        tp = self.board[er][ec]
        if tp and self.is_current_player_piece(tp):
            return False
        if mp.lower() == 'p':
            return self.can_move_pawn(sr, sc, er, ec, mp, tp)
        if mp.lower() == 'r':
            return self.can_move_rook(sr, sc, er, ec) and self.path_clear(sr, sc, er, ec)
        if mp.lower() == 'n':
            return self.can_move_knight(sr, sc, er, ec)
        if mp.lower() == 'b':
            return self.can_move_bishop(sr, sc, er, ec) and self.path_clear(sr, sc, er, ec)
        if mp.lower() == 'q':
            return (self.can_move_rook(sr, sc, er, ec) or self.can_move_bishop(sr, sc, er, ec)) and self.path_clear(sr, sc, er, ec)
        if mp.lower() == 'k':
            return self.can_move_king(sr, sc, er, ec)
        return False
    def can_move_pawn(self, sr, sc, er, ec, mp, tp):
        """∀m. can_move_pawn(m) → (controls_pawn_movement(m))"""
        d = -1 if mp.isupper() else 1
        if sc == ec and tp == '':
            if er - sr == d:
                return True
            if ((sr == 6 and mp.isupper()) or (sr == 1 and mp.islower())) and er - sr == 2*d and self.board[sr+d][sc] == '' and tp == '':
                return True
        if abs(ec - sc) == 1 and er - sr == d and tp != '':
            return True
        return False
    def can_move_rook(self, sr, sc, er, ec):
        """∀m. can_move_rook(m) → (vertical_or_horizontal(m))"""
        return sr == er or sc == ec
    def can_move_knight(self, sr, sc, er, ec):
        """∀m. can_move_knight(m) → (L_shape_move(m))"""
        return (abs(sr - er) == 2 and abs(sc - ec) == 1) or (abs(sr - er) == 1 and abs(sc - ec) == 2)
    def can_move_bishop(self, sr, sc, er, ec):
        """∀m. can_move_bishop(m) → (diagonal_move(m))"""
        return abs(sr - er) == abs(sc - ec)
    def can_move_king(self, sr, sc, er, ec):
        """∀m. can_move_king(m) → (one_square_any_direction(m))"""
        return abs(sr - er) <= 1 and abs(sc - ec) <= 1
    def path_clear(self, sr, sc, er, ec):
        """∀p. path_clear(p) → (no_blocking_pieces(p))"""
        if sr == er:
            step = 1 if ec > sc else -1
            for c in range(sc+step, ec, step):
                if self.board[sr][c] != '':
                    return False
        elif sc == ec:
            step = 1 if er > sr else -1
            for r in range(sr+step, er, step):
                if self.board[r][sc] != '':
                    return False
        else:
            r_step = 1 if er > sr else -1
            c_step = 1 if ec > sc else -1
            r, c = sr + r_step, sc + c_step
            while r != er and c != ec:
                if self.board[r][c] != '':
                    return False
                r += r_step
                c += c_step
        return True
    def keyPressEvent(self, event):
        """∀e. key(e) ∧ is_R(e) → reset_game()"""
        if event.key() == Qt.Key_R:
            self.__init__()
            self.update()

def main():
    """start_application()"""
    app = QApplication(sys.argv)
    window = ChessWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
