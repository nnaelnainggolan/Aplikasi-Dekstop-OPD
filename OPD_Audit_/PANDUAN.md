# Audit OPD v2.0
Ekstrak seluruh file ke folder aplikasi audit sebelumnya atau folder baru. audit_config.json lama tetap digunakan jika tersedia; jika tidak, digunakan audit_config.example.json. Python 3.10+ dengan tkinter (instalasi standar Windows), tanpa paket tambahan.

## Menjalankan
Klik JALANKAN_AUDIT.bat. Popup meminta folder serta tanggal mulai/akhir (YYYY-MM-DD), termasuk kedua tanggal batas. Pilih folder aktual melalui tombol, misalnya SEPTEMBER. Setelah selesai, HTML terbuka otomatis. Semua hasil berada di hasil_audit/folder waktu terbaru.
Alternatif tanpa popup: python periksa_excel.py --folder "G:\My Drive\Latihan OPD Automation\SEPTEMBER" --start 2026-09-01 --end 2026-09-30

Nama file harus memuat tanggal seperti 17 SEPTEMBER 2026.xlsx. Tanggal berdasarkan nama file, bukan isi gambar. File dengan tambahan (1) tetap diperiksa dan ditandai duplikat tanggal. Tanggal tanpa file dan nama tidak dikenali tercantum di Peringatan cakupan. File sumber tidak diubah. Tidak masuk subfolder.

## Hasil HTML
Tombol tanggal kecil dan tersusun dalam beberapa baris. Klik tanggal untuk melihat detail satu file pada halaman yang sama. Jumlah baris detail tetap bisa memerlukan scroll; tidak diperkecil sampai sulit dibaca. Beberapa file pada tanggal sama ditandai *. Hijau berarti slot wajib terisi/terkonfirmasi; merah ada yang kosong; kuning ada ketidakpastian atau masalah file/sheet tambahan.
Setiap baris memiliki alasan dan, jika tersedia, tautan gambar. Pilih Belum ditinjau / Perlu diambil ulang / Sudah dicek — aman / Sudah dilengkapi. Dua pilihan terakhir menyembunyikan baris dari filter masalah, namun tidak mengubah hasil audit asli maupun file Excel. Hilangkan centang filter untuk membatalkan konfirmasi.
Catatan disimpan di localStorage bila browser mengizinkan. Simpan catatan JSON untuk cadangan; gunakan Muat catatan pada folder/rentang sama. Catatan tidak disinkronkan antar komputer. Konfirmasi lama hanya berlaku untuk file sumber dengan isi identik; jika isi workbook berubah, slot perlu dinilai ulang. File Excel hasil audit tidak diperbarui oleh pilihan HTML; lakukan audit ulang untuk mengecek perubahan workbook nyata. Folder gambar harus tetap bersama hasil.html.

## Aturan lebih fleksibel
Broadband: area baris 2–16, Metro: 18–33, posisi awal kolom A–W. Minimal 80% tinggi gambar harus berada pada satu area. Ukuran baris aktual serta offset diperhitungkan. Dukungan one-cell, two-cell, dan absolute vertical anchors. Gambar bukan wajib tepat A2/A18. Gambar tunggal dengan media terbaca -> terisi. Tidak ada gambar dan tidak ambigu -> kosong. Gambar ganda, melintasi dua area, media hilang/eksternal, atau penempatan tidak terbaca -> perlu dicek dengan alasan spesifik. Bentuk dekoratif tanpa gambar tidak menyebabkan seluruh sheet perlu dicek.
Gambar di luar kedua area diabaikan. Gambar yang mulai kolom X ke kanan diabaikan. Pada absolute anchor, pengelompokan berdasarkan posisi vertikal; tinjau jika ada gambar dekoratif sejajar dengan area laporan. Posisi dua gambar dalam grup dianggap ambigu. Gambar dalam sel/rich data belum didukung dan ditandai perlu dicek.
Aturan ini mengecek keberadaan/penempatan, bukan keaslian, tanggal, atau isi screenshot. Logo di area slot bisa ikut dihitung. Screenshot No Data dihitung terisi, bukan berarti koneksi normal. Penilaian aman hanya terkait kelengkapan slot.

## Excel hasil
slot_belum_terisi.xlsx hanya berisi File laporan, Sheet/project, Jaringan, Keterangan. Hanya slot yang kosong atau sheet wajib belum tersedia yang dicantumkan. Tidak memuat slot terisi, belum pasti, atau file gagal dibaca. Karena itu Excel kosong bukan bukti semua lengkap: lihat peringatan HTML terlebih dahulu. Jika tidak ada kekurangan pasti, hanya ada baris judul.

## Pemetaan
Mengikuti config 36 project/71 slot, HQ Metro saja. Ubah projects/aliases jika nama sheet atau cakupan berbeda. Batas area saat ini mengikuti template standar; slots pada config lama tidak mengubah area v2.0. Sheet tambahan tidak langsung diasumsikan kosong, tetapi dicatat di HTML.
