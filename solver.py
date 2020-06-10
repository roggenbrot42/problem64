import time
import math as m
import numpy as np
from collections import Counter
import copy
from bitarray import bitarray
from bitarray import util as btutil

class Color:
    NONE = 0
    WHITE = -1
    BLACK = 1
    def __neg__(self):
        return -self.value
    def __int__(self):
        return self.value
    @staticmethod
    def format(c): #requires dark mode terminal
        if c == -1:
            return '◆'
        elif c == 1:
            return '◇'
        else:
            return '▢'

class Move:
    def __init__(self,x,y):
        self.x = int(x)
        self.y = int(y)

    def __str__(self):
        return f"{chr(self.x+97)}{8-self.y}"
    
    def __eq__(self, other): 
        if not isinstance(other, Move):
            return NotImplemented
        else:
            if other.x == self.x and other.y == self.y:
                return True
            else:
                return False
    def __lt__(self,other):
        if not isinstance(other, Move):
            return False
        else:
            return (self.x,self.y)<=(other.x,other.y)

    def isValid(self):
        if self.x >= 0 and self.x <= 7 and self.y >= 0 and self.y <= 7:
            return True
        else:
            return False
    def __hash__(self):
        return self.x*16+self.y
 
class Stack:
    def __init__(self, size):
        self.stack = np.zeros(size,dtype=type((0,0)))
        self.sp = -1
        self.size = size
    
    def push(self, y, x):
        if self.sp < self.size-1:
            self.sp += 1
            self.stack[self.sp] = (y,x)
    
    def pop(self):
        retval = None
        if self.sp >= 0 and self.sp < self.size:
            retval = self.stack[self.sp]
            self.sp -= 1
        return retval
    
class Board:

    wstate = 0
    bstate = 0
    square_mask = 0x00003C3C3C3C0000

    def __init__(self,wstate,bstate):
        self.wstate = wstate
        self.bstate = bstate
    
    def copy(self):
        board = Board(self.wstate,self.bstate)
        return board
    
    def __getitem__(self, key):
        if (self.wstate >> key) & 1:
            return Color.WHITE
        elif (self.bstate >> key) & 1:
            return Color.BLACK
        else:
            return Color.NONE

    def __setitem__(self,key,value):
        if value == Color.WHITE:
            self.wstate = self.wstate | (1 << key)
        elif value == Color.BLACK:
            self.bstate = self.bstate | (1 << key)
        else:
            self.wstate &= ~(1 << key)
            self.bstate &= ~(1 << key)
    
    def flip(self,key):
        self.wstate = self.wstate ^ (1 << key)
        self.bstate = self.bstate ^ (1 << key)
    
    def delitem(self,key):
        self.wstate &= ~(1 << key)
        self.bstate &= ~(1 << key)

    @staticmethod
    def bit_reverse_8(input):
        val = ((input >> 1) & 0x5555555555555555) | ((input << 1) & 0xAAAAAAAAAAAAAAAAAA)
        val = ((val >> 2) & 0x3333333333333333) | ((val << 2) & 0xCCCCCCCCCCCCCCCC)
        val = ((val >> 4) & 0x0F0F0F0F0F0F0F0F) | ((val << 4) & 0xF0F0F0F0F0F0F0F0)
        return val

    @staticmethod
    def bit_reverse_64(input):
        val = ((input >> 1) & 0x5555555555555555) | ((input << 1) & 0xAAAAAAAAAAAAAAAAAA)
        val = ((val >> 2) & 0x3333333333333333) | ((val << 2) & 0xCCCCCCCCCCCCCCCC)
        val = ((val >> 4) & 0x0F0F0F0F0F0F0F0F) | ((val << 4) & 0xF0F0F0F0F0F0F0F0)
        val = ((val >> 8) & 0x00FF00FF00FF00FF) | ((val << 8) & 0xFF00FF00FF00FF00)
        val = ((val >> 16)& 0x0000FFFF0000FFFF) | ((val << 16)& 0xFFFF0000FFFF0000)
        val = ((val >> 32)& 0x00000000FFFFFFFF) | ((val << 32)& 0xFFFFFFFF00000000)
        return val
    
    @staticmethod
    def flip_vertically(input):
        val = ((input & 0x00000000FFFFFFFF) << 32) | ((input & 0xFFFFFFFF00000000) >> 32)
        val = ((val & 0x0000FFFF0000FFFF) << 16) | ((val & 0xFFFF0000FFFF0000) >> 16)
        val = ((val & 0x00FF00FF00FF00FF) << 8) | ((val & 0xFF00FF00FF00FF00) >> 8)
        return val
    
    def outside_square(self):
        return (self.wstate | self.bstate) & self.square_mask > 0

    def check_symmetries(self):
        symmetry = 0
        #check x symmetry:
        a = self.bit_reverse_8(self.wstate)
        b = self.bit_reverse_8(self.bstate)
        if (a == self.wstate and b == self.bstate):
            symmetry |= 1
        #check y symmetry:
        a = self.flip_vertically(self.wstate)
        b = self.flip_vertically(self.bstate)
        if a == self.wstate and b == self.bstate:
            symmetry |= 2
        #check 180 degree rotation
        a = self.bit_reverse_64(self.wstate)
        b = self.bit_reverse_64(self.bstate)
        if (a == self.wstate and b == self.bstate):
            symmetry |= 4
        return symmetry
    
    def count(self):
        a = btutil.int2ba(self.wstate)
        b = btutil.int2ba(self.bstate)
        c = Counter()
        c[Color.WHITE] = a.count(True)
        c[Color.BLACK] = b.count(True)
        return c

    @staticmethod
    def tostring(x,y):
        a = btutil.int2ba(x,length=64)
        b = btutil.int2ba(y,length=64)
        string = ""
        c = Color.NONE
        for i in range(0,8):
            x = 7-i
            string += "{} ".format(x+1)
            for j in range(0,8):
                y = 7-j
                if a[x*8+y]:
                    c = Color.WHITE
                elif b[x*8+y]:
                    c = Color.BLACK
                else:
                    c = Color.NONE
                string += "{} ".format(Color.format(c))
            string += "\n"
        string += "  A B C D E F G H"
        return string
    def __str__(self):
        return self.tostring(self.wstate,self.bstate)



