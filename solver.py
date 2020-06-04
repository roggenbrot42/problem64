import time
import math as m
import numpy as np
from collections import Counter
import copy

def ip(c): #invert player
    if c == -1: 
        return 1
    elif c == 1: 
        return -1
    else: 
        return False

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
            return NotImplemented
        else:
            return (self.x,self.y)<=(other.x,other.y)

    def isValid(self):
        if self.x >= 0 and self.x <= 7 and self.y >= 0 and self.y <= 7:
            return True
        else:
            return False
    def __hash__(self):
        return self.x*16+self.y
 



class Game:
    def __init__(self):
        self.initialize_game()
    
    def initialize_game(self):
        self.game_state = np.zeros((8,8))
        self.game_state[3][3] = self.game_state[4][4] = -1
        self.game_state[3][4] = self.game_state[4][3] = 1

        self.structure = np.array([[16, -4, 4, 2, 2, 4, -4, 16],
                            [-4, 12, -2, -2 ,-2, -2, -12,-4],
                            [4, -2, 4, 2, 2, 4, -2, 4],
                            [2, -2, 2, 0, 0, 2, -2, 2],
                            [2, -2, 2, 0, 0, 2, -2, 2],
                            [4, -2, 4, 2, 2, 4, -2, 4],
                            [-4, 12, -2, -2 ,-2, -2, -12,-4],
                            [16, -4, 4, 2, 2, 4, -4, 16]])
        self.depth = 6
        self.counter = self.count()
        self.pruned = 0
        self.evals = 0
        self.moves = 0
        

    #TODO: Implement actual test
    def move_valid(self, move, player):
        if self.game_state[move.y][move.x] != 0:
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
                print('{}'.format(format_player(self.game_state[i][j])), end=" ")
            print()
        print("  A B C D E F G H")

    def test_moves(self, i, j, player):
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
                        if self.game_state[y][x] == ip(player):
                            nmoves += 1
                        else:
                            break
                    else:
                        nmoves = 0
                        break

                if nmoves >  0 and self.game_state[y][x] == 0:
                    if x < 0 or y < 0:
                        print("boink")
                    else:
                        retval.append(Move(x,y))

        return retval
    
    def next_moves(self,player):
        next_moves = []
        for i in range(0,8):
            for j in range(0,8):
                if(self.game_state[i][j] == player):
                    m = self.test_moves(i,j,player)
                    next_moves += m
        used = set()
        unique = [x for x in next_moves if x not in used and (used.add(x) or True)]
        return unique

    def make_move(self,player,move):
        flipstack = []
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
                        if self.game_state[y][x] == ip(player):
                            nmoves += 1
                        else:
                            break
                    else:
                        nmoves = 0
                        break

                if nmoves > 0 and self.game_state[y][x] == player:
                    x -= xinc
                    y -= yinc
                    while self.game_state[y][x] == ip(player):
                        flipstack.append(Move(x,y))
                        self.game_state[y][x] = player                      
                        x -= xinc
                        y -= yinc
        self.counter[player] += len(flipstack) + 1
        self.counter[ip(player)] -= len(flipstack)

        self.moves += 1
        return flipstack
    
    def undo_move(self,move,flipstack):
        i = move.y
        j = move.x

        player = self.game_state[i][j]
        self.counter[player] -= len(flipstack) - 1
        self.counter[ip(player)] += len(flipstack)
        self.game_state[i][j] = 0

        for f in flipstack:
            self.game_state[f.y][f.x] = ip(player)

    def outside_square(self):

        #Trivial case
        if sum(self.counter.values()) > 16:
            return True
        
        #search square around inner 4x4
        for i in [1,6]:
            for j in range(1,6):
                if self.game_state[i][j] != 0:
                    return True

        for j in [1, 6]:
            for i in range(2,5):
                if self.game_state[i][j] != 0:
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
        return structure_sum

    def eval(self,player,moves):
        self.evals += 1

        omoves = self.next_moves(ip(player))
        M = (len(moves)-len(omoves))*2
        S = self.eval_structure(player)

        A = self.counter[player] - self.counter[ip(player)]
     
        n = sum(self.counter.values())
        z = 0.035
        W = m.exp(-n*z)

        score = (M+S)*W + A*(1-W)
        return score

    
    def minimax(self, c, maxi, depth):
        moves = self.next_moves(c)

        #game is finished can't move anymore
        if len(moves) == 0 or depth == 0:
            return self.eval(c,moves)
        

        if maxi == True:
            value = -m.inf
            for mov in moves:
                s = self.make_move(c,mov)
                value = max(value,self.minimax(ip(c),not(maxi),depth-1))
                self.undo_move(mov,s)
            return value
        else:
            value = m.inf
            for mov in moves:
                s = self.make_move(c,mov)
                value = min(value, self.minimax(ip(c),maxi,depth-1))
                self.undo_move(mov,s)
            return value

    def alphabeta_max(self, c, depth, alpha, beta):
        moves = self.next_moves(c)
        if self.depth == depth and len(moves) == 1:
            return (m.inf, moves[0])

        if len(moves) == 0 or depth == 0:
            return (self.eval(c,moves),None)
        
        retmv = None      
        max_value = alpha
        for mov in moves:
            s = self.make_move(c,mov)
            value = self.alphabeta_min(ip(c),depth-1,max_value,beta)
            self.undo_move(mov,s)
            if value > max_value:
                max_value = value
                if depth == self.depth:
                    retmv = mov
                if max_value >= beta:
                    self.pruned += 1
                    break
        return (max_value,retmv)
    
    def alphabeta_min(self, c, depth, alpha, beta):
        moves = self.next_moves(c)
        if len(moves) == 0 or depth == 0:
            return self.eval(c,moves)

        min_value = beta
        for mov in moves:
            s = self.make_move(c,mov)
            (value,xxx) = self.alphabeta_max(ip(c),depth-1,alpha,min_value)
            self.undo_move(mov,s)
            if value < min_value:
                min_value = value
                if min_value <= alpha:
                    self.pruned += 1
                    break
        return min_value
    
def main():
    g = Game()
    g.draw_board()

    passing = 0
    cp = -1
    moves = []

    g.depth = 8
    passing = 0

    pm = None    

    while True:
        if cp == -1:
            t1 = time.time()
            (value,mv) = g.alphabeta_max(cp,g.depth,-m.inf,m.inf)
            t1 = time.time() - t1
            print(t1)
            print("Evals: {} Moves: {} Pruned: {}".format(g.evals,g.moves,g.pruned))
        else:
            try:
                while True:
                    (x,y) = input("Move: ").split()
                    x = ord(x) - 97
                    y = 8-int(y)
                    mv = Move(x,y)
                    if g.move_valid(mv, cp):
                        break
            except:
                mv = None

        if mv != None:
            g.make_move(cp,mv)
            moves.append(mv)
            g.draw_board()
            print(mv)
            passing = 0
        else:
            passing += 1

        if passing == 2:
            break

        cp = ip(cp)
    
    c = g.count()
    if c[-1] > c[1]:
        print("White won!")
    else:
        print("Black won!")

    for mov in moves:
        print(mov,end="")
    print()

if __name__ == "__main__":
    main()