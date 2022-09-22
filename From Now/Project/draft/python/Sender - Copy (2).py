# Program to generate a random number between 0 and 9

# importing the random module
import pandas as pd
import time

def send(k):
	start_time = time.time()
	df = pd.read_csv('raw_signal_edited.csv',skiprows=k, nrows=1, usecols=['A-B'], names=['A','B','A-B'])
	a = df.iat[0,0]
	print("pd.read_csv took %s seconds" % (time.time() - start_time))
	print(a)
	return a


start_time1 = time.time()
for x in range(10000):
	send(x)

print("pd.read_csv took %s seconds as a whole" % (time.time() - start_time1))