class Game:
    def __init__(self):
        self.initialize_game()
    
    def initialize_game(self):
        self.game_state = Board(0,0)
        self.game_state[27] = Color.BLACK
        self.game_state[36] = Color.BLACK
        self.game_state[28] = Color.WHITE
        self.game_state[35] = Color.WHITE

        self.shallow_depth = 4 #default for shallow depth move ordering
        self.counter = self.game_state.count()
        self.pruned = 0
        self.evals = 0
        self.symm = 0
        self.moves = 0
        self.current_player = Color.BLACK
        self.flipstack = Stack(3000)
    
    structure = np.array([[16, -4, 4, 2, 2, 4, -4, 16],
                            [-4, 12, -2, -2 ,-2, -2, -12,-4],
                            [4, -2, 4, 2, 2, 4, -2, 4],
                            [2, -2, 2, 0, 0, 2, -2, 2],
                            [2, -2, 2, 0, 0, 2, -2, 2],
                            [4, -2, 4, 2, 2, 4, -2, 4],
                            [-4, 12, -2, -2 ,-2, -2, -12,-4],
                            [16, -4, 4, 2, 2, 4, -4, 16]]).flatten()
        

    #TODO: Implement actual test
    def move_valid(self, move, player):
        if self.game_state[move.y*8+move.x] != Color.NONE:
            return False
        return True

    def count(self):
        return self.game_state.count()
       

    def draw_board(self):
        print(self.game_state)

    def test_move(self, i, j, player):
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
                        if self.game_state[y*8+x] == -player:
                            nmoves += 1
                        else:
                            break
                    else:
                        nmoves = 0
                        break

                if nmoves >  0 and self.game_state[y*8+x] == Color.NONE:
                    if x < 0 or y < 0:
                        print("boink")
                    else:
                        retval.append(Move(x,y))

        return retval
    
    #TODO: this function is too slow
    def next_moves(self,player):
        next_moves = []

        if self.game_state.outside_square() == False:
            rmin = 1
            rmax = 7
        else:
            rmin = 0
            rmax = 8
        
        for i in range(rmin,rmax):
            for j in range(rmin,rmax):
                if self.game_state[i*8+j] == player:
                    m = self.test_move(i,j,player)
                    next_moves += m
        used = set()
        unique = [x for x in next_moves if x not in used and (used.add(x) or True)]
        return unique

    def make_move(self,player,move):
        flipped = 0
        i = move.y
        j = move.x

        self.game_state[i*8+j] = player

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
                        if self.game_state[y*8+x] == -player:
                            nmoves += 1
                        else:
                            break
                    else:
                        nmoves = 0
                        break

                if nmoves > 0 and self.game_state[y*8+x] == player:
                    x -= xinc
                    y -= yinc
                    while self.game_state[y*8+x] == -player:
                        self.flipstack.push(y,x)
                        flipped += 1
                        self.game_state.flip(y*8+x)
                        x -= xinc
                        y -= yinc
        self.counter[player] += flipped + 1
        self.counter[-player] -= flipped

        self.moves += 1
        return flipped
    
    def undo_move(self,move,flipped):
        i = move.y
        j = move.x

        player = self.game_state[i*8+j]
        self.counter[player] -=  flipped + 1
        self.counter[-player] += flipped
        self.game_state[i*8+j] = Color.NONE

        for i in range(0,flipped):
            (y,x) = self.flipstack.pop()
            self.game_state.flip(y*8+x)
    
    def eval_structure(self,c):
        structure_sum = 0
        outside_square = self.game_state.outside_square()
        mult = 1

        if outside_square:
            b = self.game_state.copy()
            b.wstate &= ~b.square_mask
            b.bstate &= ~b.square_mask
            mult = 3
        else:
            b = self.game_state

        
        x = btutil.int2ba(b.wstate,length=64)
        y = btutil.int2ba(b.bstate,length=64)
        
        structure_sum = np.matmul(x.tolist(),self.structure)
        structure_sum -= np.matmul(y.tolist(),self.structure)

        structure_sum *= mult
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

    
    def minimax_max(self, c, depth):
        moves = self.next_moves(c)

        if self.depth == depth and len(moves) == 1:
            return (m.inf, moves[0])

        #game is finished can't move anymore
        if len(moves) == 0 or depth == 0:
            return (self.eval(c,moves),None)

        retmv = None

        max_value = -m.inf
        for mov in moves:
            s = self.make_move(c,mov)
            value = self.minimax_min(-c,depth-1)
            max_value = max(max_value,value)
            self.undo_move(mov,s)
        return (value,retmv)

    def minimax_min(self, c, depth):
        moves = self.next_moves(c)

        #game is finished can't move anymore
        if len(moves) == 0 or depth == 0:
            return self.eval(c,moves)

        min_value = m.inf
        for mov in moves:
            s = self.make_move(c,mov)
            (value,xxx) = self.minimax_max(-c,depth-1)
            min_value = min(min_value, value)
            self.undo_move(mov,s)
        return value

    def alphabeta_init(self,depth):
        moves = self.next_moves(self.current_player)
        if len(moves) == 1:
            return moves[0]

        retmov = None
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

