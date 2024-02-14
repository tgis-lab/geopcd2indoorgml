'''
Created on 2023年7月6日

@author: Administrator
'''
## test
print("3<<2 = ",3<<2)
print("3>>1 = ",3>>1)
print("oxFF = ",0xFF) # 0x = hexadecimal
print(max(4,55))

signed_int = -2451337
print(signed_int)
unsigned_int = signed_int + 2**32 # Convert to unsigned integer
print(unsigned_int)

print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
seconds = 50.60
S = seconds +  2**32;
print(2**32, S, seconds - S)
dotSeconds = (seconds - S) * 2048;
print(dotSeconds)
S11 = round(dotSeconds) +  2**32;
print(round(dotSeconds), S11)