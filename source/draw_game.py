"""
FileName:
--------------------------------------------------------------------------------
    draw_game.py

Description:
--------------------------------------------------------------------------------
    リバーシのゲーム描画

History:
--------------------------------------------------------------------------------
    2022/01/06 作成

"""

import numpy as np
import pygame

BLACK_PIECE = 0
WHITE_PIECE = 1

BLACK_WIN = 0
WHITE_WIN = 1
DRAW = 2
PASS = -1


class ReversiException(Exception):
    NOT_EMPTY = 'NOT EMPTY SQUARE'


class BoardSurface():
    def __init__(self):
        """ 初期化
        """

        # ボードサイズ
        self.board_size = (400, 400)
        # 縦横のオフセット幅
        self.screnn_offset = (40, 80)
        # スクリーンサイズをボードサイズとオフセットから計算
        ans = np.array(self.board_size) + (np.array(self.screnn_offset)*2)
        self.screen_size = ans.tolist()
        # マス目
        self.board_squares = (8, 8)
        # マスサイズを算出
        ans = np.array(self.board_size) / np.array(self.board_squares)
        self.square_size = ans.tolist()

        # フォントサイズ
        self.font_size = 24

        return

    def init_pygeme(self):
        """ PyGame(GUI)初期化
        """

        pygame.init()
        self.game_screen = pygame.display.set_mode(
            size=self.screen_size,
            # flags=pygame.FULLSCREEN,
        )
        pygame.display.set_caption('ReversiAI')

        self.game_font = pygame.font.Font(
            None, self.font_size)

        return

    def draw_background(self):
        """ 背景描画
        """

        self.game_screen.fill('darkgreen')

    def draw_board_frame(self):
        """ 盤面枠の描画
        """
        X, Y = 0, 1
        screen = self.game_screen
        offset_x, offset_y = self.screnn_offset
        board_w, board_h = self.board_size

        line_width = 2

        # 盤面背景
        pygame.draw.rect(
            surface=screen,
            color='forestgreen',
            rect=pygame.Rect(
                offset_x, offset_y,
                board_w, board_h,
            ),
            border_radius=0,
        )

        # 盤面外枠
        pygame.draw.lines(
            surface=screen,
            color='black',
            closed=True,
            points=[
                (offset_x, offset_y),
                (board_w+offset_x-1, offset_y),
                (board_w+offset_x-1, board_h+offset_y-1),
                (offset_x, board_h+offset_y-1),
            ],
            width=line_width,
        )

        # 盤面縦線
        H_sq_size, V_sq_size = self.square_size
        for x_index in range(1, self.board_squares[X]):
            pygame.draw.line(
                surface=screen,
                color='black',
                start_pos=(offset_x+H_sq_size*x_index-1, offset_y),
                end_pos=(offset_x+H_sq_size*x_index-1, board_h+offset_y-1),
                width=line_width
            )

        # 盤面横線
        for y_index in range(1, self.board_squares[Y]):
            pygame.draw.line(
                surface=screen,
                color='black',
                start_pos=(offset_x, offset_y+V_sq_size*y_index-1),
                end_pos=(board_w+offset_x-1, offset_y+V_sq_size*y_index-1),
                width=line_width
            )

        # マス目インデックス表示
        hex_A = 0x41
        for x_index in range(self.board_squares[X]):
            text = self.game_font.render(
                chr(hex_A+x_index),
                False,
                'white',
            )

            screen.blit(
                text,
                [
                    offset_x+H_sq_size*x_index+H_sq_size/2-self.font_size/4,
                    offset_y-self.font_size
                ]
            )

            screen.blit(
                text,
                [
                    offset_x+H_sq_size*x_index+H_sq_size/2-self.font_size/4,
                    offset_y+board_h+self.font_size/2
                ]
            )

        hex_1 = 0x31
        for y_index in range(self.board_squares[Y]):
            text = self.game_font.render(
                chr(hex_1+y_index),
                False,
                'white',
            )

            screen.blit(
                text,
                [
                    offset_x-self.font_size,
                    offset_y+V_sq_size*y_index+V_sq_size/2-self.font_size/4
                ]
            )

            screen.blit(
                text,
                [
                    offset_x+board_w+self.font_size/2,
                    offset_y+V_sq_size*y_index+V_sq_size/2-self.font_size/4
                ]
            )

        return

    def draw_pieces(self, pieces_on_board):
        """ 駒配置描画
        """

        X, Y = 0, 1
        screen = self.game_screen
        offset_x, offset_y = self.screnn_offset

        p_offset = 2

        # 黒白コマのマス目を抽出
        black_pieces = np.where(pieces_on_board == BLACK_PIECE)
        white_pieces = np.where(pieces_on_board == WHITE_PIECE)

        if black_pieces:
            raw, clm = black_pieces
            for x_index, y_index in zip(raw, clm):
                cx = offset_x + self.square_size[X] * \
                    x_index + self.square_size[X]/2
                cy = offset_y + self.square_size[Y] * \
                    y_index + self.square_size[Y]/2
                pygame.draw.circle(
                    surface=screen,
                    color='black',
                    center=(cx, cy),
                    radius=self.square_size[X]/2-p_offset*2,
                )

        if white_pieces:
            raw, clm = white_pieces
            for x_index, y_index in zip(raw, clm):
                cx = offset_x + self.square_size[X] * \
                    x_index + self.square_size[X]/2
                cy = offset_y + self.square_size[Y] * \
                    y_index + self.square_size[Y]/2
                pygame.draw.circle(
                    surface=screen,
                    color='white',
                    center=(cx, cy),
                    radius=self.square_size[X]/2-p_offset*2,
                )

        return

    def draw_player(self, player_turn):
        """ プレイヤーターン描画
        """

        X, Y = 0, 1
        t_offset_x, t_offset_y = 10, 20
        screen = self.game_screen

        text_msg = 'Player'
        text = self.game_font.render(
            text_msg,
            False,
            'white',
        )
        screen.blit(
            text,
            [t_offset_x, t_offset_y]
        )
        size = self.game_font.size(text_msg)

        if player_turn == BLACK_PIECE:
            color = 'black'
        elif player_turn == WHITE_PIECE:
            color = 'white'

        circle_size = self.font_size/2

        pygame.draw.circle(
            surface=screen,
            color=color,
            center=(t_offset_x*4+size[X], t_offset_y+size[Y]/2),
            radius=circle_size,
        )

        return

    def draw_counter(self, pieces_on_board):
        """ 黒白コマ数描画

        """
        Y = 1
        t_offset_x = 10
        screen = self.game_screen
        circle_size = self.font_size/2

        cx = t_offset_x+circle_size
        cy = self.screen_size[Y] - self.font_size

        pygame.draw.circle(
            surface=screen,
            color='black',
            center=(cx, cy),
            radius=circle_size,
        )

        pygame.draw.circle(
            surface=screen,
            color='white',
            center=(cx+circle_size*5, cy),
            radius=circle_size,
        )

        pieces_counter = self.count_pieces(pieces_on_board)
        text_msg = str(pieces_counter[BLACK_PIECE])
        text = self.game_font.render(
            text_msg,
            False,
            'white',
            'darkgreen'
        )
        screen.blit(
            text,
            [cx+circle_size*2, cy-5]
        )
        text_msg = str(pieces_counter[WHITE_PIECE])
        text = self.game_font.render(
            text_msg,
            False,
            'white',
            'darkgreen'
        )
        screen.blit(
            text,
            [cx+circle_size*7, cy-5]
        )

        return

    def draw_game_over(self, judge: int):
        """ ゲーム終了表示

        Args:
            judge (int): 勝敗結果
        """

        X, Y = 0, 1
        dialog_size = (150, 40)
        screen = self.game_screen

        screen_w, screen_h = self.screen_size

        pygame.draw.rect(
            surface=screen,
            color='gray',
            rect=pygame.Rect(
                screen_w/2-dialog_size[X]/2, screen_h/2-dialog_size[Y]/2,
                dialog_size[X], dialog_size[Y],
            ),
            border_radius=0,
        )

        if 'judge' in judge:
            judge = judge['judge']

            if judge == BLACK_WIN:
                text_msg = 'Black Wins!!'
            if judge == WHITE_WIN:
                text_msg = 'White Wins!!'
            if judge == DRAW:
                text_msg = 'Draw!!'

            text = self.game_font.render(
                text_msg,
                False,
                'red',
            )

            screen.blit(
                text,
                [
                    screen_w/2-dialog_size[X]/2+20,
                    screen_h/2-dialog_size[Y]/2+14
                ]
            )

    def count_pieces(self, pieces_on_board):
        """ 黒白コマ数カウント

        Returns:
            (dict): BLACK_PIECE,WHITE_PIECEをKeyとして、個数をDict型で返信
        """

        black_count = np.count_nonzero(pieces_on_board == BLACK_PIECE)
        white_count = np.count_nonzero(pieces_on_board == WHITE_PIECE)

        return {BLACK_PIECE: black_count, WHITE_PIECE: white_count}
