import pandas as pd
import importlib
import re

def read_files(input_file, ways_file):
    """
    input.txt ve ways.txt dosyalarını okur.

    Args:
        input_file (str): input.txt dosyasının adı.
        ways_file (str): ways.txt dosyasının adı.

    Returns:
        tuple: input.txt ve ways.txt dosyalarının içeriği (liste olarak).
    """
    with open(input_file, 'r') as f:
        input_data = f.readlines()
    with open(ways_file, 'r') as f:
        ways_data = f.readlines()
    return input_data, ways_data

def validate_data(input_data, ways_data):
    """
    input.txt verilerini ve ways.txt komutlarını doğrular.

    Args:
        input_data (list): input.txt dosyasının içeriği (liste olarak).
        ways_data (list): ways.txt dosyasının içeriği (liste olarak).

    Returns:
        bool: Veri doğrulama başarılıysa True, değilse False.
    """
    # input.txt veri doğrulama (basit bir örnek)
    if len(input_data) < 2:  # Başlık satırı ve en az 1 veri satırı olmalı
        print("Hata: input.txt dosyasında yeterli veri yok.")
        return False

    # ways.txt komut doğrulama (basit bir örnek)
    for line in ways_data:
        if not re.match(r'^(make|q|make ANH) .*', line.strip()):
            print(f"Hata: Geçersiz ways.txt komutu: {line.strip()}")
            return False

    return True

def process_ways(input_data, ways_data):
    """
    ways.txt dosyasındaki komutları işleyerek formülleri uygular.

    Args:
        input_data (list): input.txt dosyasının içeriği (liste olarak).
        ways_data (list): ways.txt dosyasının içeriği (liste olarak).

    Returns:
        dict: Hesaplanan skorları ve değişken değerlerini içeren bir sözlük.
    """

    results = {}
    input_header = input_data[0].strip().split('\t')
    input_values = input_data[1].strip().split('\t')

    data = dict(zip(input_header, input_values))

    for line in ways_data:
        line = line.strip()
        parts = line.split()
        command = parts[0]

        if command == 'make':
            skorlar = parts[1:]
            for skor in skorlar:
                module = importlib.import_module(f'formulas.{skor}_formula')
                calculate_func = getattr(module, f'calculate_{skor}')
                # Gerekli parametreleri input_data'dan al
                params = {}
                func_params = calculate_func.__code__.co_varnames
                for param in func_params:
                    if param in data:
                        params[param] = float(data[param])
                
                results[skor] = calculate_func(**params)

        elif command == 'q':
            variable, expression = parts[1], ' '.join(parts[2:])
            # Basit aritmetik işlemler için eval kullanıyoruz (dikkatli olun!)
            results[variable] = eval(expression, results)

        elif command == 'make' and parts[1] == 'ANH':
            variable, expression = parts[2], ' '.join(parts[3:])
            skor_agirlik_pairs = expression.split()
            skorlar = {}
            agirliklar = {}
            for pair in skor_agirlik_pairs:
                skor, agirlik = pair.split(':')
                skorlar[skor] = results.get(skor, 0)  # Skor yoksa 0 al
                agirliklar[skor] = float(agirlik)
            
            module = importlib.import_module('formulas.ANH_formula')
            calculate_ANH = getattr(module, 'calculate_ANH')
            results[variable] = calculate_ANH(skorlar, agirliklar)

    return results
def write_to_excel(results, output_file):
    """
    Hesaplanan sonuçları bir Excel dosyasına yazar.

    Args:
        results (dict): Hesaplanan skorları ve değişken değerlerini içeren bir sözlük.
        output_file (str): Çıktı Excel dosyasının adı.
    """
    df = pd.DataFrame(list(results.items()), columns=['Değişken', 'Değer'])
    df.to_excel(output_file, index=False)
    print(f"Sonuçlar {output_file} dosyasına yazıldı.")

def main():
    input_file = 'input.txt'
    ways_file = 'ways.txt'
    output_file = 'output.xlsx'

    input_data, ways_data = read_files(input_file, ways_file)

    if validate_data(input_data, ways_data):
        results = process_ways(input_data, ways_data)
        write_to_excel(results, output_file)
    else:
        print("Veri doğrulama başarısız, program sonlandırılıyor.")

if __name__ == "__main__":
    main()
