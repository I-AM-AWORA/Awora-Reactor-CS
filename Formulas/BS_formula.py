def calculate_BS(dP, sigma, dPref, sigmaref):
    """
    Basınç Skorunu (BS) hesaplar.

    Args:
        dP: Basınç farkı
        sigma: Malzemenin gerilimi
        dPref: Referans basınç farkı
        sigmaref: Referans gerilimi

    Returns:
        float: Hesaplanan Basınç Skoru (BS)
    """
    bs = (dP / dPref) + (sigma / sigmaref)
    return bs