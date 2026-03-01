import random

file_name = "../random_numbers.txt"
min = 0
max = 20
count = 10000

def generate():
    with open(file_name, "w") as f:
        for _ in range(count):
            num = random.randint(min, max)
            f.write(f"{num}\n")
    print(f"Successfully generated {count} random numbers to {file_name}.")

if __name__ == "__main__":
    generate()