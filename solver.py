import time
import math as m
import numpy as np
from collections import Counter
import copy

class Color:
    @staticmethod
    def ip(c): #invert color
        return -c
    
    none = 0
    white = -1
    black = 1
    @staticmethod
    def format_player(c):
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
    



class Game:
    def __init__(self):
        self.initialize_game()
    
    def initialize_game(self):
        self.game_state = np.zeros((8,8))
        self.game_state[3][3] = self.game_state[4][4] = Color.black
        self.game_state[3][4] = self.game_state[4][3] = Color.white

        self.depth = 12
        self.counter = self.count()
        self.pruned = 0
        self.evals = 0
        self.moves = 0
        self.current_player = Color.black
        self.flipstack = Stack(3000)
    
    structure = np.array([[16, -4, 4, 2, 2, 4, -4, 16],
                            [-4, 12, -2, -2 ,-2, -2, -12,-4],
                            [4, -2, 4, 2, 2, 4, -2, 4],
                            [2, -2, 2, 0, 0, 2, -2, 2],
                            [2, -2, 2, 0, 0, 2, -2, 2],
                            [4, -2, 4, 2, 2, 4, -2, 4],
                            [-4, 12, -2, -2 ,-2, -2, -12,-4],
                            [16, -4, 4, 2, 2, 4, -4, 16]])
        

    #TODO: Implement actual test
    def move_valid(self, move, player):
        if self.game_state[move.y][move.x] != Color.none:
            return False
        return True

    def count(self):
        c = Counter(self.game_state[0])
        for i in range(1,8):
            c.update(Counter(self.game_state[i]))
        return c
       

    def draw_board(self):
        for i in range(0,8):
            print(8-i, end=" ")
            for j in range(0,8):
                print('{}'.format(Color.format_player(self.game_state[i][j])), end=" ")
            print()
        print("  A B C D E F G H")

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
                        if self.game_state[y][x] == Color.ip(player):
                            nmoves += 1
                        else:
                            break
                    else:
                        nmoves = 0
                        break

                if nmoves >  0 and self.game_state[y][x] == Color.none:
                    if x < 0 or y < 0:
                        print("boink")
                    else:
                        retval.append(Move(x,y))

        return retval
    
    #TODO: this function is too slow
    def next_moves(self,player):
        next_moves = []

        if self.outside_square() == False:
            rmin = 1
            rmax = 7
        else:
            rmin = 0
            rmax = 8

        for i in range(rmin,rmax):
            for j in range(rmin,rmax):
                if(self.game_state[i][j] == player):
                    m = self.test_move(i,j,player)
                    next_moves += m
        used = set()
        unique = [x for x in next_moves if x not in used and (used.add(x) or True)]
        return unique

    def make_move(self,player,move):
        flipped = 0
        i = move.y
        j = move.x

        self.game_state[i][j] = player

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
                        if self.game_state[y][x] == Color.ip(player):
                            nmoves += 1
                        else:
                            break
                    else:
                        nmoves = 0
                        break

                if nmoves > 0 and self.game_state[y][x] == player:
                    x -= xinc
                    y -= yinc
                    while self.game_state[y][x] == Color.ip(player):
                        self.flipstack.push(y,x)
                        flipped += 1
                        self.game_state[y][x] = player                      
                        x -= xinc
                        y -= yinc
        self.counter[player] += flipped + 1
        self.counter[Color.ip(player)] -= flipped

        self.moves += 1
        return flipped
    
    def undo_move(self,move,flipped):
        i = move.y
        j = move.x

        player = self.game_state[i][j]
        self.counter[player] -=  flipped + 1
        self.counter[Color.ip(player)] += flipped
        self.game_state[i][j] = Color.none

        for i in range(0,flipped):
            (y,x) = self.flipstack.pop()
            self.game_state[y][x] = Color.ip(player)

    def outside_square(self):
        #Trivial case
        if self.counter[Color.none] >= 48:
            return True
        
        #search square around inner 4x4
        for i in [1,6]:
            for j in range(1,6):
                if self.game_state[i][j] != Color.none:
                    return True

        for j in [1, 6]:
            for i in range(2,5):
                if self.game_state[i][j] != Color.none:
                    return True
        #Nothing
        return False
    
    def eval_structure(self,c):
        structure_sum = 0
        outside_square = self.outside_square()

        structure_sum = sum(sum(np.matmul(self.game_state,self.structure)))

        #assume outside square
        if outside_square == False:
            diff = sum(sum(np.matmul(self.game_state[2:6][2:6],self.structure[2:6][2:6])))
            structure_sum -= diff
        else:
            structure_sum *= 3
        return c*structure_sum

    def eval(self):
        self.evals += 1

        omoves = self.next_moves(-self.current_player)
        moves = self.next_moves(self.current_player)

        M = (len(moves)-len(omoves))*2
        S = self.eval_structure(self.current_player)
        A = self.counter[self.current_player] - self.counter[-self.current_player]
     
        n = self.counter[Color.white]+self.counter[Color.black]
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
            value = self.minimax_min(Color.ip(c),depth-1)
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
            (value,xxx) = self.minimax_max(Color.ip(c),depth-1)
            min_value = min(min_value, value)
            self.undo_move(mov,s)
        return value

    def alphabeta_max(self, depth, alpha, beta):
        moves = self.next_moves(self.current_player)
        if self.depth == depth and len(moves) == 1:
            return (m.inf, moves[0])

        if len(moves) == 0 or depth == 0:
            return (self.eval(),None)
        
        retmov = None      
        max_value = alpha
        for mov in moves:
            s = self.make_move(self.current_player,mov)
            value = self.alphabeta_min(depth-1,max_value,beta)
            self.undo_move(mov,s)
            if value > max_value:
                max_value = value
                if depth == self.depth:
                    retmov = mov
                if max_value >= beta:
                    self.pruned += 1
                    break
            #samesies but use the alphabetically lower version
            if value == max_value and mov and mov < retmov:
                retmov = mov                

        return (max_value,retmov)
    
    def alphabeta_min(self, depth, alpha, beta):
        moves = self.next_moves(Color.ip(self.current_player))
        if len(moves) == 0 or depth == 0:
            return self.eval()

        min_value = beta
        for mov in moves:
            s = self.make_move(-self.current_player,mov)
            (value,xxx) = self.alphabeta_max(depth-1,alpha,min_value)
            self.undo_move(mov,s)
            if value < min_value:
                min_value = value
                if min_value <= alpha:
                    self.pruned += 1
                    break
        return min_value
    
