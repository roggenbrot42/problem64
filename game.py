import time
import math as m
import numpy as np
from collections import Counter
import copy
from bitarray import bitarray
from bitarray import util as btutil
import argparse
from zobrist import ZobristTable
from problem64 import Color, Move, Board, Stack

class Game:
    def __init__(self):
        self.initialize_game()
    
    def initialize_game(self):
        self.board = Board(0,0)
        self.board[27] = Color.BLACK
        self.board[36] = Color.BLACK
        self.board[28] = Color.WHITE
        self.board[35] = Color.WHITE

        self.shallow_depth = 4 #default for shallow depth move ordering
        self.counter = self.board.count()
        self.pruned = 0
        self.evals = 0
        self.symm = 0
        self.moves = 0
        self.current_player = Color.BLACK
        self.flipstack = Stack(3000)
        self.zobrist = ZobristTable()
        self.zobrist.calc_keys()
        self.current_hash = self.zobrist.hash_board(self.board)
    
    structure = np.array([[16, -4, 4, 2, 2, 4, -4, 16],
                            [-4, -12, -2, -2 ,-2, -2, -12,-4],
                            [4, -2, 4, 2, 2, 4, -2, 4],
                            [2, -2, 2, 0, 0, 2, -2, 2],
                            [2, -2, 2, 0, 0, 2, -2, 2],
                            [4, -2, 4, 2, 2, 4, -2, 4],
                            [-4, -12, -2, -2 ,-2, -2, -12,-4],
                            [16, -4, 4, 2, 2, 4, -4, 16]]).flatten()
        

    #TODO: Implement actual test
    def move_valid(self, move, player):
        if self.board[move.y*8+move.x] != Color.NONE:
            return False
        return True

    def count(self):
        return self.board.count()
       

    def draw_board(self):
        print(self.board)

    def scan_move(self, i, j, player):
        retval = []
        for yinc in range(-1,2):
            for xinc in range(-1,2):
                if xinc == 0 and yinc == 0:
                    continue
                x = j
                y = i

                nmoves = 0

                while True:
                    x += xinc
                    y += yinc
                    if x>=0 and y>=0 and x<=7 and y<=7:
                        if self.board[y*8+x] == -player:
                            nmoves += 1
                        else:
                            break
                    else:
                        nmoves = 0
                        break

                if nmoves >  0 and self.board[y*8+x] == Color.NONE:
                    if x < 0 or y < 0:
                        print("boink")
                    else:
                        retval.append(Move(x,y))

        return retval
    
    #TODO: this function is too slow
    def next_moves(self,player):
        next_moves = []

        if self.board.outside_square() == False:
            rmin = 1
            rmax = 7
        else:
            rmin = 0
            rmax = 8
        
        for i in range(rmin,rmax):
            for j in range(rmin,rmax):
                if self.board[i*8+j] == player:
                    m = self.scan_move(i,j,player)
                    next_moves += m
        used = set()
        unique = [x for x in next_moves if x not in used and (used.add(x) or True)]
        return unique

    def make_move(self,player,move):
        flipped = 0
        i = move.y
        j = move.x

        self.board[i*8+j] = player
        #self.current_hash ^= int(self.zobrist.key_table[i*8+j][player])

        for yinc in range(-1,2):
            for xinc in range(-1,2):
                if xinc == 0 and yinc ==0:
                    continue
                y = i
                x = j
                nmoves = 0

                while True:
                    x += xinc
                    y += yinc
                    if x>=0 and y>=0 and x<=7 and y<=7:
                        if self.board[y*8+x] == -player:
                            nmoves += 1
                        else:
                            break
                    else:
                        nmoves = 0
                        break

                if nmoves > 0 and self.board[y*8+x] == player:
                    x -= xinc
                    y -= yinc
                    while self.board[y*8+x] == -player:
                        self.flipstack.push(y,x)
                        flipped += 1
                        self.board.flip(y*8+x)
                        x -= xinc
                        y -= yinc
        self.counter[player] += flipped + 1
        self.counter[-player] -= flipped

        self.moves += 1
        return flipped
    
    def undo_move(self,move,flipped):
        i = move.y
        j = move.x

        player = self.board[i*8+j]
        self.counter[player] -=  flipped + 1
        self.counter[-player] += flipped
        self.board[i*8+j] = Color.NONE
        #self.current_hash ^= int(self.zobrist.key_table[i*8+j][player]) #TODO: zobrist.get_key()

        for i in range(0,flipped):
            (y,x) = self.flipstack.pop()
            self.board.flip(y*8+x)
    
    def eval_structure(self,c):
        structure_sum = 0
        outside_square = self.board.outside_square()
        mult = 1

        if outside_square:
            b = self.board.copy()
            b.wstate &= ~b.square_mask
            b.bstate &= ~b.square_mask
            mult = 3
        else:
            b = self.board

        
        x = btutil.int2ba(b.wstate,length=64)
        y = btutil.int2ba(b.bstate,length=64)
        
        structure_sum = np.matmul(y.tolist(),self.structure)
        structure_sum -= np.matmul(x.tolist(),self.structure)


        structure_sum *= mult*c
        return structure_sum

    def eval(self):
        self.evals += 1

        omoves = self.next_moves(-self.current_player)
        moves = self.next_moves(self.current_player)

        M = (len(moves)-len(omoves))*2
        S = self.eval_structure(self.current_player)
        A = self.counter[self.current_player] - self.counter[-self.current_player]
     
        n = self.counter[Color.WHITE]+self.counter[Color.BLACK]
        z = 0.035
        W = m.exp(-n*z)

        score = (M+S)*W + A*(1-W)
        return score
    
    def sort_initial_moves(self,moves):
        sorted_moves = []
        alpha = -m.inf
        beta = m.inf
        max_value = alpha
        value = 0
        for mov in moves:
            s = self.make_move(self.current_player,mov)
            value = self.alphabeta_min(self.shallow_depth-1,max_value,beta)
            self.undo_move(mov,s)
            sorted_moves.append((value,mov))
        sorted_moves.sort(reverse=True)
        return sorted_moves

    def alphabeta_init(self,depth):
        moves = self.next_moves(self.current_player)
        if len(moves) == 1:
            return moves[0]

        retmov = None
        alpha = -m.inf
        beta = m.inf
        max_value = alpha
        value = 0
        sorted_moves = self.sort_initial_moves(moves)
        for item in sorted_moves:
            mov = item[1]
            s = self.make_move(self.current_player,mov)
            value = self.alphabeta_min(depth-1,max_value,beta)
            self.undo_move(mov,s)
            if value > max_value:
                max_value = value
                retmov = mov
                if max_value >= beta:
                    self.pruned += 1
                    break
            #samesies but use the alphabetically lower version
            if value == max_value and mov and mov < retmov:
                retmov = mov
        return (value,retmov)

    def alphabeta_max(self, depth, alpha, beta):
        moves = self.next_moves(self.current_player)

        if len(moves) == 0 or depth == 0:
            return self.eval()
        
        max_value = alpha
        for mov in moves:
            s = self.make_move(self.current_player,mov)
            value = self.alphabeta_min(depth-1,max_value,beta)
            self.undo_move(mov,s)
            if value > max_value:
                max_value = value
                if max_value >= beta:
                    self.pruned += 1
                    break               
        return max_value
    
    def alphabeta_min(self, depth, alpha, beta):
        moves = self.next_moves(-self.current_player)
        if len(moves) == 0 or depth == 0:
            return self.eval()

        min_value = beta
        for mov in moves:
            s = self.make_move(-self.current_player,mov)
            value = self.alphabeta_max(depth-1,alpha,min_value)
            self.undo_move(mov,s)
            if value < min_value:
                min_value = value
                if min_value <= alpha:
                    self.pruned += 1
                    break
        return min_value

