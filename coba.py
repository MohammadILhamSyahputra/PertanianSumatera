from flask import Flask

# Inisialisasi aplikasi Flask
app = Flask(__name__)

# Membuat rute utama (halaman depan)
@app.route('/')
def hello():
    return "<h1>Flask Berhasil Terinstal!</h1><p>Dashboard Ilmu Data sedang disiapkan.</p>"

if __name__ == '__main__':
    # Menjalankan server dalam mode debug agar otomatis restart jika ada perubahan kode
    app.run(debug=True)