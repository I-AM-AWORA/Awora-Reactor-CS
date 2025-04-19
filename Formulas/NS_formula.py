def calculate_NS(neutron_akisi, keff, neutron_akisi_ref, kref):
    """
    Nötron Skorunu (NS) hesaplar.

    Args:
        neutron_akisi: Nötron akışı
        keff: Fizyon zincir reaksiyonu
        neutron_akisi_ref: Referans nötron akışı
        kref: Referans fizyon zincir reaksiyonu

    Returns:
        float: Hesaplanan Nötron Skoru (NS)
    """
    ns = (neutron_akisi / neutron_akisi_ref) + (keff / kref)
    return ns