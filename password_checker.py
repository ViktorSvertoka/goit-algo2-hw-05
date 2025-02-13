from bitarray import bitarray
import mmh3
from colorama import Fore, Style, init
from typing import List

init(autoreset=True)


class BloomFilter:
    def __init__(self, size: int, num_hashes: int):
        self.size = size
        self.num_hashes = num_hashes
        self.bit_array = bitarray(size)
        self.bit_array.setall(0)

    def add(self, item: str):
        for i in range(self.num_hashes):
            index = mmh3.hash(item, i) % self.size
            self.bit_array[index] = 1

    def contains(self, item: str) -> bool:
        return all(
            self.bit_array[mmh3.hash(item, i) % self.size]
            for i in range(self.num_hashes)
        )


def check_password_uniqueness(bloom: BloomFilter, passwords: List[str]) -> dict:
    results = {}
    for password in passwords:
        if bloom.contains(password):
            results[password] = f"{Fore.RED}вже використаний{Style.RESET_ALL}"
        else:
            results[password] = f"{Fore.GREEN}унікальний{Style.RESET_ALL}"
    return results


if __name__ == "__main__":
    bloom = BloomFilter(size=1000, num_hashes=3)

    existing_passwords = ["password123", "admin123", "qwerty123"]
    for password in existing_passwords:
        bloom.add(password)

    new_passwords_to_check = ["password123", "newpassword", "admin123", "guest"]
    results = check_password_uniqueness(bloom, new_passwords_to_check)

    print("\nРезультати перевірки паролів:")
    for password, status in results.items():
        print(f"{Fore.CYAN}Пароль '{password}' - {status}.")
