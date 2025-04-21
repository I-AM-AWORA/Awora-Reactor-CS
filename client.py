# -- AWORA-FLX CLIENT ID: C1
# -- AWORA-FLX CLIENT Version: 1.0.0
import os
import json
import platform
import uuid
import argparse

SYSTEM_INFO_FILE = "system_info.json"

def get_system_info():
    """Sistem bilgilerini toplar."""
    system_info = {
        "platform": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "architecture": platform.machine(),
        "hostname": platform.node(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "uuid": str(uuid.uuid1())
    }
    return system_info

def load_system_info():
    """system_info.json dosyasını yükler."""
    try:
        with open(SYSTEM_INFO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        print("Uyarı: system_info.json dosyası geçerli bir JSON formatında değil.")
        return None

def save_system_info(info):
    """Sistem bilgilerini system_info.json dosyasına kaydeder."""
    try:
        with open(SYSTEM_INFO_FILE, "w", encoding="utf-8") as f:
            json.dump(info, f, indent=4)
        print(f"Sistem bilgileri '{SYSTEM_INFO_FILE}' dosyasına kaydedildi.")
    except IOError as e:
        print(f"Hata: Sistem bilgileri dosyaya yazılamadı: {e}")

def display_system_info(info):
    """Sistem bilgilerini ekrana yazdırır."""
    if info:
        print("\n--- Sistem Bilgileri ---")
        for key, value in info.items():
            print(f"{key}: {value}")
        print("-------------------------\n")
    else:
        print("Sistem bilgisi bulunamadı veya yüklenirken bir hata oluştu.")

def main():
    parser = argparse.ArgumentParser(description="Awora-FLX İstemci Uygulaması")
    parser.add_argument("action", choices=['info', 'show'], help="'info' sistem bilgisini kaydeder, 'show' kaydEdilmiş bilgiyi gösterir.")
    args = parser.parse_args()

    if args.action == 'info':
        system_info = get_system_info()
        save_system_info(system_info)
    elif args.action == 'show':
        loaded_info = load_system_info()
        display_system_info(loaded_info)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()