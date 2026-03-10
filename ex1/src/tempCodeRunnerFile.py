import math
import time

try:
    with open("../data/random_numbers.txt", "r") as f:
        num = [int(line.strip()) for line in f]
except FileNotFoundError:
    print(f"Error file not found!")
    exit()
