# -- AWORA-FLX CLIENT ID: C1
# -- AWORA-FLX CLIENT Version: 1.0.0
import os
import re
import argparse
import json
import importlib.util
import sys

# Sabitler
INFO_PREFIXES = {
    "CLIENT": "# -- AWORA-FLX CLIENT ID: ",
    "CLIENT_VERSION": "# -- AWORA-FLX CLIENT Version: ",
    "CORE_ID": "# -- AWORA-FLX CORE ID: ",
    "CORE_VERSION": "# -- AWORA-FLX CORE Version: ",
    "COMPONENT_ID": "# -- AWORA-FLX COMPONENT ID: ",
    "COMPONENT_VERSION": "# -- AWORA-FLX COMPONENT Version: ",
}
SYSTEM_INFO_FILE = "system_info.json"
DEFAULT_OUTPUT_FILE = "output.json"
CLI_VERSION = "1.0"
CORES_DIR = "cores"
CURRENT_CORE = None  # Şu anda seçili olan çekirdek ID'si

def get_system_info():
    system_info = {"CLIENT": {}, "CORE": [], "COMPONENT": []}
    for root, _, files in os.walk("."):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    client_info = {}
                    core_info = {}
                    component_info = {}
                    for line in f:
                        line = line.strip()
                        if line.startswith(INFO_PREFIXES["CLIENT"]):
                            client_info["id"] = line[len(INFO_PREFIXES["CLIENT"]):].strip()
                            client_info["name"] = os.path.splitext(file)[0]
                            client_info["path"] = root
                        elif line.startswith(INFO_PREFIXES["CLIENT_VERSION"]):
                            client_info["version"] = line[len(INFO_PREFIXES["CLIENT_VERSION"]):].strip()
                        elif line.startswith(INFO_PREFIXES["CORE_ID"]):
                            core_info["id"] = line[len(INFO_PREFIXES["CORE_ID"]):].strip()
                            core_info["name"] = os.path.splitext(file)[0]
                            core_info["path"] = root
                        elif line.startswith(INFO_PREFIXES["CORE_VERSION"]):
                            core_info["version"] = line[len(INFO_PREFIXES["CORE_VERSION"]):].strip()
                        elif line.startswith(INFO_PREFIXES["COMPONENT_ID"]):
                            component_info["id"] = line[len(INFO_PREFIXES["COMPONENT_ID"]):].strip()
                            component_info["name"] = os.path.splitext(file)[0]
                            component_info["path"] = root
                        elif line.startswith(INFO_PREFIXES["COMPONENT_VERSION"]):
                            component_info["version"] = line[len(INFO_PREFIXES["COMPONENT_VERSION"]):].strip()

                    if client_info:
                        system_info["CLIENT"] = client_info
                    elif core_info:
                        system_info["CORE"].append(core_info)
                    elif component_info:
                        system_info["COMPONENT"].append(component_info)
    return system_info

def write_system_info_to_file(system_info):
    with open(SYSTEM_INFO_FILE, 'w', encoding='utf-8') as f:
        json.dump(system_info, f, indent=4)
    print(f"Sistem bilgileri '{SYSTEM_INFO_FILE}' dosyasına JSON formatında kaydedildi.")

def display_system_info(system_info):
    print("Sistem Bilgileri (JSON Formatında):")
    print(json.dumps(system_info, indent=4))

def list_cores(system_info):
    print("Kullanılabilir Analiz Çekirdekleri (system_info.json'dan):")
    if system_info["CORE"]:
        for core in system_info["CORE"]:
            is_current = "(şu anda seçili)" if CURRENT_CORE == core.get('id') else ""
            print(f"- ID: {core.get('id', '')}, İsim: {core.get('name', '')} v{core.get('version', 'bilinmiyor')} (Konum: {core.get('path', '')}) {is_current}")
    else:
        print("Sistemde hiç çekirdek bilgisi bulunamadı.")

def change_core(core_id, system_info):
    global CURRENT_CORE
    for core in system_info["CORE"]:
        if core.get('id') == core_id:
            CURRENT_CORE = core_id
            print(f"Analiz çekirdeği '{core_id}' ({core.get('name', '')}, Konum: {core.get('path', '')}) olarak değiştirildi.")
            return True
    print(f"Hata: '{core_id}' ID'sine sahip bir çekirdek bulunamadı.")
    return False

