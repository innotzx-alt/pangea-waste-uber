import os
import json
from flask import Flask, request, jsonify, render_template
from sklearn.linear_model import LinearRegression
import numpy as np

app = Flask(__name__)

# Mafaili ya Kutunza Data
FAILI_LA_MADEREVA = "madereva.json"
FAILI_LA_SAFARI = "safari.json"

# --- 1. UBINGO WA AI (Linear Regression) ---
idadi_ya_watu = np.array([[1], [2], [3], [5], [6], [8]])
tani_za_taka = np.array([0.2, 0.4, 0.6, 1.1, 1.3, 1.8])

ubongo_wa_ai = LinearRegression()
ubongo_wa_ai.fit(idadi_ya_watu, tani_za_taka)

def pakia_data(faili, chaguo_default=[]):
    if os.path.exists(faili):
        with open(faili, "r") as f:
            try:
                return json.load(f)
            except:
                return chaguo_default
    return chaguo_default

def hifadhi_data(faili, data):
    with open(faili, "w") as f:
        json.dump(data, f, indent=4)

# ==========================================
# 2. WEB ENDPOINTS (Anwani za Mtandao)
# ==========================================

@app.route('/', methods=['GET'])
def nyumbani():
    return render_template('index.html')

# ANWANI YA 1: Kusajili Dereva kutoka kwenye Simu yake
@app.route('/sajili_dereva', methods=['POST'])
def api_sajili_dereva():
    data = request.get_json() or {}
    jina = data.get("jina")
    simu = data.get("simu")
    gari = data.get("aina_gari")
    tani = float(data.get("uwezo_tani", 7.0))

    madereva = pakia_data(FAILI_LA_MADEREVA, [
        {"jina": "Kassim wa Guta", "simu": "071123344", "aina_gari": "Guta/Mkokoteni", "uwezo_tani": 1.5},
        {"jina": "Mzee Juma", "simu": "0755667788", "aina_gari": "Fuso Tipper", "uwezo_tani": 7.0}
    ])

    if jina and simu:
        dereva_mpya = {"jina": jina, "simu": simu, "aina_gari": gari, "uwezo_tani": tani}
        madereva.append(dereva_mpya)
        hifadhi_data(FAILI_LA_MADEREVA, madereva)
        return jsonify({"status": True, "ujumbe": f"Dereva {jina} amesajiliwa kikamilifu!"})
    
    return jsonify({"status": False, "ujumbe": "Data hazijakamilika"}), 400

# ANWANI YA 2: Mteja Kuomba Gari la Taka (Hapa AI inapiga hesabu)
@app.route('/omba_gari', methods=['POST', 'GET'])
def api_omba_gari():
    if request.method == 'GET':
        # Kama dereva anavuta data, tunampa safari ya mwisho iliyopo
        safari_zote = pakia_data(FAILI_LA_SAFARI)
        if safari_zote:
            return jsonify({"status": True, "data_ya_safari": safari_zote[-1]})
        return jsonify({"status": False, "ujumbe": "Hakuna safari yoyote kwa sasa"}), 404

    data = request.get_json() or {}
    mteja = data.get("mteja", "Mteja wa kwanza")
    mtaa = data.get("mtaa")
    watu = int(data.get("watu", 4))
    aina_huduma = data.get("aina_huduma", "Kaya")

    # AI inakadiria tani za taka kulingana na idadi ya watu
    tani_zilizokadiriwa = float(ubongo_wa_ai.predict([[watu]])[0])
    tani_safi = round(max(0.1, tani_zilizokadiriwa), 2)

    madereva = pakia_data(FAILI_LA_MADEREVA, [
        {"jina": "Kassim wa Guta", "simu": "071123344", "aina_gari": "Guta/Mkokoteni", "uwezo_tani": 1.5},
        {"jina": "Mzee Juma", "simu": "0755667788", "aina_gari": "Fuso Tipper", "uwezo_tani": 7.0}
    ])

    # AI inachagua gari linalofaa kulingana na uzito wa taka
    dereva_teule = madereva[0]
    for d in madereva:
        if d["uwezo_tani"] >= tani_safi:
            dereva_teule = d
            break

    # Hesabu za Kamisheni (The Ghost Architect Engine)
    kamisheni = int(tani_safi * 5000)
    if kamisheni < 1000: kamisheni = 1000

    safari_zote = pakia_data(FAILI_LA_SAFARI)
    safari_mpya = {
        "mteja": mteja,
        "mtaa": mtaa,
        "watu_nyumbani": watu,
        "tani_ai": tani_safi,
        "dereva": dereva_teule["jina"],
        "simu_dereva": dereva_teule["simu"],
        "gari": dereva_teule["aina_gari"],
        "kamisheni_tsh": f"{kamisheni:,}"
    }

    safari_zote.append(safari_mpya)
    hifadhi_data(FAILI_LA_SAFARI, safari_zote)

    return jsonify({"status": True, "data_ya_safari": safari_mpya})

# ANWANI YA 3: Ukurasa wa Dereva kuona Order LIVE
@app.route('/dereva', methods=['GET'])
def ukurasa_wa_dereva():
    return render_template('dereva.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
