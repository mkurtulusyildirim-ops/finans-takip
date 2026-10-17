import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk

# Tema Ayarları
ctk.set_appearance_mode("System")  # "System", "Dark", "Light"
ctk.set_default_color_theme("blue")

class FinansTakipUygulamasi(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Kişisel Finans & Borç Takip Sistemi")
        self.geometry("1200x720")
        
        # Veritabanı Kurulumu
        self.veritabani_kur()

        # Ana Düzen (Grid)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SOL MENÜ (KONTROL PANELİ) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(7, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="💰 FİNANSIM", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_ekle = ctk.CTkButton(self.sidebar_frame, text="➕ Yeni İşlem Ekle", command=self.islem_ekle_penceresi)
        self.btn_ekle.grid(row=1, column=0, padx=20, pady=10)

        self.btn_guncelle = ctk.CTkButton(self.sidebar_frame, text="✏️ Seçileni Güncelle", command=self.guncelle_penceresi)
        self.btn_guncelle.grid(row=2, column=0, padx=20, pady=10)

        self.btn_sil = ctk.CTkButton(self.sidebar_frame, text="🗑️ Seçileni Sil", fg_color="#C0392B", hover_color="#962D22", command=self.islem_sil)
        self.btn_sil.grid(row=3, column=0, padx=20, pady=10)

        self.btn_odeme_yap = ctk.CTkButton(self.sidebar_frame, text="💳 Ödeme / Taksit Öde", fg_color="#27AE60", hover_color="#1E8449", command=self.taksit_ode)
        self.btn_odeme_yap.grid(row=4, column=0, padx=20, pady=10)

        # Hepsini Seç / Kaldır Hızlı Butonları
        self.btn_hepsini_sec = ctk.CTkButton(self.sidebar_frame, text="☑️ Hepsini Seç", fg_color="#34495E", hover_color="#2C3E50", command=lambda: self.hepsini_durum_degistir(1))
        self.btn_hepsini_sec.grid(row=5, column=0, padx=20, pady=(20, 5))

        self.btn_hepsini_kaldir = ctk.CTkButton(self.sidebar_frame, text="☐ Hepsini Kaldır", fg_color="#7F8C8D", hover_color="#95A5A6", command=lambda: self.hepsini_durum_degistir(0))
        self.btn_hepsini_kaldir.grid(row=6, column=0, padx=20, pady=5)

        # --- SAĞ TARAF (TABLO VE ÖZET) ---
        self.right_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(1, weight=1)

        # Özet Kartları Üst Kısım
        self.ozet_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.ozet_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        self.ozet_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.lbl_toplam_borc = ctk.CTkLabel(self.ozet_frame, text="Genel Borç: 0.00 TL", font=ctk.CTkFont(size=12, weight="bold"), text_color="#E74C3C")
        self.lbl_toplam_borc.grid(row=0, column=0, padx=5, sticky="ew")

        self.lbl_toplam_alacak = ctk.CTkLabel(self.ozet_frame, text="Toplam Gelir: 0.00 TL", font=ctk.CTkFont(size=12, weight="bold"), text_color="#2ECC71")
        self.lbl_toplam_alacak.grid(row=0, column=1, padx=5, sticky="ew")

        self.lbl_taksit_ozet = ctk.CTkLabel(self.ozet_frame, text="Aylık Taksit: 0.00 TL\nKalan Taksit Borcu: 0.00 TL", font=ctk.CTkFont(size=12, weight="bold"), text_color="#E67E22")
        self.lbl_taksit_ozet.grid(row=0, column=2, padx=5, sticky="ew")

        self.lbl_net_durum = ctk.CTkLabel(self.ozet_frame, text="Net Durum: 0.00 TL", font=ctk.CTkFont(size=13, weight="bold"))
        self.lbl_net_durum.grid(row=0, column=3, padx=5, sticky="ew")

        # Tablo (Treeview) Kısmı
        self.tree_frame = ctk.CTkFrame(self.right_frame)
        self.tree_frame.grid(row=1, column=0, sticky="nsew")
        self.tree_frame.grid_columnconfigure(0, weight=1)
        self.tree_frame.grid_rowconfigure(0, weight=1)

        # Tablo sütunları (Baştaki ☑️ sütunu eklendi)
        sutunlar = ("Secim", "ID", "Tür", "Açıklama / Kişi", "Aylık Tutar", "Toplam Taksit", "Kalan Taksit", "Kalan Toplam Borç", "Son Ödeme")
        self.tree = ttk.Treeview(self.tree_frame, columns=sutunlar, show="headings", selectmode="browse")
        
        for col in sutunlar:
            if col == "Secim":
                self.tree.heading(col, text="☑️ Dahil?")
                self.tree.column(col, width=70, anchor="center")
            elif col == "ID":
                self.tree.heading(col, text=col)
                self.tree.column(col, width=35, anchor="center")
            elif col in ["Kalan Taksit", "Toplam Taksit"]:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=90, anchor="center")
            else:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=120, anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Çift tıklama ve Tıklama Event'leri (Kutucuğa basıldığında işaret değişimi)
        self.tree.bind("<Double-1>", self.toggle_secim)
        self.tree.bind("<space>", self.toggle_secim)

        # Tablo Kaydırma Çubuğu
        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Verileri Listele
        self.verileri_listele()

    def veritabani_kur(self):
        self.conn = sqlite3.connect("finans.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS finans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tur TEXT,
                aciklama TEXT,
                tutar REAL,
                toplam_taksit INTEGER,
                kalan_taksit INTEGER,
                son_odeme TEXT,
                net_dahil INTEGER DEFAULT 1
            )
        """)
        try:
            self.cursor.execute("ALTER TABLE finans ADD COLUMN net_dahil INTEGER DEFAULT 1")
        except sqlite3.OperationalError:
            pass
        self.conn.commit()

    def verileri_listele(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        self.cursor.execute("SELECT id, tur, aciklama, tutar, toplam_taksit, kalan_taksit, son_odeme, net_dahil FROM finans")
        kayitlar = self.cursor.fetchall()

        genel_borc = 0
        toplam_gelir = 0
        aylik_taksit_yuku = 0
        kalan_taksit_toplam_borc = 0

        for kayit in kayitlar:
            k_id, tur, aciklama, aylik_tutar, toplam_t, kalan_t, son_odeme, net_dahil = kayit
            net_dahil = 1 if net_dahil is None else net_dahil
            
            # Kalan Toplam Borç Hesabı
            if tur == "Taksitli Borç":
                kalan_borc = aylik_tutar * (kalan_t if kalan_t > 0 else 0)
            else:
                kalan_borc = aylik_tutar

            # --- Sadece Taksitli Borçlar için Taksit İstatistikleri ---
            if tur == "Taksitli Borç" and kalan_t > 0:
                aylik_taksit_yuku += aylik_tutar
                kalan_taksit_toplam_borc += kalan_borc

            # --- Net Durum ve Borç/Gelir Hesaplamaları ---
            if net_dahil == 1:
                if tur in ["Borç", "Taksitli Borç", "Kredi Kartı Ekstresi", "Kira (Gider)"]:
                    genel_borc += kalan_borc
                elif tur in ["Alacak", "Maaş / Gelir", "Kira (Gelir)"]:
                    toplam_gelir += kalan_borc

            # Sütun başında Checkbox simgesi
            secim_simge = "[☑]" if net_dahil == 1 else "[  ]"

            # Tabloya eklenecek değerler
            gosterim_kayit = (
                secim_simge, k_id, tur, aciklama, f"{aylik_tutar:,.2f} TL", 
                toplam_t, kalan_t, f"{kalan_borc:,.2f} TL", son_odeme
            )
            self.tree.insert("", "end", values=gosterim_kayit)

        # Etiketlerin Güncellenmesi
        self.lbl_toplam_borc.configure(text=f"Genel Borç: {genel_borc:,.2f} TL")
        self.lbl_toplam_alacak.configure(text=f"Toplam Gelir: {toplam_gelir:,.2f} TL")
        self.lbl_taksit_ozet.configure(text=f"Aylık Taksit Yükü: {aylik_taksit_yuku:,.2f} TL\nKalan Taksit Borcu: {kalan_taksit_toplam_borc:,.2f} TL")
        
        net = toplam_gelir - genel_borc
        self.lbl_net_durum.configure(text=f"Net Durum: {net:,.2f} TL", text_color=("#27AE60" if net >= 0 else "#E74C3C"))

    def toggle_secim(self, event=None):
        """Tablodaki satıra tıklanınca kutucuğu açar/kapatır ve hesabı anında günceller"""
        secili = self.tree.selection()
        if not secili:
            return
        
        item_values = self.tree.item(secili)["values"]
        secili_id = item_values[1]
        mevcut_simge = item_values[0]

        # Simgeyi ve DB değerini değiştir
        yeni_durum = 0 if mevcut_simge == "[☑]" else 1
        
        self.cursor.execute("UPDATE finans SET net_dahil=? WHERE id=?", (yeni_durum, secili_id))
        self.conn.commit()
        self.verileri_listele()

    def hepsini_durum_degistir(self, durum):
        """Tüm kayıtların dahil edilme durumunu toplu değiştirir"""
        self.cursor.execute("UPDATE finans SET net_dahil=?", (durum,))
        self.conn.commit()
        self.verileri_listele()

    def islem_ekle_penceresi(self):
        self.pencere_ac("Yeni İşlem Ekle", self.islem_kaydet)

    def islem_kaydet(self, pencere, tur, aciklama, tutar, toplam_taksit, kalan_taksit, son_odeme, net_dahil):
        try:
            tutar = float(tutar.replace(',', '.'))
            toplam_taksit = int(toplam_taksit)
            kalan_taksit = int(kalan_taksit)
        except ValueError:
            messagebox.showerror("Hata", "Lütfen tutar ve taksit kısımlarına geçerli sayılar giriniz!")
            return

        self.cursor.execute("INSERT INTO finans (tur, aciklama, tutar, toplam_taksit, kalan_taksit, son_odeme, net_dahil) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (tur, aciklama, tutar, toplam_taksit, kalan_taksit, son_odeme, net_dahil))
        self.conn.commit()
        pencere.destroy()
        self.verileri_listele()
        messagebox.showinfo("Başarılı", "İşlem başarıyla eklendi.")

    def guncelle_penceresi(self):
        secili = self.tree.selection()
        if not secili:
            messagebox.showwarning("Uyarı", "Lütfen güncellemek istediğiniz satırı seçin.")
            return
        
        secili_id = self.tree.item(secili)["values"][1]
        self.cursor.execute("SELECT * FROM finans WHERE id=?", (secili_id,))
        veri = self.cursor.fetchone()

        self.pencere_ac("İşlem Güncelle", lambda p, t, a, tu, tt, kt, so, nd: self.islem_guncelle_db(p, veri[0], t, a, tu, tt, kt, so, nd), veri)

    def islem_guncelle_db(self, pencere, id_degeri, tur, aciklama, tutar, toplam_taksit, kalan_taksit, son_odeme, net_dahil):
        try:
            tutar = float(str(tutar).replace(',', '.'))
            toplam_taksit = int(toplam_taksit)
            kalan_taksit = int(kalan_taksit)
        except ValueError:
            messagebox.showerror("Hata", "Lütfen tutar ve taksit kısımlarına geçerli sayılar giriniz!")
            return

        self.cursor.execute("""
            UPDATE finans SET tur=?, aciklama=?, tutar=?, toplam_taksit=?, kalan_taksit=?, son_odeme=?, net_dahil=? WHERE id=?
        """, (tur, aciklama, tutar, toplam_taksit, kalan_taksit, son_odeme, net_dahil, id_degeri))
        self.conn.commit()
        pencere.destroy()
        self.verileri_listele()
        messagebox.showinfo("Başarılı", "İşlem güncellendi.")

    def islem_sil(self):
        secili = self.tree.selection()
        if not secili:
            messagebox.showwarning("Uyarı", "Lütfen silmek istediğiniz satırı seçin.")
            return
        
        secili_id = self.tree.item(secili)["values"][1]
        if messagebox.askyesno("Onay", f"ID {secili_id} numaralı kaydı silmek istediğinize emin misiniz?"):
            self.cursor.execute("DELETE FROM finans WHERE id=?", (secili_id,))
            self.conn.commit()
            self.verileri_listele()
            messagebox.showinfo("Başarılı", "Kayıt silindi.")

    def taksit_ode(self):
        secili = self.tree.selection()
        if not secili:
            messagebox.showwarning("Uyarı", "Lütfen taksiti ödenecek kaydı seçin.")
            return
        
        secili_id = self.tree.item(secili)["values"][1]
        self.cursor.execute("SELECT kalan_taksit FROM finans WHERE id=?", (secili_id,))
        kalan_taksit = self.cursor.fetchone()[0]

        if kalan_taksit > 0:
            yeni_kalan = kalan_taksit - 1
            self.cursor.execute("UPDATE finans SET kalan_taksit=? WHERE id=?", (yeni_kalan, secili_id))
            self.conn.commit()
            self.verileri_listele()
            messagebox.showinfo("Başarılı", f"1 taksit ödemesi düşüldü. Kalan Taksit: {yeni_kalan}")
        else:
            messagebox.showinfo("Bilgi", "Bu kalemin ödenecek taksiti kalmamıştır.")

    def pencere_ac(self, baslik, kaydet_komutu, veri=None):
        win = ctk.CTkToplevel(self)
        win.title(baslik)
        win.geometry("430x620")
        win.grab_set()

        scroll_frame = ctk.CTkScrollableFrame(win, width=390, height=590)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(scroll_frame, text=baslik, font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(5, 15))

        # Tür Seçimi
        ctk.CTkLabel(scroll_frame, text="İşlem Türü:").pack(anchor="w", padx=20)
        tur_var = ctk.StringVar(value=veri[1] if veri else "Taksitli Borç")
        tur_menu = ctk.CTkComboBox(scroll_frame, values=["Taksitli Borç", "Borç", "Kredi Kartı Ekstresi", "Kira (Gider)", "Maaş / Gelir", "Kira (Gelir)", "Alacak"], variable=tur_var)
        tur_menu.pack(fill="x", padx=20, pady=5)

        # Açıklama
        ctk.CTkLabel(scroll_frame, text="Açıklama / Kişi / Kurum:").pack(anchor="w", padx=20)
        entry_aciklama = ctk.CTkEntry(scroll_frame)
        entry_aciklama.pack(fill="x", padx=20, pady=5)
        if veri: entry_aciklama.insert(0, str(veri[2]))

        # Tutar
        ctk.CTkLabel(scroll_frame, text="Aylık Taksit / İşlem Tutarı (TL):").pack(anchor="w", padx=20)
        entry_tutar = ctk.CTkEntry(scroll_frame)
        entry_tutar.pack(fill="x", padx=20, pady=5)
        if veri: entry_tutar.insert(0, str(veri[3]))

        # Toplam Taksit
        ctk.CTkLabel(scroll_frame, text="Toplam Taksit Sayısı (Tek çekimse 1):").pack(anchor="w", padx=20)
        entry_toplam_taksit = ctk.CTkEntry(scroll_frame)
        entry_toplam_taksit.pack(fill="x", padx=20, pady=5)
        if veri: entry_toplam_taksit.insert(0, str(veri[4]))
        else: entry_toplam_taksit.insert(0, "1")

        # Kalan Taksit
        ctk.CTkLabel(scroll_frame, text="Kalan Taksit Sayısı:").pack(anchor="w", padx=20)
        entry_kalan_taksit = ctk.CTkEntry(scroll_frame)
        entry_kalan_taksit.pack(fill="x", padx=20, pady=5)
        if veri: entry_kalan_taksit.insert(0, str(veri[5]))
        else: entry_kalan_taksit.insert(0, "1")

        # Son Ödeme Tarihi
        ctk.CTkLabel(scroll_frame, text="Son Ödeme / Vade Tarihi:").pack(anchor="w", padx=20)
        entry_son_odeme = ctk.CTkEntry(scroll_frame)
        entry_son_odeme.pack(fill="x", padx=20, pady=5)
        if veri: entry_son_odeme.insert(0, str(veri[6]))
        else: entry_son_odeme.insert(0, "15.11.2026")

        # Net Duruma Dahil Etme Onay Kutusu (Aynen Korundu)
        net_dahil_var = ctk.IntVar(value=veri[7] if (veri and len(veri) > 7 and veri[7] is not None) else 1)
        chk_net_dahil = ctk.CTkCheckBox(scroll_frame, text="Net Duruma / Genel Hesaba Dahil Et", variable=net_dahil_var)
        chk_net_dahil.pack(anchor="w", padx=20, pady=15)

        # Kaydet Butonu
        kaydet_btn = ctk.CTkButton(scroll_frame, text="💾 Kaydet", font=ctk.CTkFont(weight="bold"), command=lambda: kaydet_komutu(
            win, 
            tur_var.get(), 
            entry_aciklama.get(), 
            entry_tutar.get(), 
            entry_toplam_taksit.get(), 
            entry_kalan_taksit.get(), 
            entry_son_odeme.get(),
            net_dahil_var.get()
        ))
        kaydet_btn.pack(pady=15, fill="x", padx=20)

if __name__ == "__main__":
    app = FinansTakipUygulamasi()
    app.mainloop()