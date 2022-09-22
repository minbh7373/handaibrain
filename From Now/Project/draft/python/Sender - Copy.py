# Program to generate a random number between 0 and 9

# importing the random module
import pandas as pd

def send(k):
	df = pd.read_csv('raw_signal_edited.csv', names=['A','B','A-B'])
	a = df.iat[k,2]
	return a