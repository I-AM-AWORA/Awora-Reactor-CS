import os
import json
import platform
import uuid
import argparse
import logging
import time

SYSTEM_INFO_FILE = "system_info.json"
LOG_FILE = "client.log"

# Temel loglama ayarları
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s')

def bilgi_mesaji(mesaj):
    """Detaylı bilgi mesajlarını loglar ve ekrana yazdırır."""
    logging.info(mesaj)
    print(f"[BİLGİ] {mesaj}")

def uyari_mesaji(mesaj):
    """Detaylı uyarı mesajlarını loglar ve ekrana yazdırır."""
    logging.warning(mesaj)
    print(f"[UYARI] {mesaj}")

def hata_mesaji(mesaj):
    """Detaylı hata mesajlarını loglar ve ekrana yazdırır."""
    logging.error(mesaj)
    print(f"[HATA] {mesaj}")

def get_system_info(detay_seviyesi="normal"):
    """Sistem bilgilerini detay seviyesine göre toplar."""
    bilgi_mesaji(f"Sistem bilgileri '{detay_seviyesi}' detay seviyesinde toplanıyor...")
    system_info = {
        "temel": {
            "platform": platform.system(),
            "release": platform.release(),
            "architecture": platform.machine(),
            "hostname": platform.node(),
            "python_version": platform.python_version()
        }
    }
    if detay_seviyesi in ["normal", "detayli"]:
        system_info["normal"] = {
            "version": platform.version(),
            "processor": platform.processor(),
            "uuid": str(uuid.uuid1())
        }
    if detay_seviyesi == "detayli":
        system_info["detayli"] = {
            "python_build": platform.python_build(),
            "python_compiler": platform.python_compiler(),
            "uname": platform.uname()._asdict()
        }
    bilgi_mesaji(f"Sistem bilgileri toplandı.")
    return system_info

def load_system_info():
    """system_info.json dosyasını yükler."""
    bilgi_mesaji(f"'{SYSTEM_INFO_FILE}' dosyası yüklenmeye çalışılıyor...")
    try:
        with open(SYSTEM_INFO_FILE, "r", encoding="utf-8") as f:
            info = json.load(f)
            bilgi_mesaji(f"'{SYSTEM_INFO_FILE}' dosyası başarıyla yüklendi.")
            return info
    except FileNotFoundError:
        uyari_mesaji(f"'{SYSTEM_INFO_FILE}' dosyası bulunamadı.")
        return None
    except json.JSONDecodeError as e:
        hata_mesaji(f"'{SYSTEM_INFO_FILE}' dosyası geçerli bir JSON formatında değil. Hata: {e}")
        return None
    except IOError as e:
        hata_mesaji(f"'{SYSTEM_INFO_FILE}' dosyası okunurken bir hata oluştu. Hata: {e}")
        return None

def save_system_info(info, yedekle=False):
    """Sistem bilgilerini system_info.json dosyasına kaydeder ve isteğe bağlı olarak yedekler."""
    bilgi_mesaji(f"Sistem bilgileri '{SYSTEM_INFO_FILE}' dosyasına kaydediliyor...")
    if yedekle and os.path.exists(SYSTEM_INFO_FILE):
        yedek_dosya = SYSTEM_INFO_FILE + ".yedek." + time.strftime("%Y%m%d%H%M%S")
        try:
            os.rename(SYSTEM_INFO_FILE, yedek_dosya)
            bilgi_mesaji(f"Mevcut '{SYSTEM_INFO_FILE}' dosyası '{yedek_dosya}' olarak yedeklendi.")
        except OSError as e:
            hata_mesaji(f"'{SYSTEM_INFO_FILE}' dosyası yedeklenirken bir hata oluştu. Hata: {e}")

    try:
        with open(SYSTEM_INFO_FILE, "w", encoding="utf-8") as f:
            json.dump(info, f, indent=4)
        bilgi_mesaji(f"Sistem bilgileri başarıyla '{SYSTEM_INFO_FILE}' dosyasına kaydedildi.")
    except IOError as e:
        hata_mesaji(f"Hata: Sistem bilgileri '{SYSTEM_INFO_FILE}' dosyasına yazılamadı: {e}")

def display_system_info(info, detay_goster=False):
    """Sistem bilgilerini detaylı bir şekilde ekrana yazdırır."""
    if info:
        print("\n--- Sistem Bilgileri ---")
        for ana_kategori, degerler in info.items():
            print(f"\n[{ana_kategori.upper()}]")
            if isinstance(degerler, dict):
                for alt_anahtar, alt_deger in degerler.items():
                    print(f"  {alt_anahtar}: {alt_deger}")
            else:
                print(f"  Değer: {degerler}")
        print("-------------------------\n")
    else:
        uyari_mesaji("Sistem bilgisi bulunamadı veya yüklenirken bir hata oluştu.")

def main():
    parser = argparse.ArgumentParser(description="Awora-FLX İstemci Uygulaması - Detaylı Komut İstemi",
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("action",
                        choices=['info', 'show', 'save', 'load'],
                        help="""Yapılacak eylem:
  info  : Sistem bilgilerini toplar ve ekrana yazdırır. Kaydetmez.
  show  : Kaydedilmiş sistem bilgilerini detaylı bir şekilde gösterir.
  save  : Sistem bilgilerini toplar ve '{0}' dosyasına kaydeder.
          İsteğe bağlı olarak yedekleme de yapar.
  load  : Kaydedilmiş sistem bilgilerini yükler ve ekrana temel bilgileri gösterir.
""".format(SYSTEM_INFO_FILE))
    parser.add_argument("-d", "--detay",
                        choices=['normal', 'detayli'],
                        default='normal',
                        help="Sistem bilgisinin detay seviyesi (yalnızca 'info' için geçerli): normal (varsayılan), detayli.")
    parser.add_argument("-y", "--yedekle",
                        action="store_true",
                        help="Kaydetmeden önce mevcut '{0}' dosyasını yedekler (yalnızca 'save' için geçerli).".format(SYSTEM_INFO_FILE))
    parser.add_argument("--verbose",
                        action="store_true",
                        help="Daha fazla işlem ayrıntısı gösterir.")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        bilgi_mesaji("Detaylı çıktı modu etkinleştirildi.")
    else:
        logging.getLogger().setLevel(logging.INFO)

    if args.action == 'info':
        bilgi = get_system_info(args.detay)
        display_system_info(bilgi, detay_goster=True)
    elif args.action == 'show':
        loaded_info = load_system_info()
        display_system_info(loaded_info, detay_goster=True)
    elif args.action == 'save':
        bilgi = get_system_info()
        save_system_info(bilgi, args.yedekle)
    elif args.action == 'load':
        loaded_info = load_system_info()
        if loaded_info and "temel" in loaded_info:
            print("\n--- Yüklenen Sistem Bilgileri (Temel) ---")
            for key, value in loaded_info["temel"].items():
                print(f"{key}: {value}")
            print("-----------------------------------------\n")
        else:
            uyari_mesaji("Yüklenecek sistem bilgisi bulunamadı veya temel bilgiler eksik.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()