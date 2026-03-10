import math
import time

try:
    with open("../data/random_numbers.txt", "r") as f:
        num = [int(line.strip()) for line in f]
except FileNotFoundError:
    print(f"Error file not found!")
    exit()

length = len(num)
n = 59

results_for_file = [math.factorial(m) for m in num]
# 100 ns
t0 = time.perf_counter()
for i in range(n):
    for m in num:
        pass
t1 = time.perf_counter()
empty_time = t1 - t0

t2 = time.perf_counter()
for i in range(n):
    for m in num:
        math.factorial(m)
t3 = time.perf_counter()
full_time = t3 - t2

delta_time = full_time - empty_time


with open("../result/math_factorial_report.txt", "w") as f:
    for res in results_for_file:
        f.write(f"{res}\n")

    f.write("\n" + "=" * 40 + "\n")
    f.write("PERFORMANCE REPORT: math.factorial (Original)\n")
    f.write("=" * 40 + "\n")
    f.write(f"Number of unique data entries: {length}\n")
    f.write(f"Number of repetitions (n): {n}\n")
    f.write(f"Total function executions: {length * n}\n")
    f.write("-" * 40 + "\n")
    f.write(f"Full time: {full_time:.6f} s\n")
    f.write(f"Empty loop time: {empty_time:.6f} s\n")
    f.write(f"Net function time: {delta_time:.6f} s\n")
    f.write(f"Average time per execution: {delta_time / (length * n):.12f} s\n")
    f.write("=" * 40 + "\n")
    timer_res = 1e-6
    rel_error = (timer_res / delta_time) * 100

    f.write("\n" + "=" * 40 + "\n")
    f.write("ERROR ANALYSIS (Requirement: < 1%)\n")
    f.write("=" * 40 + "\n")
    f.write(f"Assumed timer resolution: {timer_res:.1e} s\n")
    f.write(f"Net function time (T_net): {delta_time:.6f} s\n")
    f.write("-" * 40 + "\n")
    f.write(f"Calculation: ({timer_res:.1e} / {delta_time:.6f}) * 100%\n")
    f.write("-" * 40 + "\n")
    f.write(f"RELATIVE ERROR: {rel_error:.8f} %\n")

    if rel_error < 1.0:
        f.write("STATUS: COMPLIANT (Error is below 1%)\n")
    else:
        f.write("STATUS: NON-COMPLIANT (Increase 'n' to extend time)\n")
    f.write("=" * 40 + "\n")
print("Done!")
