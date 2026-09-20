import os
import math
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Алфавіт: 33 (укр) * 2 + 26 (англ) * 2 + 10 (цифри) + 9 (символи) = 137 символів (просте число)
ALPHABET = "АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯабвгґдеєжзиіїйклмнопрстуфхцчшщьюяABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz 0123456789.,!?-\':;"
MOD = len(ALPHABET)

# ==========================================
# ДОПОМІЖНІ ФУНКЦІЇ ДЛЯ МАТРИЦЬ (ШИФР ХІЛЛА)
# ==========================================

def get_minor(matrix, i, j):
    """Повертає мінор матриці без i-го рядка та j-го стовпця."""
    return [row[:j] + row[j+1:] for row in (matrix[:i] + matrix[i+1:])]

def get_determinant(matrix):
    """Рекурсивне обчислення детермінанта квадратної матриці."""
    n = len(matrix)
    if n == 1:
        return matrix[0][0]
    if n == 2:
        return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    
    det = 0
    for c in range(n):
        det += ((-1) ** c) * matrix[0][c] * get_determinant(get_minor(matrix, 0, c))
    return det

def mod_inverse(a, m):
    """Знаходження оберненого елемента за модулем m."""
    a = a % m
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return -1

def get_matrix_inverse_mod(matrix, m):
    """Знаходження оберненої матриці за модулем m."""
    det = get_determinant(matrix)
    det_inv = mod_inverse(det, m)
    
    if det_inv == -1:
        raise ValueError("Детермінант і модуль не взаємно прості. Оберненої матриці не існує.")
    
    n = len(matrix)
    # Якщо матриця 1x1
    if n == 1:
        return [[det_inv % m]]
        
    adjugate = []
    for i in range(n):
        adjugate_row = []
        for j in range(n):
            minor = get_minor(matrix, i, j)
            cofactor = ((-1) ** (i + j)) * get_determinant(minor)
            adjugate_row.append(cofactor)
        adjugate.append(adjugate_row)
    
    # Транспонування (Adjugate -> класична приєднана матриця) та множення на det_inv
    inverse = []
    for i in range(n):
        inv_row = []
        for j in range(n):
            val = (adjugate[j][i] * det_inv) % m
            inv_row.append(val)
        inverse.append(inv_row)
    return inverse

# ==========================================
# ЗАВДАННЯ 1: ШИФР ГРОНСФЕЛЬДА
# ==========================================

def gronsfeld_encrypt(text, key):
    key_shifts = [int(k) for k in str(key)]
    encrypted = ""
    for i, char in enumerate(text):
        if char in ALPHABET:
            char_idx = ALPHABET.index(char)
            shift = key_shifts[i % len(key_shifts)]
            new_idx = (char_idx + shift) % MOD
            encrypted += ALPHABET[new_idx]
        else:
            encrypted += char # Пропускаємо невідомі символи
    return encrypted

def gronsfeld_decrypt(text, key):
    key_shifts = [int(k) for k in str(key)]
    decrypted = ""
    for i, char in enumerate(text):
        if char in ALPHABET:
            char_idx = ALPHABET.index(char)
            shift = key_shifts[i % len(key_shifts)]
            new_idx = (char_idx - shift) % MOD
            decrypted += ALPHABET[new_idx]
        else:
            decrypted += char
    return decrypted

def task1_gronsfeld():
    print("\n--- ЗАВДАННЯ 1: ШИФР ГРОНСФЕЛЬДА ---")
    input_file = "gronsfeld_input.txt"
    enc_file = "gronsfeld_encrypted.txt"
    
    # Створення тестового файлу, якщо не існує
    if not os.path.exists(input_file):
        with open(input_file, "w", encoding="utf-8") as f:
            f.write("Секретне повідомлення для шифру Гронсфельда 123.")
            
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()
        
    print(f"Зчитано текст з {input_file}: {text}")
    
    while True:
        key = input("Введіть числовий ключ для шифру Гронсфельда (наприклад, 2015): ")
        if key.isdigit():
            break
        print("Ключ повинен складатися лише з цифр!")
        
    # Шифрування
    encrypted_text = gronsfeld_encrypt(text, key)
    with open(enc_file, "w", encoding="utf-8") as f:
        f.write(encrypted_text)
    print(f"Зашифрований текст збережено у файл {enc_file}")
    
    # Розшифрування
    with open(enc_file, "r", encoding="utf-8") as f:
        text_to_decrypt = f.read()
        
    decrypted_text = gronsfeld_decrypt(text_to_decrypt, key)
    print(f"\nРозшифрований текст з файлу {enc_file}:")
    print(decrypted_text)