def test_symmetry():
    b = Board(0,0)
    b[27] = Color.BLACK
    b[28] = Color.BLACK
    b[63] = Color.WHITE
    b[56] = Color.WHITE
    #b[62] = Color.WHITE
    #b[56] = Color.WHITE
    #b = g.game_state.copy()
    #print("x symmetry")
    #print(b)
    assert(b.wstate == b.bit_reverse_8(b.wstate))
    assert(b.bstate == b.bit_reverse_8(b.bstate))
    b = Board(0,0)
    b[0] = Color.WHITE
    b[56] = Color.WHITE
    #print("y symmetry")
    #print (b)
    assert(b.wstate == b.flip_vertically(b.wstate))
    assert(b.bstate == b.flip_vertically(b.bstate))
    #print(b)
    b = Game().board
    #print("180 degree rotation")
    #print (b)
    assert(b.wstate == b.bit_reverse_64(b.wstate))
    assert(b.bstate == b.bit_reverse_64(b.bstate))
    print("Symmetry test successful.")

def test_eval():
    g = Game()
    assert(g.eval() == 0)
    b = g.board
    b[2*8+5] = Color.WHITE
    b[3*8+5] = Color.BLACK
    b[4*8+2] = Color.BLACK
    b[5*8+2] = Color.WHITE
    assert(g.eval_structure(Color.WHITE) == 4)
    assert(g.eval_structure(Color.BLACK) == -4)
    b[0] = Color.BLACK
    assert(g.eval_structure(Color.BLACK)==48)
    assert(g.eval_structure(Color.WHITE)==-48)
    g = Game()
    assert(len(g.next_moves(Color.BLACK))==4)
    g.make_move(Color.BLACK,Move(4,2))
    np.testing.assert_almost_equal(g.eval(),2.160542979230793)
    print("Evaluation Test successful")

