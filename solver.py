import time
import math as m
from collections import Counter
import copy

def ip(c): #invert player
    if c == 'w': 
        return 'b'
    elif c == 'b': 
        return 'w'
    else: 
        return False
        

class Game:
    def __init__(self):
        self.initialize_game()
    
    def initialize_game(self):
        self.game_state = [['.','.','.','.','.','.','.','.'],
                            ['.','.','.','.','.','.','.','.'],
                            ['.','.','.','.','.','w','.','.'],
                            ['.','.','.','b','w','b','.','.'],
                            ['.','.','b','w','b','.','.','.'],
                            ['.','.','w','.','.','.','.','.'],
                            ['.','.','.','.','.','.','.','.'],
                            ['.','.','.','.','.','.','.','.']]
        self.structure = [[16, -4, 4, 2, 2, 4, -4, 16],
                            [-4, 12, -2, -2 ,-2, -2, -12,-4],
                            [4, -2, 4, 2, 2, 4, -2, 4],
                            [2, -2, 2, 0, 0, 2, -2, 2],
                            [2, -2, 2, 0, 0, 2, -2, 2],
                            [4, -2, 4, 2, 2, 4, -2, 4],
                            [-4, 12, -2, -2 ,-2, -2, -12,-4],
                            [16, -4, 4, 2, 2, 4, -4, 16]]
    def count(self):
        c = Counter(self.game_state[0])
        for i in range(1,8):
            c.update(Counter(self.game_state[i]))
        return c
       

    def draw_board(self):
        for i in range(0,8):
            print(i, end=" ")
            for j in range(0,8):
                print('{}'.format(self.game_state[i][j]), end=" ")
            print()
        print("  A B C D E F G H")

    def test_horizontal(self, i, j, c):
        retval = []
        if j < 6 and self.game_state[i][j+1] == c:
            k = j+2
            while k<7 and self.game_state[i][k] == c:
                k += 1
            if self.game_state[i][k] == '.':
                retval.append((i,k))
        if j > 1 and self.game_state[i][j-1] == c:
            k = j-2
            while k > 0 and self.game_state[i][k] == c:
                k -= 1
            if self.game_state[i][k] == '.':
                retval.append((i,k))
        return retval

    def test_vertical(self, i, j, c):
        retval = []
        if i < 6 and self.game_state[i+1][j] == c:
            k = i+2
            while k<8 and self.game_state[k][j] == c:
                k += 1
            if self.game_state[k][j] == '.':
                retval.append((k,j))
        if i > 1 and self.game_state[i-1][j] == c:
            k = i-2
            while k>0 and self.game_state[k][j] == c:
                k -= 1
            if self.game_state[k][j] == '.':
                retval.append((k,j))
        return retval

    def test_diagonal(self, i, j,c):
        retval = []
        if i < 6:
            if j<6 and self.game_state[i+1][j+1] == c:
                k = i+2
                l = j+2
                while k<8 and l<8 and self.game_state[k][l] == c:
                    k += 1
                    l += 1
                if self.game_state[k][l] == '.':
                    retval.append((k,l))
            if j > 1 and self.game_state[i+1][j-1] == c:
                k = i+2
                l = j-2
                while k < 8 and l > 0 and self.game_state[k][l] == c:
                    k += 1
                    l -= 1
                if self.game_state[k][l] == '.':
                    retval.append((k,l))
        if i > 1:
            if j > 1 and self.game_state[i-1][j-1] == c:
                k = i-2
                l = j-2
                while k > 0 and i > 0 and self.game_state[k][l] == c:
                    k -= 1
                    l -= 1
                if self.game_state[k][l] == '.':
                    retval.append((i-2,j-2))    
            if j < 6 and self.game_state[i-1][j+1] == c:
                k = i-2
                l = j+2
                while k > 0 and l < 8 and self.game_state[k][l] == c:
                    k -= 1
                    l += 1
                if self.game_state[k][l] == '.':
                    retval.append((i-2,j+2))
        return retval

    def test_moves(self, i, j, player):
        retval = []
        for xinc in range(-1,2):
            for yinc in range(-1,2):
                if xinc == 0 and yinc == 0:
                    continue
                x = i
                y = j
                nmoves = 0

                while True:
                    x += xinc
                    y += yinc
                    if x>=0 and y>=0 and x<=7 and y<=7:
                        if self.game_state[x][y] == ip(player):
                            nmoves += 1
                        else:
                            break
                    else:
                        nmoves = 0
                        break

                if nmoves >  0 and self.game_state[x][y] == '.':
                    if x < 0 or y < 0:
                        print("boink")
                    retval.append((x,y))

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
        i = move[0]
        j = move[1]

        self.game_state[i][j] = player

        for xinc in range(-1,2):
            for yinc in range(-1,2):
                if xinc == 0 and yinc ==0:
                    continue
                x = i+xinc
                y = j+yinc
                nmoves = 0

                try:
                    while self.game_state[x][y] == ip(player):
                        x += xinc
                        y += yinc
                        nmoves += 1

                    if nmoves > 0 and self.game_state[x][y] == player:
                        x -= xinc
                        y -= yinc
                        while self.game_state[x][y] == ip(player):
                            flipstack.append((x,y))
                            self.game_state[x][y] = player
                            x -= xinc
                            y -= yinc
                except:
                    continue
        return flipstack
    
    def undo_move(self,move,flipstack):
        i = move[0]
        j = move[1]

        self.game_state[i][j] = '.'

        for f in flipstack:
            self.game_state[f[0]][f[1]] = ip(self.game_state[f[0]][f[1]])

    
    def eval_structure(self,c):
        sum = 0
        outside_square = False
       
        for i in range(0,8):
            for j in range(0,8):
                    if i > 1 and i < 6 and j > 1 and j < 6 and self.game_state[i][j] != '.':
                        outside_square == True

        for i in range(0,8):
            for j in range(0,8):
                if outside_square == True and i > 1 and i < 6 and j > 1 and j < 6:
                    continue
                elif self.game_state[i][j] == '.':
                    continue
                elif self.game_state[i][j] == c:
                    sum += self.structure[i][j]
                else:
                    sum -= self.structure[i][j]
        if outside_square == True:
            sum *= 3
        return sum

    def eval(self,player,moves,omoves):
        c = self.count()

        M = (len(moves)-len(omoves))*2
        S = self.eval_structure(player)

        if player == 'w':
            A = c['w'] - c['b']
        else:
            A = c['b'] - c['w']
        
        n = c['w'] + c['b']
        z = 0.035
        W = m.exp(-n*z)

        score = (M+S)*W + A*(1-W)
        return score

    
    def minimax(self, c, maxi, depth):
        moves = self.next_moves(c)
        omoves = self.next_moves(ip(c))

        #game is finished can't move anymore
        if len(moves) == 0 and len(omoves) == 0\
            or depth == 0:
            return self.eval(c,moves,omoves)
        

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
    
    def alphabeta(self, c, maxi, depth, alpha, beta):
        moves = self.next_moves(c)
        omoves = self.next_moves(ip(c))

        #game is finished can't move anymore
        if len(moves) == 0 and len(omoves) == 0\
            or depth == 0:
            return self.eval(c,moves,omoves)
        

        if maxi == True:
            value = -m.inf
            for mov in moves:
                s = self.make_move(c,mov)
                value = max(value,self.alphabeta(ip(c),not(maxi),depth-1,alpha,beta))
                alpha = max(alpha, value)
                self.undo_move(mov,s)
                if alpha >= beta:
                    break
            return value
        else:
            value = m.inf
            for mov in moves:
                s = self.make_move(c,mov)
                value = min(value, self.alphabeta(ip(c),maxi,depth-1,alpha,beta))
                beta = min(beta, value)
                self.undo_move(mov,s)
                if alpha >= beta:
                    break
            return value

def main():
    g = Game()
    g.draw_board()

    passing = 0
    cp = 'b'
    moves = []

    while True:
        
        mvs = g.next_moves(cp)
        #print(mvs)

        if len(mvs) == 0:
            cp = ip(cp)
            passing += 1
            if passing == 2:
                break
            else:
                continue

        passing = 0
        
        bm = (-1,-1)
        bv = -m.inf
        for mv in mvs:
            s = g.make_move(cp,mv)
            nv = g.alphabeta(ip(cp),False,12,m.inf,-m.inf)
            g.undo_move(mv,s)
            if nv > bv:
                bm = mv
                bv = nv
        g.make_move(cp,bm)
        moves.append(bm)
        
        cp = ip(cp)

    g.draw_board()

    c = g.count()
    if c['w'] > c['b']:
        print("White won!")
    else:
        print("Black won!")

    for mov in moves:
        letter = chr(mov[0]+97)
        number = 8-mov[1]
        print("{}{}".format(letter,number),end="")
    print()

if __name__ == "__main__":
    main()