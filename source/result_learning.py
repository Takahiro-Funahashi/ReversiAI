import json
import linecache
import numpy as np
import os

import reversi_game as game


class LearningResult():
    def __init__(self):
        current = os.getcwd()
        file_path = current + "/source/data/game_result.txt"
        if os.path.exists(file_path):
            self.file_path = file_path
        else:
            self.file_path = None

    def run(self):
        if self.file_path:
            self.create_reversi_game()

            game_record = self.read_game_record()
            self.assemble_game_array(game_record)

        return

    def create_reversi_game(self):
        self.game = game.BoardSurface()
        self.game.init_pieces()

    def read_game_record(self):
        game_record = list()

        line = linecache.getline(self.file_path, 1)
        data = json.loads(line)
        if isinstance(data, dict):
            if 'process' in data:
                game_record = data['process']
                game_record = [game_record[i: i+3]
                               for i in range(0, len(game_record), 3)]
        return game_record

    def assemble_game_array(self, game_record):

        def _create_borad_():
            board = self.game.pieces_on_board.copy()
            black_board = np.where(board == game.WHITE_PIECE, np.nan, board)
            black_board = np.where(
                black_board == game.BLACK_PIECE, 1, black_board)
            black_board = np.where(np.isnan(black_board), 0, black_board)
            white_board = np.where(board == game.BLACK_PIECE, np.nan, board)
            white_board = np.where(
                white_board == game.WHITE_PIECE, 1, white_board)
            white_board = np.where(np.isnan(white_board), 0, white_board)

            return board, black_board, white_board

        self.record_pieces_on_board = np.full(
            [1, 3, ] + list(self.game.board_squares), np.nan)
        self.record_pieces_on_board[0][0] = self.game.pieces_on_board.copy()

        board, black_board, white_board = _create_borad_()
        self.record_pieces_on_board[0][1] = black_board
        self.record_pieces_on_board[0][2] = white_board

        for turn in game_record:
            if turn[0] == 'b':
                self.game.player_turn = game.BLACK_PIECE
            elif turn[0] == 'w':
                self.game.player_turn = game.WHITE_PIECE
            x_index, y_index = ord(turn[1])-0x41, ord(turn[2])-0x31

            self.game.player_procedure(mpos_index=(x_index, y_index))

            board, black_board, white_board = _create_borad_()

            self.record_pieces_on_board = \
                np.append(self.record_pieces_on_board,
                          [[board, black_board, white_board]], axis=0)

        return


if __name__ == '__main__':
    LearningResult().run()