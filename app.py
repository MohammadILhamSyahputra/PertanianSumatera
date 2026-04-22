from flask import Flask, render_template, url_for
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Hindari error di environment server
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime
import os
import seaborn as sns

app = Flask(__name__)

IMAGE_FOLDER = 'static/images'
os.makedirs(IMAGE_FOLDER, exist_ok=True)


# ==============================================
# 1. BACA DATASET YANG SUDAH BERSIH
# ==============================================
data = pd.read_csv('Data_Tanaman_Padi_Sumatera_praproses.csv')

# Pastikan kolom numerik dalam format float
kolom_numerik = ['Produksi', 'Luas Panen', 'Curah hujan', 'Kelembapan', 'Suhu rata-rata']
for col in kolom_numerik:
    data[col] = pd.to_numeric(data[col], errors='coerce')

def save_plot_as_png(filename):
    """
    Menyimpan plot matplotlib yang sudah dibuat ke folder static/images
    dan mengembalikan path url untuk diakses di template.
    """
    filepath = os.path.join(IMAGE_FOLDER, filename)
    plt.savefig(filepath, bbox_inches='tight', dpi=100)
    plt.close()
    return url_for('static', filename=f'images/{filename}')

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
    plt.figure(figsize=(14, 7))
    daftar_provinsi = data['Provinsi'].unique()
    colors = plt.cm.get_cmap('tab20', len(daftar_provinsi))
    for i, prov in enumerate(daftar_provinsi):
        subset = data[data['Provinsi'] == prov].sort_values('Tahun')
        
        plt.plot(
            subset['Tahun'], 
            subset['Produksi'], 
            marker='o', 
            markersize=4, 
            linewidth=1.5,
            label=prov,
            color=colors(i)
        )
    plt.xlabel('Tahun', fontsize=12)
    plt.ylabel('Produksi (ton)', fontsize=12)
    plt.title('Tren Produksi Padi Seluruh Provinsi di Sumatera', fontsize=14)
    plt.legend(title="Provinsi", bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
    
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    return save_plot_as_png('tren_produksi.png')

def plot_distribusi_kelembapan():
    plt.figure(figsize=(12, 6))
    data_clean = data.dropna(subset=['Kelembapan'])
    
    sns.boxplot(x='Provinsi', y='Kelembapan', data=data_clean, palette='GnBu')
    plt.xticks(rotation=45, ha='right')
    plt.title('Variasi dan Distribusi Kelembapan per Provinsi')
    plt.ylabel('Kelembapan (%)')
    
    return save_plot_as_png('distribusi_kelembapan.png')

def plot_rata_produksi():
    rata_produksi = data.groupby('Provinsi')['Produksi'].mean().sort_values(ascending=False)
    plt.figure(figsize=(12, 6))
    warna = plt.cm.Greens(np.linspace(0.3, 0.9, len(rata_produksi)))
    plt.bar(rata_produksi.index, rata_produksi.values, color=warna)
    plt.xlabel('Provinsi')
    plt.ylabel('Rata-rata Produksi (ton)')
    plt.title('Rata-rata Produksi Padi per Provinsi')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    return save_plot_as_png('rata_produksi.png')

def plot_korelasi_luas_produksi():
    plt.figure(figsize=(12, 6))
    daftar_provinsi = data['Provinsi'].unique()
    colors = plt.cm.get_cmap('tab10', len(daftar_provinsi))

    for i, prov in enumerate(daftar_provinsi):
        subset = data[data['Provinsi'] == prov]
        
        plt.scatter(
            subset['Luas Panen'], 
            subset['Produksi'], 
            alpha=0.7, 
            label=prov,
            color=colors(i),
            edgecolors='w', 
            s=60            
        )

    plt.title('Hubungan Luas Panen vs Produksi Padi Berdasarkan Provinsi', fontsize=14)
    plt.xlabel('Luas Panen (ha)', fontsize=12)
    plt.ylabel('Produksi (ton)', fontsize=12)
    plt.legend(title="Provinsi", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    return save_plot_as_png('korelasi_luas.png')

def plot_scatter_curah():
    plt.figure(figsize=(12, 6))
    daftar_provinsi = data['Provinsi'].unique()
    colors = plt.cm.get_cmap('tab10', len(daftar_provinsi))
    for i, prov in enumerate(daftar_provinsi):
        subset = data[data['Provinsi'] == prov]
        
        plt.scatter(
            subset['Curah hujan'], 
            subset['Produksi'], 
            alpha=0.7, 
            label=prov,
            color=colors(i),
            edgecolors='w', 
            s=60
        )
    plt.title('Hubungan Curah Hujan dengan Produksi Padi Berdasarkan Provinsi', fontsize=14)
    plt.xlabel('Curah Hujan (mm)', fontsize=12)
    plt.ylabel('Produksi (ton)', fontsize=12)
    plt.legend(title="Provinsi", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    return save_plot_as_png('scatter_curah.png')

def plot_histogram_produksi():
    plt.figure(figsize=(10, 6))
    plt.hist(data['Produksi'], bins=20, edgecolor='black', alpha=0.7, color='skyblue')
    plt.xlabel('Produksi (ton)')
    plt.ylabel('Frekuensi')
    plt.title('Histogram Distribusi Produksi Padi')
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    return save_plot_as_png('histogram_produksi.png')

def plot_perbandingan_produksi_curah():
    agregat = data.groupby('Provinsi').agg({
        'Produksi': 'sum',
        'Luas Panen': 'sum',
        'Curah hujan': 'mean'
    }).sort_values('Produksi', ascending=False)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    agregat['Produksi'].plot(
        kind='bar', ax=ax, color='blue', alpha=0.7,
        label='Total Produksi (ton)'
    )
    ax.set_ylabel('Total Produksi (ton)', fontsize=12)
    ax.set_xlabel('Provinsi', fontsize=12)
    ax2 = ax.twinx()
    agregat['Curah hujan'].plot(
        kind='line', ax=ax2, color='red', marker='o', linewidth=2,
        label='Rata-rata Curah Hujan (mm)'
    )
    ax2.set_ylabel('Rata-rata Curah Hujan (mm)', fontsize=12)
    
    plt.title('Perbandingan Total Produksi dan Rata-rata Curah Hujan per Provinsi', fontsize=14)
    ax.legend(loc='upper left')
    ax2.legend(loc='upper right')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    return save_plot_as_png('perbandingan_produksi_curah.png')

def plot_proporsi_per_tahun(tahun):
    data_tahun = data[data['Tahun'] == tahun].copy()

    if data_tahun.empty:
        return None 
    
    idx_maks = data_tahun['Produksi'].argmax()
    explode_list = [0] * len(data_tahun)
    explode_list[idx_maks] = 0.1
    
    fig = plt.figure(figsize=(8, 8), dpi=100)
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    
    ax.pie(
        data_tahun['Produksi'], 
        labels=data_tahun['Provinsi'], 
        autopct='%1.1f%%', 
        startangle=140, 
        explode=explode_list,
        colors=plt.cm.Paired(np.linspace(0, 1, len(data_tahun)))
    )
    
    ax.set_title(f'Proporsi Produksi Padi Sumatera ({tahun})', pad=20, fontsize=14)
    
    filename = f'proporsi_{tahun}.png'
    filepath = os.path.join(IMAGE_FOLDER, filename)
    plt.savefig(filepath) 
    plt.close()
    
    return url_for('static', filename=f'images/{filename}')

# ==============================================
# 4. ROUTE UTAMA DASHBOARD
# ==============================================
@app.route('/')
def dashboard():
    """Halaman utama dashboard menampilkan semua grafik"""
    try:
        img_tren = plot_tren_produksi()
        img_rata = plot_rata_produksi()
        img_scatter = plot_korelasi_luas_produksi()
        img_scatter_curah = plot_scatter_curah()
        img_hist = plot_histogram_produksi()
        img_perbandingan = plot_perbandingan_produksi_curah()
        img_pie_1993 = plot_proporsi_per_tahun(1993)
        img_pie_2020 = plot_proporsi_per_tahun(2020)
        img_distribusi_kelembapan = plot_distribusi_kelembapan()
        
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
        img_rata=img_rata,
        img_scatter=img_scatter,
        img_scatter_curah=img_scatter_curah,
        img_hist=img_hist,
        img_perbandingan=img_perbandingan,
        stats_produksi=stats_produksi,
        stats_luas=stats_luas,
        stats_curah=stats_curah,
        stats_kelembapan=stats_kelembapan,
        stats_suhu=stats_suhu,
        tahun_min=int(data['Tahun'].min()),
        tahun_max=int(data['Tahun'].max()),
        provinsi_count=data['Provinsi'].nunique(),
        img_pie_1993=img_pie_1993,
        img_pie_2020=img_pie_2020,
        img_distribusi_kelembapan=img_distribusi_kelembapan
        
    )

if __name__ == '__main__':
    app.run(debug=True)