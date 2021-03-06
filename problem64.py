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
        return (self.wstate | self.bstate) & ~self.square_mask > 0

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