"""
data_reader.py

Veri dosyalarını okuyan fonksiyonlar.
"""

import json
from typing import Dict, Any


def read_data(file_path: str) -> Dict[str, Any]:
    """
    Belirtilen JSON dosyasından verileri okur.

    Args:
        file_path: Okunacak JSON dosyasının yolu.

    Returns:
        Okunan verileri içeren bir sözlük.
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        raise FileNotFoundError(f"Veri dosyası bulunamadı: {file_path}")
    except json.JSONDecodeError:
        raise json.JSONDecodeError(f"Geçersiz JSON formatı: {file_path}", '', 0)


# İleride farklı veri formatları için fonksiyonlar eklenebilir (örn. read_csv, read_txt)