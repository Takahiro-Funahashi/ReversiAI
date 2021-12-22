"""
FileName:
--------------------------------------------------------------------------------
    reversi_game.py

Description:
--------------------------------------------------------------------------------
    リバーシのゲーム動作

History:
--------------------------------------------------------------------------------
    2021/12/21 作成

"""

import json
import numpy as np
import os
import pygame
import random
import time

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

        self.init_game_record()

        return

    def init_game_record(self):
        self.game_record = {
            'result': {
                'black': None, 'wihte': None,
            },
            'process': '',
        }

    def run(self, isMsample: bool = False, isAutoBlack: bool = False, isAutoWhite: bool = False):
        """ ゲーム実行開始
        """

        self.init_game_record()

        self.init_pieces()

        if not isMsample:
            # Pygeme(GUI)初期化
            self.init_pygeme()
            # 背景描画
            self.draw_background()
        else:
            isAutoBlack = True
            isAutoWhite = True

        while(True):
            if not isMsample:
                # 盤面枠描画
                self.draw_board_frame()
                # 駒描画
                self.draw_pieces()
                # プレイヤーターン描画
                self.draw_player()
                # 黒白コマ数描画
                self.draw_counter()
                # GUI描画更新
                pygame.display.update()

            # ゲームの判定
            judge = self.judge_trun()
            if judge is not True:
                if judge != PASS:
                    self.record_game_result()
                    if not isMsample:
                        self.draw_game_over(judge)
                        pygame.display.update()
                        time.sleep(1)
                        pygame.quit()
                        break
                    else:
                        break

            # 自動配置処理
            if self.player_turn == WHITE_PIECE and isAutoWhite:
                self.auto_player(isMsample)
                if not isMsample:
                    time.sleep(0.1)
            elif self.player_turn == BLACK_PIECE and isAutoBlack:
                self.auto_player(isMsample)
                if not isMsample:
                    time.sleep(0.1)

            # GUIイベント処理
            if not isMsample:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        break
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == pygame.BUTTON_LEFT:
                            x, y = event.pos
                            self.mouse_left_clicked(event.pos)

        return self.game_record

    def init_pieces(self):
        """ 盤面配列の初期化
        """

        # 盤面配列
        self.pieces_on_board = np.full(self.board_squares, np.nan)

        # 初期コマ配置
        self.pieces_on_board[3, 3] = BLACK_PIECE
        self.pieces_on_board[4, 4] = BLACK_PIECE
        self.pieces_on_board[3, 4] = WHITE_PIECE
        self.pieces_on_board[4, 3] = WHITE_PIECE

        # 手番変数（黒が先手）
        self.player_turn = BLACK_PIECE

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

    def draw_pieces(self):
        """ 駒配置描画
        """

        X, Y = 0, 1
        screen = self.game_screen
        offset_x, offset_y = self.screnn_offset

        p_offset = 2

        # 黒白コマのマス目を抽出
        black_pieces = np.where(self.pieces_on_board == BLACK_PIECE)
        white_pieces = np.where(self.pieces_on_board == WHITE_PIECE)

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

    def draw_player(self):
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

        if self.player_turn == BLACK_PIECE:
            color = 'black'
        elif self.player_turn == WHITE_PIECE:
            color = 'white'

        circle_size = self.font_size/2

        pygame.draw.circle(
            surface=screen,
            color=color,
            center=(t_offset_x*4+size[X], t_offset_y+size[Y]/2),
            radius=circle_size,
        )

        return

    def draw_counter(self):
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

        pieces_counter = self.count_pieces()
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

    def count_pieces(self):
        """ 黒白コマ数カウント

        Returns:
            (dict): BLACK_PIECE,WHITE_PIECEをKeyとして、個数をDict型で返信
        """

        black_count = np.count_nonzero(self.pieces_on_board == BLACK_PIECE)
        white_count = np.count_nonzero(self.pieces_on_board == WHITE_PIECE)

        return {BLACK_PIECE: black_count, WHITE_PIECE: white_count}

    def mouse_left_clicked(self, pos: list):
        """ マウス左クリックイベント

        Args:
            pos (list): マウスクリック座標(x,y)
        """

        # offset補正
        board_pos = np.array(pos)-np.array(self.screnn_offset)
        # インデックス値に変換
        ans = board_pos/np.array(self.square_size)
        ans = ans.astype('uint8')
        mpos_index = ans.tolist()

        # 有効なクリック化を判定し、駒情報の更新、プレイヤーターン切替など。
        self.player_procedure(mpos_index)

    def player_procedure(self, mpos_index: list):
        """ プレイヤーが指定したマス目インデックスに対する動作

        Args:
            mpos_index (list):マス目インデックス(x_index,y_index)

        Raises:
            ReversiException: インデックス値が違反している場合に例外送出

        Returns:
            (bool): 有効な手の場合True
        """
        try:
            # 空いているマス目か判定
            if self.judge_empty_square(mpos_index):
                # 有効なマス目か判定
                candidate_pos = self.judge_put_square(
                    pos_index=mpos_index,
                    turn=self.player_turn,
                )

                if candidate_pos:
                    for cand in candidate_pos:
                        for x_index, y_index in cand['position']:
                            # ひっくり返すマス目に代入
                            self.pieces_on_board[
                                x_index, y_index] = self.player_turn

                    # 指定したマス目に代入
                    x_index, y_index = mpos_index
                    self.pieces_on_board[x_index, y_index] = self.player_turn

                    self.record_play_turn(
                        pos=(x_index, y_index), turn=self.player_turn
                    )

                    # プレイヤーターンの切替
                    self.player_turn = 1 - self.player_turn
                    return True

        except ReversiException:
            raise ReversiException(ReversiException.NOT_EMPTY)

        return False

    def judge_trun(self):
        """ パス・ゲーム終了判定

        Returns:
            [type]: [description]
        """

        X, Y = 0, 1
        isOver = False

        # コマ数取得
        counters = self.count_pieces()
        black = counters[BLACK_PIECE]
        white = counters[WHITE_PIECE]

        # 黒がすべてなくなったら白の勝ち
        if not black:
            return WHITE_WIN
        # 白がすべてなくなったら黒の勝ち
        if not white:
            return BLACK_WIN

        # 駒未配置箇所の取得
        empty = np.where(np.isnan(self.pieces_on_board))
        # 駒未配置箇所のカウント
        empty_count = np.count_nonzero(np.isnan(self.pieces_on_board))

        # 駒未配置箇所がなくなったら終了
        if empty_count:
            # 未配置箇所が現在のPlayerターンで有効なマス目があるかを判定
            empty_pos_list = [(x, y) for x, y in zip(empty[X], empty[Y])]
            judge1, judge2 = list(), list()
            for empty_pos in empty_pos_list:
                pos = self.judge_put_square(
                    pos_index=empty_pos,
                    turn=self.player_turn,
                )
                if pos:
                    judge1.append(pos)
            for empty_pos in empty_pos_list:
                pos = self.judge_put_square(
                    pos_index=empty_pos,
                    turn=1-self.player_turn,
                )
                if pos:
                    judge2.append(pos)
            # 配置できるマス目がない(PASS)
            if not judge1 and not judge2:
                isOver = True
            elif not judge1:
                self.player_turn = 1 - self.player_turn
                return PASS
        elif not empty_count:
            isOver = True

        if isOver:
            # 勝ち負け判定
            if black > white:
                return BLACK_WIN
            elif black < white:
                return WHITE_WIN
            else:
                return DRAW

        return True

    def judge_empty_square(self, pos_index: list):
        """ 未配置マス目の判定

        Args:
            pos_index (list): マス目インデックス(x_index,y_index)
        Raises:
            ReversiException: 未配置マス目がない場合、例外送出
        Returns:
            (bool): 指定されたマス目が未配置ならTrue
        """

        X, Y = 0, 1

        empty = np.where(np.isnan(self.pieces_on_board))
        if empty:
            empty_pos_list = [(x, y) for x, y in zip(empty[X], empty[Y])]
            if tuple(pos_index) in empty_pos_list:
                return True
            else:
                return False

        raise ReversiException(ReversiException.NOT_EMPTY)

    def judge_put_square(self, pos_index: np.array, turn: int):
        """ マス目配置の判定

        Args:
            pos_index (np.array): マス目インデックス(x_index,y_index)
            turn (int): Playerターン（BLACK_PIECE/WHITE_PIECE）

        Returns:
            candidate_pos(list): dict型（position,directtion,count）のリスト
        """

        candidate_pos = list()

        X, Y = 0, 1

        # Playerの相手側の駒配置を取得
        target = np.where(self.pieces_on_board == 1-turn)
        if target:
            target_pos_list = [(x, y) for x, y in zip(target[X], target[Y])]

            # 隣接八方向を示す配列
            direction = np.array(
                [
                    [-1, -1], [0, -1], [1, -1],
                    [-1, 0],        [1, 0],
                    [-1, 1], [0, 1], [1, 1],
                ]
            )

            def _judge_direction_(pos, direct):
                if pos is None:
                    return False
                ans = pos + direct
                x_index, y_index = ans.tolist()
                try:
                    if x_index < 0 or y_index < 0:
                        return False

                    piece = self.pieces_on_board[x_index, y_index]
                    if piece == turn:
                        return True
                    elif piece == 1-turn:
                        return ans
                    else:
                        return False
                except IndexError:
                    return False

            # 指定マス目の隣接八方向のマス目インデックスを算出
            re_pos = np.array(pos_index)+direction
            if re_pos.any():
                for pos, direct in zip(re_pos, direction):
                    if tuple(pos.tolist()) in target_pos_list:
                        # ひっくり返し可能なコマ数をカウント
                        count = 1
                        pos_list = [pos.tolist(), ]
                        isJudge = True
                        # 隣接方向にさらにひっくり返す駒があるかを確認
                        while(isJudge):
                            ans = _judge_direction_(pos, direct)
                            # bool値ならひっくり返す駒がない
                            if isinstance(ans, bool):
                                isJudge = False
                                # Trueの場合、挟み込み可能。
                                if ans:
                                    pos = pos.tolist()
                                    candidate_pos.append(
                                        {
                                            'position': pos_list,
                                            'directtion': direct,
                                            'count': count,
                                        }
                                    )
                            else:
                                # 先の隣接駒情報へ更新
                                pos = ans
                                pos_list.append(pos.tolist())
                                count += 1

        return candidate_pos

    def auto_player(self, isMsample: bool):
        """ 自動配置処理
        """

        X, Y = 0, 1

        # 未配置箇所の取得
        empty = np.where(np.isnan(self.pieces_on_board))
        empty_pos_list = [(x, y) for x, y in zip(empty[X], empty[Y])]

        limit_counter = 300
        while(empty_pos_list):
            # empty_pos_listインデックス値をランダム抽出
            index = random.randint(0, len(empty_pos_list)-1)
            pos = empty_pos_list[index]
            # 配置可能になったら抜け出し
            if self.player_procedure(pos):
                break
            if not isMsample:
                time.sleep(0.05)
            limit_counter -= 1
            if not limit_counter:
                raise 'AutoPlayer infinite loop !!'

        return

    def record_play_turn(self, pos: tuple, turn: int):
        if isinstance(pos, tuple) and isinstance(turn, int):
            if len(pos) == 2:
                x_index, y_index = pos
                hex_A = 0x41
                xkey = chr(hex_A + x_index)
                hex_1 = 0x31
                ykey = chr(hex_1 + y_index)

            if turn == BLACK_PIECE:
                player_key = 'b'
            elif turn == WHITE_PIECE:
                player_key = 'w'

            process = self.game_record['process']

            process += '{}{}{}'.format(player_key, xkey, ykey)
            self.game_record['process'] = process

        return

    def record_game_result(self):
        counters = self.count_pieces()
        black = counters[BLACK_PIECE]
        white = counters[WHITE_PIECE]

        self.game_record['result']['black'] = black
        self.game_record['result']['wihte'] = white

        record_txt = json.dumps(self.game_record)

        current = os.getcwd()
        file_path = current + "/data"

        if os.path.exists(file_path):
            with open(file_path+'/game_result.txt', 'a') as f:
                f.write(record_txt+'\n')

        return


if __name__ == '__main__':
    isPlaygame = False

    if isPlaygame:
        result = BoardSurface().run(True, True, True)
    else:
        # 試行回数
        practice_time = 5000
        counter = practice_time
        # 機械学習フラグ
        isMsample = True
        # AutoPlayer
        isAutoBlack = True
        isAutoWhite = True

        while(counter):
            result = BoardSurface().run(isMsample, isAutoBlack, isAutoWhite)
            print('Game{:4d}'.format(practice_time+1-counter))
            print(result)
            counter -= 1
