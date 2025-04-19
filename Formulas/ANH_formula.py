def calculate_ANH(skorlar, agirliklar):
    """
    Ağırlıklı Harmonik Ortalama'yı hesaplar.

    Args:
        skorlar (dict): Skorların adlarını ve değerlerini içeren bir sözlük.
        agirliklar (dict): Skorların adlarını ve ağırlıklarını içeren bir sözlük.

    Returns:
        float: Hesaplanan Ağırlıklı Harmonik Ortalama.
    """
    toplam_agirlik = sum(agirliklar.values())
    toplam = 0
    for skor, agirlik in agirliklar.items():
        toplam += agirlik / skorlar.get(skor, 1)  # Skor yoksa 1 al
    return toplam_agirlik / toplam if toplam else 0