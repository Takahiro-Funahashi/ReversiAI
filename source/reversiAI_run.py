from typing import NewType
import numpy as np
import pygame
import sys
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
        self.board_size = (400,400)
        self.screnn_offset = (40,80)
        ans = np.array(self.board_size) + (np.array(self.screnn_offset)*2)
        self.screen_size = ans.tolist()
        self.board_squares = (8,8)
        self.font_size = 24

        ans = np.array(self.board_size) / np.array(self.board_squares)
        self.square_size = ans.tolist()

        self.init_pieces()

        return


    def init_pieces(self):
        self.pieces_on_board = np.full(self.board_squares,np.nan)
        self.pieces_on_board[3,3] = BLACK_PIECE
        self.pieces_on_board[4,4] = BLACK_PIECE
        self.pieces_on_board[3,4] = WHITE_PIECE
        self.pieces_on_board[4,3] = WHITE_PIECE

        self.player_turn = BLACK_PIECE
        return

    def init_pygeme(self):

        pygame.init()
        self.game_screen = pygame.display.set_mode(
            size=self.screen_size,
            #flags=pygame.FULLSCREEN,
            )
        pygame.display.set_caption('ReversiAI')

        self.game_font = pygame.font.Font(
            None, self.font_size)

        return


    def run(self):
        self.init_pygeme()
        self.draw_background()

        while(True):
            self.draw_board_frame()
            self.draw_pieces()
            self.draw_player()
            self.draw_counter()

            pygame.display.update()

            judge = self.judge_trun()
            if judge is not True:
                if judge != PASS:
                    self.game_over(judge)
                    pygame.display.update()
                    time.sleep(5)
                    pygame.quit()
                    sys.exit()

            if self.player_turn == WHITE_PIECE:
                self.auto_player()
                time.sleep(0.3)
            elif self.player_turn == BLACK_PIECE:
                self.auto_player()
                time.sleep(0.3)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == pygame.BUTTON_LEFT:
                        x, y = event.pos
                        self.mouse_left_clicked(event.pos)



    def draw_background(self):
        self.game_screen.fill('darkgreen')


    def draw_board_frame(self):
        line_width = 2
        X, Y = 0, 1
        screen = self.game_screen
        offset_x, offset_y = self.screnn_offset
        board_w, board_h = self.board_size

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
                (board_w+offset_x-1,offset_y),
                (board_w+offset_x-1,board_h+offset_y-1),
                (offset_x,board_h+offset_y-1),
                ],
            width=line_width,
            )

        # 盤面縦線
        H_sq_size, V_sq_size = self.square_size
        for x_index in range(1,self.board_squares[X]):
            pygame.draw.line(
                surface=screen,
                color='black',
                start_pos=(offset_x+H_sq_size*x_index-1, offset_y),
                end_pos=(offset_x+H_sq_size*x_index-1, board_h+offset_y-1),
                width=line_width
            )

        # 盤面横線
        for y_index in range(1,self.board_squares[Y]):
            pygame.draw.line(
                surface=screen,
                color='black',
                start_pos=(offset_x, offset_y+V_sq_size*y_index-1),
                end_pos=(board_w+offset_x-1, offset_y+V_sq_size*y_index-1),
                width=line_width
            )

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
        p_offset = 2
        X, Y = 0, 1
        screen = self.game_screen
        offset_x, offset_y = self.screnn_offset

        black_pieces = np.where(self.pieces_on_board == BLACK_PIECE)
        white_pieces = np.where(self.pieces_on_board == WHITE_PIECE)

        if black_pieces:
            raw, clm = black_pieces
            for x_index, y_index in zip(raw, clm):
                cx = offset_x + self.square_size[X]*x_index + self.square_size[X]/2
                cy = offset_y + self.square_size[Y]*y_index + self.square_size[Y]/2
                pygame.draw.circle(
                    surface=screen,
                    color='black',
                    center=(cx,cy),
                    radius=self.square_size[X]/2-p_offset*2,
                )

        if white_pieces:
            raw, clm = white_pieces
            for x_index, y_index in zip(raw, clm):
                cx = offset_x + self.square_size[X]*x_index + self.square_size[X]/2
                cy = offset_y + self.square_size[Y]*y_index + self.square_size[Y]/2
                pygame.draw.circle(
                    surface=screen,
                    color='white',
                    center=(cx,cy),
                    radius=self.square_size[X]/2-p_offset*2,
                )

        return


    def draw_player(self):
        X, Y = 0, 1
        t_offset_x, t_offset_y= 10, 20
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
        X, Y = 0, 1
        t_offset_x, t_offset_y= 10, 20
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
            [cx+circle_size*2,cy-5]
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
            [cx+circle_size*7,cy-5]
            )

        return


    def count_pieces(self):
        black_count = np.count_nonzero(self.pieces_on_board==BLACK_PIECE)
        white_count = np.count_nonzero(self.pieces_on_board==WHITE_PIECE)

        return {BLACK_PIECE:black_count,WHITE_PIECE:white_count}


    def mouse_left_clicked(self,pos):
        board_pos = np.array(pos)-np.array(self.screnn_offset)
        ans = board_pos/np.array(self.square_size)
        ans = ans.astype('uint8')
        mpos_index = ans.tolist()

        self.player_procedure(mpos_index)


    def player_procedure(self,mpos_index):
        try:
            if self.judge_empty_square(mpos_index):
                candidate_pos = self.judge_put_square(
                    pos_index=mpos_index,
                    turn=self.player_turn,
                    )

                if candidate_pos:
                    for cand in candidate_pos:
                        for x_index, y_index in cand['position']:
                            self.pieces_on_board[x_index, y_index] = self.player_turn
                    x_index, y_index = mpos_index
                    self.pieces_on_board[x_index, y_index] = self.player_turn

                    self.player_turn = 1 - self.player_turn
                    return True

        except ReversiException:
            raise ReversiException(ReversiException.NOT_EMPTY)

        return False


    def judge_trun(self):
        X, Y = 0, 1

        counters = self.count_pieces()
        black = counters[BLACK_PIECE]
        white = counters[WHITE_PIECE]

        if not black:
            return WHITE_WIN
        if not white:
            return BLACK_WIN

        empty = np.where(np.isnan(self.pieces_on_board))
        empty_count = np.count_nonzero(np.isnan(self.pieces_on_board))
        if not empty_count:
            if black > white:
                return BLACK_WIN
            elif black < white:
                return WHITE_WIN
            else:
                return DRAW
        else:
            empty_pos_list = [(x, y) for x, y in zip(empty[X],empty[Y])]
            judge = list()
            for empty_pos in empty_pos_list:
                pos = self.judge_put_square(
                    pos_index = empty_pos,
                    turn = self.player_turn,
                    )
                if pos:
                    judge.append(pos)
            if not judge:
                self.player_turn = 1 - self.player_turn
                return PASS

        return True


    def judge_empty_square(self,pos_index):
        X, Y = 0, 1

        empty = np.where(np.isnan(self.pieces_on_board))
        if empty:
            empty_pos_list = [(x, y) for x, y in zip(empty[X],empty[Y])]
            if tuple(pos_index) in empty_pos_list:
                return True
            else:
                return False

        raise ReversiException(ReversiException.NOT_EMPTY)


    def judge_put_square(self,pos_index,turn):
        candidate_pos = list()

        X, Y = 0, 1
        target = np.where(self.pieces_on_board == 1-turn)
        if target:
            target_pos_list = [(x, y) for x, y in zip(target[X],target[Y])]
            direction = np.array(
                [
                    [-1,-1],[ 0,-1],[ 1,-1],
                    [-1, 0],        [ 1, 0],
                    [-1, 1],[ 0, 1],[ 1, 1],
                ]
            )

            def _judge_direction_(pos,direct):
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


            re_pos = np.array(pos_index)+direction
            if re_pos.any():
                for pos, direct in zip(re_pos,direction):
                    if tuple(pos.tolist()) in target_pos_list:
                        count = 1
                        pos_list = [pos.tolist(),]
                        isJudge = True
                        while(isJudge):
                            ans = _judge_direction_(pos,direct)
                            if isinstance(ans,bool):
                                isJudge = False
                                if ans:
                                    pos = pos.tolist()
                                    candidate_pos.append(
                                        {
                                            'position':pos_list,
                                            'directtion':direct,
                                            'count':count,
                                        }
                                    )
                            else:
                                pos = ans
                                pos_list.append(pos.tolist())
                                count += 1

        return candidate_pos


    def game_over(self,judge):
        X, Y = 0, 1
        dialog_size = (150,40)
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


    def auto_player(self):
        import random

        X, Y = 0, 1

        empty = np.where(np.isnan(self.pieces_on_board))
        empty_pos_list = [(x, y) for x, y in zip(empty[X],empty[Y])]


        while(True):
            index = random.randint(0,len(empty_pos_list)-1)
            pos = empty_pos_list[index]
            if self.player_procedure(pos):
                break
            time.sleep(0.05)

        return

if __name__ == '__main__':
    BoardSurface().run()
