# importing modules
import random
import time

def send():
	start = time.perf_counter()
	while time.perf_counter() - start < 3:
		random_number = random.randint(0,100)
		yield random_number
