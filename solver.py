import time
import math as m

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
                            ['.','.','.','.','.','.','.','.'],
                            ['.','.','.','b','w','.','.','.'],
                            ['.','.','.','w','b','.','.','.'],
                            ['.','.','.','.','.','.','.','.'],
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
        self.nw = 2
        self.nb = 2
        self.outside_square = False

    def draw_board(self):
        for i in range(0,8):
            print(i, end=" ")
            for j in range(0,8):
                print('{}'.format(self.game_state[i][j]), end=" ")
            print()
        print("  A B C D E F G H")

    def test_horizontal(self, i, j, c):
        retval = []
        if j < 6:
            if self.game_state[i][j:j+3] == [c,ip(c),'.']:
                retval.append((i,j+2))
        if j > 1:
            if self.game_state[i][j-2:j+1] == ['.',ip(c),c]:
                retval.append((i,j-2))
        return retval

    def test_vertical(self, i, j, c):
        retval = []
        if i < 6:
            if self.game_state[i+1][j] == ip(c) and self.game_state[i+2][j] == '.':
                retval.append((i+2,j))
        if i > 1:
            if self.game_state[i-1][j] == ip(c) and self.game_state[i-2][j] == '.':
                retval.append((i-2,j))
        return retval

    def test_diagonal(self, i, j,c):
        retval = []
        if i < 6:
            if j<6 and self.game_state[i+1][j+1] == ip(c) and self.game_state[i+2][j+2] == '.':
                retval.append((i+2,j+2))
            if j > 1 and self.game_state[i+1][j-1] == ip(c) and self.game_state[i+2][j-2] == '.':
                retval.append((i+2,j-2))
        if i > 1:
            if j > 1 and self.game_state[i-1][j-1] == ip(c) and self.game_state[i-2][j-2] == '.':
                retval.append((i-2,j-2))    
            if j < 6 and self.game_state[i-1][j+1] == ip(c) and self.game_state[i-2][j+2] == '.':
                retval.append((i-2,j+2))
        return retval

    
    def next_moves(self,player):
        next_moves = []
        for i in range(0,8):
            for j in range(0,8):
                if(self.game_state[i][j] == player):
                    m = self.test_horizontal(i,j,player)
                    next_moves += m 
                    m = self.test_vertical(i,j,player)
                    next_moves += m
                    m = self.test_diagonal(i,j,player)
                    next_moves += m
        return next_moves
    
    
    def eval_structure(self,c):
        sum = 0
        for i in range(0,8):
            for j in range(0,8):
                if self.game_state[i][j] == '.':
                    continue
                if self.game_state[i][j] == c:
                    sum += self.structure[i][j]
                else:
                    sum -= self.structure[i][j]
        if self.outside_square == True:
            sum *= 3
        return sum


    def eval_material(self,player):
        if player == 'w':
            return self.nw - self.nb
        else:
            return self.nb - self.nw

    def eval(self,player,moves,omoves):
        M = (len(moves)-len(omoves))*2
        S = self.eval_structure(player)
        A = self.eval_material(player)
        n = self.nw + self.nb
        z = 0.035
        W = m.exp(-n*z)

        score = (M+S)*W + A*(1-W)
        return score

    def play(self):
        self.draw_board()
        
        start = time.time()
        moves = self.next_moves('b')

        for m in moves:
            self.game_state[m[0]][m[1]] = 'b'
            self.nb += 1
            a = self.next_moves('b')
            b = self.next_moves('w')
            res = self.eval('b',a,b)
            print("Eval: {}".format(res,7))
            

            self.game_state[m[0]][m[1]] = '.'
            self.nb -= 1
        end = time.time()
        print("Evaluation Time: {}s".format(end-start,7))

        

def main():
    g = Game()
    g.play()

if __name__ == "__main__":
    main()

#def eval_mobility(game)
    #number of moves available - number of moves available to opponent

#def eval_structure(game)
    #number of strategic positions occupied
    #has someone played outside the inner 4*4 square?
    #if yes, set inner 4*4 square to zero

#def eval_material(game)
    #number of pieces - opponent pieces 

#def score(game)