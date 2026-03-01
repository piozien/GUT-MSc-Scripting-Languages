#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <chrono>
#include <iomanip>
#include <cstdint>

uint64_t my_factorial(int32_t k) {
    if (k < 0) return 0;
    uint64_t res = 1;
    for (int32_t j = 2; j <= k; ++j) {
        res *= j;
    }
    return res;
}

int main() {
    std::vector<int64_t> num;
    std::ifstream input_file("../../data/random_numbers.txt");
    if (!input_file.is_open()) {
        std::cerr << "Error file not found!" << std::endl;
        return 1;
    }

    int64_t val;
    while (input_file >> val) {
        num.push_back(val);
    }
    input_file.close();

    size_t length = num.size();
    int64_t n = 10000;

    std::vector<uint64_t> results_for_file;
    for (int32_t m : num) {
        results_for_file.push_back(my_factorial(m));
    }

    auto t0 = std::chrono::high_resolution_clock::now();
    for (int64_t i = 0; i < n; ++i) {
        for (int32_t m : num) {
        }
    }
    auto t1 = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> empty_diff = t1 - t0;
    double empty_time = empty_diff.count();

    volatile uint64_t prevent_optimization;

    auto t2 = std::chrono::high_resolution_clock::now();
    for (int64_t i = 0; i < n; ++i) {
        for (int32_t m : num) {
            prevent_optimization = my_factorial(m);
        }
    }
    auto t3 = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> full_diff = t3 - t2;
    double full_time = full_diff.count();

    double delta_time = full_time - empty_time;

    std::ofstream report_file("../../result/cpp_factorial_report.txt");

    for (uint64_t res : results_for_file) {
        report_file << res << "\n";
    }

    report_file << "\n" << std::string(40, '=') << "\n";
    report_file << "PERFORMANCE REPORT: factorial (C++ implementation)\n";
    report_file << std::string(40, '=') << "\n";
    report_file << "Number of unique data entries: " << length << "\n";
    report_file << "Number of repetitions (n): " << n << "\n";
    report_file << "Total function executions: " << (int64_t)length * n << "\n";
    report_file << std::string(40, '-') << "\n";
    report_file << std::fixed << std::setprecision(6);
    report_file << "Full time: " << full_time << " s\n";
    report_file << "Empty loop time: " << empty_time << " s\n";
    report_file << "Net function time: " << delta_time << " s\n";
    report_file << std::setprecision(12);
    report_file << "Average time per execution: " << delta_time / (double)(length * n) << " s\n";
    report_file << std::string(40, '=') << "\n";

    report_file.close();
    std::cout << "Done!" << std::endl;

    return 0;
}