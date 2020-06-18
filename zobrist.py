# This module implements a zobrist hash based transposition table
from problem64 import Color, Board, Move
import sys
import numpy as np
import random
import json

class ZobristTable:
    key_table = np.zeros([64,3])
    exponent = 16
    map_size = 2**exponent
    map_mask = exponent-1

    tp_table = np.empty(map_size,dtype=object)

    def calc_keys(self):
        for i in range(0,64):
            for j in range(0,3):
                self.key_table[i][j] = random.randint(0,sys.maxsize)
    
    def save_to_file(self,filename):
        np.savez(filename,self.key_table,self.tp_table)

    def load_from_file(self,filename):
        try:
            npzfile = np.load(filename,allow_pickle=True)
            #TODO: we could also just save the seed and recalculate
            self.key_table = npzfile['arr_0']
            self.tp_table = npzfile['arr_1']
        except FileNotFoundError:
            print("Hash table not found, creating new one...")
            self.calc_keys()
        
    def __setitem__(self,key,value):
        #TODO: account for collisions
        index = int(key) & self.map_mask
        tmp = self.tp_table[index]
        if tmp == None:
            self.tp_table[index] = (key,value)
        elif isinstance(tmp,tuple): #TODO ignoring duplicates for now
            self.tp_table[index] = list()
            self.tp_table[index].append(tmp)
            self.tp_table[index].append((key,value))
        else: #list
            self.tp_table[index].append((key,value))

    def __getitem__(self,key):
        index = int(key) & self.map_mask
        item = self.tp_table[index]
        if isinstance(item,tuple):
            return item[1]
        else:
            for it in item:
                if it[0] == key:
                    return it[1]
            return None


        

    def get_key(self,move,color):
        return self.key_table[move.y*8+move.x][color]

    def hash_board(self,board):
        h = 0
        for i in range(0,64):
            if board[i] == Color.NONE:
                h ^= int(self.key_table[i][0])
            elif board[i] == Color.BLACK:
                h ^= int(self.key_table[i][1])
            else:
                board[i] == Color.WHITE
                h ^= int(self.key_table[i][2])
        return h

def main():
    z = ZobristTable()
    z.calc_keys()
    z.save_to_file("table.npz")
    print(z.key_table[33])
    z[z.key_table[33][2]] = (Move(1,1),3)
    print(z[z.key_table[33][2]])


if __name__ == "__main__":
    main()