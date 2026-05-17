import os
import json
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Database za muda
FAILI_LA_SAFARI = '/tmp/safari_data.json'
FAILI_LA_MADEREVA = '/tmp/madereva_data.json'

MADEREVA_DEFAULT = [
    {"id": 1, "jina": "Kassim wa Guta", "aina_gari": "Guta/Mkokoteni", "simu": "071123344", "uwezo_tani": 0.5, "status": "wazi"},
    {"id": 2, "jina": "Mzee Juma", "aina_gari": "TATA Pick-up", "simu": "0655998877", "uwezo_tani": 1.5, "status": "wazi"},
    {"id": 3, "jina": "Chonji", "aina_gari": "Canter Mzigo", "simu": "0766112233", "uwezo_tani": 3.5, "status": "wazi"}
]

def pakia_data(njia_ya_faili, data_default=[]):
    if not os.path.exists(njia_ya_faili):
        with open(njia_ya_faili, 'w') as f:
            json.dump(data_default, f)
        return data_default
    try:
        with open(njia_ya_faili, 'r') as f:
            return json.load(f)
    except:
        return data_default

def hifadhi_data(njia_ya_faili, data):
    with open(njia_ya_faili, 'w') as f:
        json.dump(data, f)

pakia_data(FAILI_LA_MADEREVA, MADEREVA_DEFAULT)
pakia_data(FAILI_LA_SAFARI, [])

# 1. Ukurasa wa Mteja
@app.route('/', methods=['GET'])
def nyumbani():
    return render_template('index.html')

# 2. API ya Kuomba Gari
@app.route('/omba_gari', methods=['POST', 'GET'])
def omba_gari():
    if request.method == 'GET':
        madereva = pakia_data(FAILI_LA_MADEREVA, MADEREVA_DEFAULT)
        safari_mpyya = {
            "mteja": "Kuangalia", "mtaa": "Mtaani", "watu_nyumbani": 1, "tani_ai": 0.17,
            "dereva": madereva[0]["jina"], "gari": madereva[0]["aina_gari"],
            "simu_dereva": madereva[0]["simu"], "kamisheni_tsh": "1,000"
        }
        return jsonify({"status": True, "data_ya_safari": safari_mpyya})

    taarifa = request.get_json()
    if not taarifa:
        return jsonify({"status": False, "message": "Hakuna data"}), 400

    mteja = taarifa.get('mteja', 'Mteja wa Siri')
    mtaa = taarifa.get('mtaa', 'Mtaa usiojulikana')
    watu = int(taarifa.get('watu', 4))

    tani_safi = round(watu * 0.17, 2)

    madereva = pakia_data(FAILI_LA_MADEREVA, MADEREVA_DEFAULT)
    dereva_teule = madereva[0]
    for d in madereva:
        if d["uwezo_tani"] >= tani_safi:
            dereva_teule = d
            break

    kamisheni = int(tani_safi * 5000)
    if kamisheni < 1000: kamisheni = 1000

    safari_zote = pakia_data(FAILI_LA_SAFARI)
    safari_mpya = {
        "mteja": mteja, "mtaa": mtaa, "watu_nyumbani": watu, "tani_ai": tani_safi,
        "dereva": dereva_teule["jina"], "simu_dereva": dereva_teule["simu"],
        "gari": dereva_teule["aina_gari"], "kamisheni_tsh": f"{kamisheni:,}"
    }
    
    safari_zote.append(safari_mpya)
    hifadhi_data(FAILI_LA_SAFARI, safari_zote)

    return jsonify({"status": True, "data_ya_safari": safari_mpya})

# 3. Ukurasa wa Dereva (Njia fupi na sahihi ya kiwanda)
@app.route('/dereva', methods=['GET'])
def ukurasa_wa_dereva():
    return render_template('dereva.html')

# 4. API ya madereva kuona order live
@app.route('/api/pata_order', methods=['GET'])
def pata_order_live():
    safari_zote = pakia_data(FAILI_LA_SAFARI)
    return jsonify(safari_zote)

if __name__ == '__main__':
    app.run(debug=True)
