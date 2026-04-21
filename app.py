from flask import Flask, render_template
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Hindari error di environment server
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime

app = Flask(__name__)

# ==============================================
# 1. BACA DATASET YANG SUDAH BERSIH
# ==============================================
data = pd.read_csv('Data_Tanaman_Padi_Sumatera_praproses.csv')

# Pastikan kolom numerik dalam format float
kolom_numerik = ['Produksi', 'Luas Panen', 'Curah hujan', 'Kelembapan', 'Suhu rata-rata']
for col in kolom_numerik:
    data[col] = pd.to_numeric(data[col], errors='coerce')

# ==============================================
# 2. FUNGSI BANTU UNTUK MEMBUAT PLOT JADI BASE64
# ==============================================
def plot_to_base64():
    """Mengubah plot matplotlib menjadi format Base64 untuk ditampilkan di HTML"""
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return plot_url

# ==============================================
# 3. FUNGSI PEMBUATAN GRAFIK
# ==============================================

def plot_tren_produksi():
    """Diagram Garis: Tren Produksi per Provinsi (1993-2020)"""
    provinsi_pilih = ['Sumatera Utara', 'Sumatera Selatan', 'Aceh', 'Lampung']
    plt.figure(figsize=(12, 6))
    for prov in provinsi_pilih:
        subset = data[data['Provinsi'] == prov].sort_values('Tahun')
        plt.plot(subset['Tahun'], subset['Produksi'], marker='o', label=prov)
    plt.xlabel('Tahun')
    plt.ylabel('Produksi (ton)')
    plt.title('Tren Produksi Padi per Provinsi')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    return plot_to_base64()

# ==============================================
# 4. ROUTE UTAMA DASHBOARD
# ==============================================
@app.route('/')
def dashboard():
    """Halaman utama dashboard menampilkan semua grafik"""
    try:
        img_tren = plot_tren_produksi()
    except Exception as e:
        return f"Terjadi error saat membuat grafik: {str(e)}", 500

    # Statistik deskriptif untuk ditampilkan di dashboard
    stats_produksi = data['Produksi'].describe().to_dict()
    stats_luas = data['Luas Panen'].describe().to_dict()
    stats_curah = data['Curah hujan'].describe().to_dict()
    stats_kelembapan = data['Kelembapan'].describe().to_dict()
    stats_suhu = data['Suhu rata-rata'].describe().to_dict()

    return render_template(
        'dashboard.html',
        img_tren=img_tren,
        stats_produksi=stats_produksi,
        stats_luas=stats_luas,
        stats_curah=stats_curah,
        stats_kelembapan=stats_kelembapan,
        stats_suhu=stats_suhu,
        tahun_min=int(data['Tahun'].min()),
        tahun_max=int(data['Tahun'].max()),
        provinsi_count=data['Provinsi'].nunique()
    )

if __name__ == '__main__':
    app.run(debug=True)