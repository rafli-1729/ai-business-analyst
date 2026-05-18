# Ringkasan Alur Kerja Warehouse

Arsitektur ini mengikuti model Medallion (Bronze, Silver, Gold) yang terstruktur dengan baik, menggunakan kombinasi skrip Python untuk ingesti dan proyek dbt untuk transformasi.

---

# 1. Ingesti (Layer Bronze)

Tujuan dari layer ini adalah mendapatkan salinan data mentah dari berbagai sumber ke dalam warehouse.

* **Sumber Data:**
  Data berasal dari berbagai sumber yang didefinisikan di `warehouse/ingestion/registry.json`:

  * Google Sheets: `customers`, `products`, `orders`, `order_items`, dll.
  * Kaggle: `geolocation`.
  * File CSV Lokal: `geography_master` dan `product_category_mapping`.

* **Proses:**
  Proses ingesti diatur oleh Dagster. Untuk setiap tabel, data diambil dan dimuat ke dalam tabel staging di PostgreSQL. Dari sana, data dimasukkan ke dalam skema bronze dengan tipe data yang sudah disesuaikan. Ini menciptakan salinan data sumber yang mentah namun sudah terstruktur.

---

# 2. Transformasi & Standardisasi (Layer Silver)

Tujuan dari layer ini adalah membersihkan, menstandardisasi, dan menyiapkan data untuk analisis. Transformasi dilakukan menggunakan model SQL di dalam proyek dbt pada:

```text
warehouse/transformation/models/silver/
```

## Standardisasi Utama yang Dilakukan

* **Pembersihan Data:**

  * Menghapus spasi kosong di awal/akhir teks (menggunakan `TRIM`).
  * Mengubah string kosong (`''`) menjadi nilai `NULL` untuk konsistensi.

* **Penyesuaian Tipe Data:**

  * Memastikan semua data secara eksplisit diubah ke tipe data yang benar (misalnya, `INTEGER`, `NUMERIC`, `TIMESTAMP`).

* **Normalisasi Nilai:**

  * **Geografi:**
    Nama kota dan negara bagian distandardisasi dengan menggabungkannya dengan tabel `master.geography_master` untuk mendapatkan nama kanonis.

  * **Kategori Produk:**
    Nama kategori produk diterjemahkan ke Bahasa Inggris dan distandardisasi menggunakan tabel `reference.product_category_mapping`.

* **Deduplikasi:**

  * Data duplikat dihapus dari beberapa tabel (seperti `customers`) berdasarkan kunci unik untuk memastikan setiap entitas hanya ada satu kali.

---

# 3. Model Analitik (Layer Gold)

Layer ini merupakan produk akhir dari warehouse: tabel yang siap untuk analisis bisnis dan pelaporan. Tabel-tabel ini bersifat "lebar" (*denormalized*) dan dibuat dengan menggabungkan beberapa tabel dari layer silver.

## Tabel yang Dibuat di Layer Gold

1. **`gold.fact_sales_items`**

   * Tujuan: Tabel fakta terperinci, di mana setiap baris mewakili satu item dalam pesanan. Tabel ini menggabungkan data pesanan, produk, penjual, dan pelanggan untuk memungkinkan analisis pendapatan, kinerja produk, dan penjualan geografis.

2. **`gold.fact_order_fulfillment`**

   * Tujuan: Tabel fakta yang berfokus pada logistik, dengan satu baris per pesanan. Tabel ini menghitung metrik seperti waktu pengiriman aktual (`delivery_days_actual`) dan status keterlambatan (`is_late_delivery`), serta menggabungkannya dengan data ulasan untuk mengukur kepuasan pelanggan.

3. **`gold.mart_customer_behavior`**

   * Tujuan: Data mart yang berpusat pada pelanggan, dengan satu baris per pelanggan unik. Tabel ini menghitung metrik penting seperti lifetime value (`LTV`), frekuensi pesanan, dan perilaku pembelian berulang.

4. **`gold.mart_monthly_performance`**

   * Tujuan: Data mart agregat bulanan tingkat tinggi yang dirancang untuk pelaporan eksekutif. Tabel ini melacak metrik utama seperti `total_revenue`, `total_orders`, dan `total_customers` dari waktu ke waktu.