def main():
    g = Game()

    passing = 0
    moves = []

    g.depth = 7
    passing = 0

    pm = None

    g.game_state[2][5] = Color.white
    g.game_state[3][5] = Color.black
    g.game_state[4][2] = Color.black
    g.game_state[5][2] = Color.white

    g.draw_board()


    g.counter = g.count()


    while True:
        #if cp == Color.black:
        cev = g.evals
        cmv = g.moves
        cpr = g.pruned
        t1 = time.time()
        (value,mv) = g.alphabeta_max(g.depth,-m.inf,m.inf)
        #(value,mv) = g.minimax_max(cp,g.depth)
        t1 = time.time() - t1
        print("Time: {}s".format(t1))
        cev = g.evals - cev
        cmv = g.moves - cmv
        cpr = g.pruned - cpr
        print("Evals: {} Evals/s: {} Moves: {} Pruned: {}".format(cev,cev/t1,cmv,cpr))
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
            print("Color: {} Move: {} Value: {:0.9f}".format(Color.format_player(g.current_player),mv,value))
            passing = 0
        else:
            passing += 1
            print("Color: {}".format(Color.format_player(g.current_player)))
        if passing == 2:
            break

        g.current_player = -g.current_player
    
    c = g.count()
    if c[Color.white] > c[Color.black]:
        print("White won!")
    else:
        print("Black won!")

    for mov in moves:
        print(mov,end="")
    print()

if __name__ == "__main__":
    main()