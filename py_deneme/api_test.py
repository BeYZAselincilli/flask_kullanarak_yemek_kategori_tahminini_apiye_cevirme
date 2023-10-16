import requests

# Kullanıcıdan girdileri al
item_name = input("Ürün Adı (ITEMNAME): ")
madde_grubu_adi = input("Madde Grubu Adı (MADDE_GRUBU_ADI): ")

# API'ye istek gönder
url = "http://127.0.0.1:5000/predict"  # Flask uygulamanızın adresini kullanın
data = {"itemname": item_name, "maddegrubuadi": madde_grubu_adi}

response = requests.post(url, json=data)

if response.status_code == 200:
    result = response.json()
    
    # 'prediction' anahtar adıyla tahmin sonucunu alın ve yazdırın
    tahmin = result.get('prediction')
    if tahmin:
        print("\nTahmin Edilen LEVEL_2:", tahmin)

    # 'KATEGORININ GUVENLIK ORANI %' anahtar adıyla güvenlik oranını alın ve yazdırın
    guvenlik_orani = result.get('KATEGORININ GUVENLIK ORANI %')
    if guvenlik_orani:
        print("KATEGORİNİN GÜVENLİK ORANI %", guvenlik_orani)

    # 'En Yakın 5 Alternatif Tahmin' anahtar adıyla alternatif tahminleri alın ve yazdırın
    en_yakin_alternatifler = result.get('En Yakın 5 Alternatif Tahmin')
    if en_yakin_alternatifler:
        print("\nEn Yakın 5 Alternatif Tahmin:")
        for tahmin in en_yakin_alternatifler:
            print(f"{tahmin['sinif']}: %{tahmin['olasilik']:.2f}")

    # 'toplam alt kategorilerin oranı toplamı %' anahtar adıyla oranı alın ve yazdırın
    toplam_oran = result.get('toplam alt kategorilerin oranı toplamı %')
    if toplam_oran:
        print("\ntoplam alt kategorilerin oranı toplamı %", toplam_oran)

    # 'Bu tahmin, diğer sınıflara göre' anahtar adıyla güvenilirlik farkını alın ve yazdırın
    guvenilirlik_farki = result.get('Bu tahmin, diğer sınıflara göre')
    if guvenilirlik_farki:
        print(f"\nBu tahmin, diğer sınıflara göre %{guvenilirlik_farki:.2f} daha güvenilir.")
else:
    print("API Hatası:", response.text)
