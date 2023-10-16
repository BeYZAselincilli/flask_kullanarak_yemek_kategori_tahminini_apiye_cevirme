import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from flask import Flask, request, jsonify

app = Flask(__name__)

# Veriyi yüklemek için ayrı bir fonksiyon
def load_data():
    excel_path = r"excel dosyasının yolu"
    return pd.read_excel(excel_path)

# Güvenlik oranını hesaplamak için ayrı bir fonksiyon
def compute_safety_score(item_name, madde_grubu_adi):
    veri = load_data()

    X = veri['ITEMNAME'] + " " + veri['MADDE_GRUBU_ADI']
    y = veri['LEVEL_2']

    vektorlestirme = CountVectorizer()
    X_vektorlestirilms = vektorlestirme.fit_transform(X)

    siniflandirma = MultinomialNB()
    siniflandirma.fit(X_vektorlestirilms, y)

    veri_vektor = vektorlestirme.transform([item_name + " " + madde_grubu_adi])
    tahmin_prob = siniflandirma.predict_proba(veri_vektor)

    tahmin_sinifi = siniflandirma.classes_[tahmin_prob.argmax()]

    diger_olasiliklar = tahmin_prob[0, siniflandirma.classes_ != tahmin_sinifi]
    diger_siniflar = siniflandirma.classes_[siniflandirma.classes_ != tahmin_sinifi]

    guvenlik_orani = (tahmin_prob.max() - diger_olasiliklar.max()) / diger_olasiliklar.max() * 100

    return tahmin_sinifi, guvenlik_orani

# Flask API için endpoint
@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        item_name = data.get('itemname')
        madde_grubu_adi = data.get('maddegrubuadi')

        # Tahmin ve güvenlik oranını hesapla
        tahmin_sinifi, guvenlik_orani = compute_safety_score(item_name, madde_grubu_adi)

        # Diğer alternatif tahminleri hesapla
        veri = load_data()
        X = veri['ITEMNAME'] + " " + veri['MADDE_GRUBU_ADI']
        y = veri['LEVEL_2']
        vektorlestirme = CountVectorizer()
        X_vektorlestirilms = vektorlestirme.fit_transform(X)
        siniflandirma = MultinomialNB()
        siniflandirma.fit(X_vektorlestirilms, y)
        veri_vektor = vektorlestirme.transform([item_name + " " + madde_grubu_adi])
        tahmin_prob = siniflandirma.predict_proba(veri_vektor)
        diger_siniflar = siniflandirma.classes_[siniflandirma.classes_ != tahmin_sinifi]
        diger_olasiliklar = tahmin_prob[0, siniflandirma.classes_ != tahmin_sinifi]
        en_yakin_alternatifler = sorted(zip(diger_siniflar, diger_olasiliklar), key=lambda x: x[1], reverse=True)[:5]

        # Cevabı hazırla
        response_data = {
            'prediction': tahmin_sinifi,
            'KATEGORININ GUVENLIK ORANI %': guvenlik_orani,
            'En Yakın 5 Alternatif Tahmin': [{'sinif': sinif, 'olasilik': olasilik} for sinif, olasilik in en_yakin_alternatifler],
            'toplam alt kategorilerin oranı toplamı %': sum(olasilik for _, olasilik in en_yakin_alternatifler),
            'Bu tahmin, diğer sınıflara göre': guvenlik_orani,
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