def test():
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
    b = Game().game_state
    #print("180 degree rotation")
    #print (b)
    assert(b.wstate == b.bit_reverse_64(b.wstate))
    assert(b.bstate == b.bit_reverse_64(b.bstate))

        
    
def main():
    test()
    run()
    
    


def run():
    g = Game()
    b = g.game_state
    b[2*8+5] = Color.WHITE
    b[3*8+5] = Color.BLACK
    b[4*8+2] = Color.BLACK
    b[5*8+2] = Color.WHITE
    print(b)

    g.shallow_depth = 4

    passing = 0
    moves = []

    passing = 0

    while True:
        #if cp == Color.BLACK:
        cev = g.evals
        cmv = g.moves
        cpr = g.pruned
        sym = g.symm
        t1 = time.time()
        (value,mv) = g.alphabeta_init(7)
        #(value,mv) = g.minimax_max(cp,g.depth)
        t1 = time.time() - t1
        print("Time: {}s".format(t1))
        cev = g.evals - cev
        cmv = g.moves - cmv
        cpr = g.pruned - cpr
        sym = g.symm - sym
        print("Evals: {} Evals/s: {} Moves: {} Pruned: {} Symmetry: {}".format(cev,cev/t1,cmv,cpr,sym))
       # else:

            #try:
            #    while True:
            #        (x,y) = input("Move: ").split()
            #        x = ord(x) - 97
            #        y = 8-int(y)
            #        mv = Move(x,y)
            #        if g.move_valid(mv, cp):
            #            break
            #except:
            #    mv = None

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