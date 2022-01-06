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

import json
import numpy as np
import os
import pygame
import random
import time
import sys

source_path = os.getcwd() + '\\source'
if os.path.exists(source_path):
    sys.path.append(source_path)
    import draw_game
else:
    print('error:The source code path is incorrect.')
    sys.exit()

BLACK_PIECE = draw_game.BLACK_PIECE
WHITE_PIECE = draw_game.WHITE_PIECE

BLACK_WIN = draw_game.BLACK_WIN
WHITE_WIN = draw_game.WHITE_WIN
DRAW = draw_game.DRAW
PASS = draw_game.PASS


class ReversiException(Exception):
    NOT_EMPTY = 'NOT EMPTY SQUARE'


class ReversiGame(draw_game.BoardSurface):
    def __init__(self):
        """ 初期化
        """

        super().__init__()

        self.init_game_record()

        return

    def init_game_record(self):
        """ 盤面配列初期化
        """

        self.game_record = {
            'result': {
                'black': None, 'wihte': None,
            },
            'process': '',
        }

    def run(self,
            isMsample: bool = False,
            isAutoBlack: bool = False,
            isAutoWhite: bool = False
            ):
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
                self.draw_pieces(self.pieces_on_board)
                # プレイヤーターン描画
                self.draw_player(self.player_turn)
                # 黒白コマ数描画
                self.draw_counter(self.pieces_on_board)
                # GUI描画更新
                pygame.display.update()

            # ゲームの判定
            judge = self.judge_trun(self.player_turn, self.pieces_on_board)
            if 'player_turn' in judge:
                self.player_turn = judge['player_turn']
            if 'judge' in judge:
                game_judge = judge['judge']
                if game_judge != PASS:
                    self.record_game_result(self.pieces_on_board)
                    if not isMsample:
                        self.draw_game_over(judge)
                        pygame.display.update()
                        time.sleep(1)
                        pygame.quit()
                        break
                    else:
                        break

            # 自動配置処理
            if self.player_turn == WHITE_PIECE and isAutoBlack:
                self.auto_player(isMsample)
                if not isMsample:
                    time.sleep(0.1)
            elif self.player_turn == BLACK_PIECE and isAutoWhite:
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

    def judge_trun(self, player_turn, pieces_on_board):
        """ パス・ゲーム終了判定

        Returns:
            [type]: [description]
        """

        X, Y = 0, 1
        isOver = False

        ret_dict = dict()

        # コマ数取得
        counters = self.count_pieces(pieces_on_board)
        black = counters[BLACK_PIECE]
        white = counters[WHITE_PIECE]

        # 黒がすべてなくなったら白の勝ち
        if not black:
            return WHITE_WIN
        # 白がすべてなくなったら黒の勝ち
        if not white:
            return BLACK_WIN

        # 駒未配置箇所の取得
        empty = np.where(np.isnan(pieces_on_board))
        # 駒未配置箇所のカウント
        empty_count = np.count_nonzero(np.isnan(pieces_on_board))

        # 駒未配置箇所がなくなったら終了
        if empty_count:
            # 未配置箇所が現在のPlayerターンで有効なマス目があるかを判定
            empty_pos_list = [(x, y) for x, y in zip(empty[X], empty[Y])]
            judge1, judge2 = list(), list()
            for empty_pos in empty_pos_list:
                pos = self.judge_put_square(
                    pos_index=empty_pos,
                    turn=player_turn,
                )
                if pos:
                    judge1.append(pos)
            for empty_pos in empty_pos_list:
                pos = self.judge_put_square(
                    pos_index=empty_pos,
                    turn=1-player_turn,
                )
                if pos:
                    judge2.append(pos)
            # 配置できるマス目がない(PASS)
            if not judge1 and not judge2:
                isOver = True
            elif not judge1:
                player_turn = 1 - player_turn
                ret_dict.setdefault('judge', PASS)

        elif not empty_count:
            isOver = True

        ret_dict.setdefault('player_turn', player_turn)

        if isOver:
            judge = None
            # 勝ち負け判定
            if black > white:
                judge = BLACK_WIN
            elif black < white:
                judge = WHITE_WIN
            else:
                judge = DRAW
            ret_dict.setdefault('judge', judge)

        return ret_dict

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
        """ 指しての記録

        Args:
            pos (tuple): マス目インデックス(x_index,y_index)
            turn (int): プレイヤーターン
        """

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

    def record_game_result(self, pieces_on_board):
        """ ゲーム結果の記録
        """

        counters = self.count_pieces(pieces_on_board)
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
    isPlaygame = True

    if isPlaygame:
        result = ReversiGame().run(False, True, False)
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
            result = ReversiGame().run(isMsample, isAutoBlack, isAutoWhite)
            print('Game{:4d}'.format(practice_time+1-counter))
            print(result)
            counter -= 1