# ==========================================
# ЗАВДАННЯ 2: ШИФР ХІЛЛА
# ==========================================

def generate_key_matrix(keyword):
    # Фільтруємо символи ключа, щоб вони були в алфавіті
    valid_chars = [c for c in keyword if c in ALPHABET]
    if len(valid_chars) < 9:
        raise ValueError("Ключове слово повинно містити щонайменше 9 дійсних символів.")
        
    n = int(math.isqrt(len(valid_chars)))
    matrix = []
    idx = 0
    for i in range(n):
        row = []
        for j in range(n):
            row.append(ALPHABET.index(valid_chars[idx]))
            idx += 1
        matrix.append(row)
    return matrix, n

def hill_encrypt_decrypt(text, matrix, n, is_decrypt=False):
    # Фільтрація тексту
    filtered_text = "".join([c for c in text if c in ALPHABET])
    
    # Доповнення тексту до кратності n
    padding_len = (n - len(filtered_text) % n) % n
    filtered_text += ALPHABET[0] * padding_len 
    
    result = ""
    
    # Робота з блоками (вектор-рядок множиться на матрицю)
    for i in range(0, len(filtered_text), n):
        block = [ALPHABET.index(c) for c in filtered_text[i:i+n]]
        for col in range(n):
            val = 0
            for row in range(n):
                val += block[row] * matrix[row][col]
            result += ALPHABET[val % MOD]
            
    return result

def task2_hill():
    print("\n--- ЗАВДАННЯ 2: ШИФР ХІЛЛА ---")
    input_file = "hill_input.txt"
    enc_file = "hill_encrypted.txt"
    dec_file = "hill_decrypted.txt"
    
    if not os.path.exists(input_file):
        with open(input_file, "w", encoding="utf-8") as f:
            f.write("Секретне повідомлення для алгоритму Хілла")
            
    with open(input_file, "r", encoding="utf-8") as f:
        open_text = f.read()
    print(f"Зчитано текст з {input_file}: {open_text}")
    
    # 1. Запит ключового слова та генерування матриці
    matrix = None
    n = 0
    while not matrix:
        keyword = input("Введіть ключове слово для Хілла (9 і більше літер): ")
        try:
            temp_matrix, temp_n = generate_key_matrix(keyword)
            # Перевірка детермінанта
            det = get_determinant(temp_matrix) % MOD
            if det == 0:
                print("Детермінант матриці дорівнює нулю за модулем. Оберіть інше ключове слово.")
                continue
            
            # Перевірка існування оберненої (з простим модулем 137 це завжди так для det != 0)
            if mod_inverse(det, MOD) == -1:
                print("Детермінант ключа і довжина алфавіту не є взаємно простими. Оберіть інше ключове слово.")
                continue
            
            matrix = temp_matrix
            n = temp_n
        except Exception as e:
            print(f"Помилка: {e}")
            
    print(f"\nКлюч-матриця ({n}x{n}):")
    for row in matrix:
        print(row)
        
    # 2. Шифрування
    encrypted_text = hill_encrypt_decrypt(open_text, matrix, n, is_decrypt=False)
    with open(enc_file, "w", encoding="utf-8") as f:
        f.write(encrypted_text)
    print(f"\nЗашифрований текст збережено у файл {enc_file}")
    
    # 3. Розшифрування
    print("\n--- Система розшифровування Хілла ---")
    with open(enc_file, "r", encoding="utf-8") as f:
        cipher_text = f.read()
        
    decrypt_matrix = None
    while not decrypt_matrix:
        keyword = input("Введіть ключове слово для розшифрування: ")
        try:
            temp_matrix, temp_n = generate_key_matrix(keyword)
            inv_matrix = get_matrix_inverse_mod(temp_matrix, MOD)
            decrypt_matrix = inv_matrix
            n = temp_n
        except Exception as e:
            print(f"Помилка генерації оберненої матриці: {e}")
            
    decrypted_text = hill_encrypt_decrypt(cipher_text, decrypt_matrix, n, is_decrypt=True)
    
    with open(dec_file, "w", encoding="utf-8") as f:
        f.write(decrypted_text)
        
    print(f"Розшифрований текст збережено у файл {dec_file}")
    print(f"Результат розшифрування:\n{decrypted_text}")

if __name__ == "__main__":
    task1_gronsfeld()
    task2_hill()