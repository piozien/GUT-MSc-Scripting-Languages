import random

file_name = "../data/random_numbers.txt"
min = 0
max = 20
count = 10000

def generate_random():
    with open(file_name, "w") as f:
        for _ in range(count):
            num = random.randint(min, max)
            f.write(f"{num}\n")
    print(f"Successfully generated {count} random numbers to {file_name}.")

def generate_20():
    with open(file_name, "w") as f:
        for i in range(max+1):
            f.write(f"{i}\n")
    print(f"Successfully generated {max} random numbers to {file_name}.")

if __name__ == "__main__":
    #generate_random()
    generate_20()