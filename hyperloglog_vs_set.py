import re
import time
import mmh3
import sys
from collections import defaultdict
from typing import Set
from dataclasses import dataclass
from rich.console import Console
from rich.table import Table


class HyperLogLog:
    """Реалізація алгоритму HyperLogLog для наближеного підрахунку унікальних елементів."""

    def __init__(self, b: int = 12):
        self.b = b
        self.m = 1 << b
        self.registers = [0] * self.m

    def add(self, item: str):
        hash_value = mmh3.hash_bytes(item)  # Отримуємо 128-бітне хеш-значення
        idx = int.from_bytes(hash_value[:4], "big") % self.m  # Індекс в регістрах
        w = int.from_bytes(hash_value[4:], "big")  # Інша частина хешу
        self.registers[idx] = max(self.registers[idx], self._rho(w))

    def count(self) -> int:
        """Оцінка кількості унікальних елементів."""
        Z = sum(2**-r for r in self.registers)
        alpha_m = 0.7213 / (1 + 1.079 / self.m)
        estimate = alpha_m * (self.m**2) / Z
        return int(estimate)

    @staticmethod
    def _rho(w: int) -> int:
        """Знаходження першого біта, який дорівнює 1."""
        return (w & -w).bit_length()


def load_ip_addresses(filename: str) -> Set[str]:
    """Завантаження IP-адрес з лог-файлу."""
    ip_set = set()
    ip_pattern = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

    with open(filename, "r", encoding="utf-8", errors="ignore") as file:
        for line in file:
            match = ip_pattern.search(line)
            if match:
                ip_set.add(match.group())

    return ip_set


def benchmark(filename: str):
    """Порівняння точного підрахунку та HyperLogLog."""

    console = Console()

    # Точний підрахунок
    start_time = time.time()
    exact_ips = load_ip_addresses(filename)
    exact_count = len(exact_ips)
    exact_time = time.time() - start_time

    # HyperLogLog
    hll = HyperLogLog()
    start_time = time.time()
    for ip in exact_ips:
        hll.add(ip)
    hll_count = hll.count()
    hll_time = time.time() - start_time

    # Вивід результатів
    table = Table(
        title="Результати порівняння", show_header=True, header_style="bold magenta"
    )
    table.add_column("", justify="left")
    table.add_column("Точний підрахунок", justify="right")
    table.add_column("HyperLogLog", justify="right")

    table.add_row("Унікальні елементи", f"{exact_count:,}", f"{hll_count:,}")
    table.add_row("Час виконання (сек.)", f"{exact_time:.5f}", f"{hll_time:.5f}")

    console.print(table)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Вкажіть шлях до файлу логів.")
        sys.exit(1)

    benchmark(sys.argv[1])
