# Program to generate a random number between 0 and 9

# importing the random module
import pandas as pd
import time


start_time2 = time.time()
df = pd.read_csv('raw_signal_edited.csv',usecols=['A-B'], names=['A','B','A-B'])

start_time1 = time.time()

def send(k):
	start_time = time.time()
	a = df.iat[k,0]
	print("pd.read_csv took %s seconds" % (time.time() - start_time))
	print(a)
	return a



for x in range(10000):
	send(x)

print("this program took %s seconds as a whole" % (time.time() - start_time2))
print("pd.read_csv took %s seconds reading csv" % (start_time1 - start_time2))