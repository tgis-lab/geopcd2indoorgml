'''
Created on 2023年6月24日

@author: Zhiyong Wang
'''
import numpy as np

    
    
class Morton2D:
    # magicbit2D_masks64 = [0xFFFFFFFF, 0x0000FFFF, 0x00FF00FF, 0x0F0F0F0F, 0x33333333, 0x55555555];
    magicbit2D_masks64 = [0x00000000FFFFFFFF, 0x0000FFFF0000FFFF, 0x00FF00FF00FF00FF, 0x0F0F0F0F0F0F0F0F, 0x3333333333333333, 0x5555555555555555];

    # HELPER METHOD for Magic bits encoding - split by 2
    def splitBy2Bits(self, x):
        masks = Morton2D.magicbit2D_masks64
        x = np.int64(x)
        x = (x | x << 32) & masks[0]; 
        x = (x | x << 16) & masks[1];
        x = (x | x << 8)  & masks[2]; 
        x = (x | x << 4)  & masks[3];
        x = (x | x << 2)  & masks[4];
        x = (x | x << 1)  & masks[5];
        return x;
     

    # HELPER method for Magicbits decoding
    def getSecondBits(self, m):
        masks = Morton2D.magicbit2D_masks64
        x = m & masks[5];
        x = (x ^ (x >> 1))  & masks[4];
        x = (x ^ (x >> 2))  & masks[3];
        x = (x ^ (x >> 4))  & masks[2];
        x = (x ^ (x >> 8))  & masks[1];
        x = (x ^ (x >> 16)) & masks[0];
        return x;

    def magicbitCoding(self, l, b):
        return self.splitBy2Bits(l) | (self.splitBy2Bits(b) << 1);


    def magicbitDecoding(self, m):
        self.l = self.getSecondBits(m);
        self.b = self.getSecondBits(m >> 1);
 