def run_analysis(input_file, config_file, output_file, system_info):
    if not CURRENT_CORE:
        print("Hata: Lütfen önce bir çekirdek seçin (-c komutu ile).")
        return

    selected_core_info = None
    for core in system_info["CORE"]:
        if core.get('id') == CURRENT_CORE:
            selected_core_info = core
            break

    if not selected_core_info:
        print(f"Hata: Seçili çekirdek ID'si '{CURRENT_CORE}' sistemde bulunamadı.")
        return

    core_file_path = os.path.join(selected_core_info.get('path'), f"{selected_core_info.get('name')}.py")
    if not os.path.exists(core_file_path):
        print(f"Hata: Çekirdek dosyası '{core_file_path}' bulunamadı.")
        return

    spec = importlib.util.spec_from_file_location(selected_core_info.get('name'), core_file_path)
    if spec is None:
        print(f"Hata: '{selected_core_info.get('name')}' çekirdeği için spec oluşturulamadı.")
        return
    core_module = importlib.util.module_from_spec(spec)
    if core_module is None:
        print(f"Hata: '{selected_core_info.get('name')}' çekirdeği için modül oluşturulamadı.")
        return
    spec.loader.exec_module(core_module)

    if not hasattr(core_module, 'analyze'):
        print(f"Hata: Seçili çekirdek ('{selected_core_info.get('name')}') 'analyze' fonksiyonuna sahip değil.")
        return

    try:
        print(f"'{selected_core_info.get('name')}' çekirdeği ile analiz başlatılıyor...")
        input_data = {}
        config_data = {}
        if input_file and os.path.exists(input_file):
            with open(input_file, 'r', encoding='utf-8') as f:
                input_data = json.load(f)
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

        results = core_module.analyze(input_data, config_data)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4)
        print(f"Analiz tamamlandı. Sonuçlar '{output_file}' dosyasına kaydedildi.")

    except FileNotFoundError:
        print("Hata: Girdi veya yapılandırma dosyası bulunamadı.")
    except json.JSONDecodeError:
        print("Hata: Girdi veya yapılandırma dosyası geçerli bir JSON formatında değil.")
    except Exception as e:
        print(f"Analiz sırasında bir hata oluştu: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Awora-FLX Kontrol ve Bilgi Aracı")
    parser.add_argument("--info", action="store_true", help="Sistem bilgilerini ekrana yazdırır ve dosyayı günceller.")
    parser.add_argument("-l", "--list-cores", action="store_true", help="Kullanılabilir analiz çekirdeklerini listeler.")
    parser.add_argument("-c", "--change-core", type=str, metavar="çekirdek_id", help="Kullanılacak analiz çekirdeğinin ID'sini belirtir.")
    parser.add_argument("-i", "--input", type=str, metavar="girdi_dosyası", help="Girdi veri dosyasını belirtir (JSON).")
    parser.add_argument("-cf", "--config", type=str, metavar="yapılandırma_dosyası", help="Yapılandırma dosyasını belirtir (JSON).")
    parser.add_argument("-o", "--output", type=str, metavar="çıktı_dosyası", default=DEFAULT_OUTPUT_FILE, help=f"Çıktı sonuçlarının kaydedileceği dosyayı belirtir (JSON, varsayılan: {DEFAULT_OUTPUT_FILE}).")
    parser.add_argument("-r", "--run", action="store_true", help="Belirtilen ayarlarla analizi çalıştırır.")
    parser.add_argument("--version", action="version", version=f"Awora-FLX CLI v{CLI_VERSION}")

    args = parser.parse_args()

    system_info = get_system_info()
    write_system_info_to_file(system_info)

    if not any(vars(args).values()):
        input_command = input("AFX komutunu girin (örneğin --info, -l): ").strip()
        if input_command == "--info":
            display_system_info(system_info)
        elif input_command == "-l":
            list_cores(system_info)
        elif input_command.startswith("-c "):
            core_id = input_command[3:].strip()
            change_core(core_id, system_info)
        elif input_command == "-r":
            run_analysis(args.input, args.config, args.output, system_info)
        else:
            parser.print_help()
    else:
        if args.info:
            display_system_info(system_info)
        elif args.list_cores:
            list_cores(system_info)
        elif args.change_core:
            change_core(args.change_core, system_info)
        elif args.run:
            run_analysis(args.input, args.config, args.output, system_info)