def test_count():
    arg = 0xFFFFFFEFFFFFFF3F
    print("{0:b}".format(Board.count_bits(arg)))
    print(Board.count_bits(arg))
        
    
def main():
    parser = argparse.ArgumentParser(description='CLI based reversi game with AI player')
    parser.add_argument('--test', action='store_true')
    parser.add_argument('-v','--verbose', action='store_true')
    parser.add_argument('--count','-c',action='store_true')

    args = parser.parse_args()
    if args.test:
        test_symmetry()
        test_eval()
    elif args.count:
        test_count()
    else:
        run()
    
    


def run():
    g = Game()
    b = g.board
    b[2*8+5] = Color.WHITE
    b[3*8+5] = Color.BLACK
    b[4*8+2] = Color.BLACK
    b[5*8+2] = Color.WHITE
    print(b)
    g.zobrist.load_from_file('zobrist.npz')
    hashed_board = g.zobrist.hash_board(b)
    g.current_hash = hashed_board
    

    g.shallow_depth = 4
    depth = 7

    passing = 0
    moves = []

    passing = 0

    while True:
        try:
            cev = g.evals
            cmv = g.moves
            cpr = g.pruned
            sym = g.symm
            t1 = time.time()
            
            (value,mv) = g.alphabeta_init(depth)

            t1 = time.time() - t1
            print("Time: {}s".format(t1))
            cev = g.evals - cev
            cmv = g.moves - cmv
            cpr = g.pruned - cpr
            sym = g.symm - sym
            print("Evals: {} Evals/s: {} Moves: {} Pruned: {} Symmetry: {}".format(cev,cev/t1,cmv,cpr,sym))

            if mv != None:
                g.make_move(g.current_player,mv)
                moves.append(mv)
                g.draw_board()
                print("Color: {} Move: {} Value: {:0.9f}".format(Color.format(g.current_player),mv,value))
                passing = 0
            else:
                passing += 1
                print("Color: {}".format(Color.format(g.current_player)))
            if passing == 2:
                break

            g.current_player = -g.current_player
        except KeyboardInterrupt:
            #g.zobrist.save_to_file('zobrist.npz')
            break
        except: #make crashes traceable
            for mov in moves:
                print(mov,end="")
                print()
            print(b.wstate)
            print(b.bstate)
    
    c = g.count()
    if c[Color.WHITE] > c[Color.BLACK]:
        print("WHITE won!")
    else:
        print("BLACK won!")

    for mov in moves:
        print(mov,end="")
    print()

if __name__ == "__main__":
    main()