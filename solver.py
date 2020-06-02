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
        self.depth = 4

    def count(self):
        c = Counter(self.game_state[0])
        for i in range(1,8):
            c.update(Counter(self.game_state[i]))
        return c
       

    def draw_board(self):
        for i in range(0,8):
            print(8-i, end=" ")
            for j in range(0,8):
                print('{}'.format(self.game_state[i][j]), end=" ")
            print()
        print("  A B C D E F G H")

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
                if not(i > 1 and i < 6 and j > 1 and j < 6) and self.game_state[i][j] != '.':
                    outside_square == True
                    break
            if outside_square == True:
                break

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

    def eval(self,player,moves):
        c = self.count()
        omoves = self.next_moves(ip(c))
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
    
    def alphabeta(self, c, maxi, depth, alpha, beta):
        moves = self.next_moves(c)
        retmv = None
        
        #game is finished can't move anymore
        if len(moves) == 0 or depth == 0:
            return (self.eval(c,moves),retmv)
        
        if maxi == True:
            max_value = -m.inf
            for mov in moves:
                s = self.make_move(c,mov)
                (value,xxx) = self.alphabeta(ip(c),False,depth-1,max_value,beta)
                self.undo_move(mov,s)
                if value > max_value:
                    max_value = value
                    if depth == self.depth:
                        retmv = mov
                    if max_value >= beta:
                        break
            return (value,retmv)
        else:
            min_value = m.inf
            for mov in moves:
                s = self.make_move(c,mov)
                (value,xxx) = self.alphabeta(ip(c),True,depth-1,alpha,min_value)
                self.undo_move(mov,s)
                if value < min_value:
                    min_value = value
                    if min_value <= alpha:
                        break
            return (value,None)

def main():
    g = Game()
    g.draw_board()

    passing = 0
    cp = 'b'
    moves = []

    g.depth = 10
    passing = 0

    for i in range(0,12):
        try:
            
            (value,mv) = g.alphabeta(cp,True,g.depth,m.inf,-m.inf)

            if mv != None:
                g.make_move(cp,mv)
                moves.append(mv)
                g.draw_board()
                passing = 0
            else:
                passing += 1

            if passing == 2:
                break

            cp = ip(cp)
        except KeyboardInterrupt:
            break
    
    c = g.count()
    if c['w'] > c['b']:
        print("White won!")
    else:
        print("Black won!")

    for mov in moves:
        letter = chr(mov[1]+97)
        number = 8-mov[0]
        print("{}{}".format(letter,number),end="")
    print()

if __name__ == "__main__":
    main()