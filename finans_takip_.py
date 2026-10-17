import sqlite3
import pandas as pd
import streamlit as st

# Sayfa Konfigürasyonu (Mobil ve Masaüstü Uyumlu)
st.set_page_config(
    page_title="Finansım - Ev Gelir Gider Hesabı",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# DB Bağlantısı ve Kurulumu


def veritabani_kur():
  conn = sqlite3.connect("finans.db")
  cursor = conn.cursor()
  cursor.execute("""
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
    cursor.execute(
        "ALTER TABLE finans ADD COLUMN net_dahil INTEGER DEFAULT 1"
    )
  except sqlite3.OperationalError:
    pass
  conn.commit()
  return conn


conn = veritabani_kur()

# Başlık
st.title("💰 FİNANSIM")
st.caption("Kişisel Finans & Borç Takip Sistemi")

# Verileri Okuma
df = pd.read_sql_query("SELECT * FROM finans", conn)

# Tutar ve Hesaplamalar
if not df.empty:
  # Net dahil sütun kontrolleri
  df["net_dahil"] = df["net_dahil"].fillna(1).astype(int)

  # Kalan borç hesabı (Taksitli Borç ise tutar * kalan_taksit)
  df["kalan_toplam_borc"] = df.apply(
      lambda row: (
          row["tutar"] * row["kalan_taksit"]
          if row["tur"] == "Taksitli Borç"
          else row["tutar"]
      ),
      axis=1,
  )

  # Hesaplama Değişkenleri
  dahil_df = df[df["net_dahil"] == 1]

  genel_borc = dahil_df[
      dahil_df["tur"].isin(
          ["Borç", "Taksitli Borç", "Kredi Kartı Ekstresi", "Kira (Gider)"]
      )
  ]["kalan_toplam_borc"].sum()
  toplam_gelir = dahil_df[
      dahil_df["tur"].isin(["Alacak", "Maaş / Gelir", "Kira (Gelir)"])
  ]["kalan_toplam_borc"].sum()

  taksitli_df = df[(df["tur"] == "Taksitli Borç") & (df["kalan_taksit"] > 0)]
  aylik_taksit_yuku = taksitli_df["tutar"].sum()
  kalan_taksit_borcu = taksitli_df["kalan_toplam_borc"].sum()

  net_durum = toplam_gelir - genel_borc
else:
  genel_borc, toplam_gelir, aylik_taksit_yuku, kalan_taksit_borcu, net_durum = (
      0,
      0,
      0,
      0,
      0,
  )

# --- 1. ÖZET KARTLARI (METRİKLER) ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Genel Borç", f"{genel_borc:,.2f} TL", delta_color="inverse")
col2.metric("Toplam Gelir", f"{toplam_gelir:,.2f} TL")
col3.metric("Aylık Taksit Yükü", f"{aylik_taksit_yuku:,.2f} TL")
col4.metric(
    "Net Durum",
    f"{net_durum:,.2f} TL",
    delta=f"{net_durum:,.2f} TL",
    delta_color="normal" if net_durum >= 0 else "inverse",
)

st.divider()

# --- 2. YENİ İŞLEM EKLE & DÜZENLE (SEKMELER) ---
tab_liste, tab_ekle, tab_islem = st.tabs(
    ["📊 Borç & Gelir Listesi", "➕ Yeni Ekle", "⚙️ Öde / Sil / Güncelle"]
)

with tab_ekle:
  st.subheader("Yeni İşlem Ekle")
  with st.form("yeni_islem_formu", clear_on_submit=True):
    tur = st.selectbox(
        "İşlem Türü",
        [
            "Taksitli Borç",
            "Borç",
            "Kredi Kartı Ekstresi",
            "Kira (Gider)",
            "Maaş / Gelir",
            "Kira (Gelir)",
            "Alacak",
        ],
    )
    aciklama = st.text_input("Açıklama / Kişi / Kurum")
    tutar = st.number_input("Aylık Taksit / İşlem Tutarı (TL)", min_value=0.0)
    toplam_taksit = st.number_input(
        "Toplam Taksit Sayısı", min_value=1, value=1
    )
    kalan_taksit = st.number_input("Kalan Taksit Sayısı", min_value=0, value=1)
    son_odeme = st.text_input("Son Ödeme Tarihi", value="15.11.2026")
    net_dahil = st.checkbox("Net Duruma / Genel Hesaba Dahil Et", value=True)

    submitted = st.form_submit_button("💾 Kaydet")
    if submitted:
      cursor = conn.cursor()
      cursor.execute(
          "INSERT INTO finans (tur, aciklama, tutar, toplam_taksit,"
          " kalan_taksit, son_odeme, net_dahil) VALUES (?, ?, ?, ?, ?, ?, ?)",
          (
              tur,
              aciklama,
              tutar,
              toplam_taksit,
              kalan_taksit,
              son_odeme,
              1 if net_dahil else 0,
          ),
      )
      conn.commit()
      st.success("İşlem başarıyla eklendi!")
      st.rerun()

with tab_liste:
  st.subheader("Tüm Borç ve Gelirleriniz")
  if not df.empty:
    # Kullanıcı canlı onay kutusu seçebilsin
    edited_df = st.data_editor(
        df[[
            "net_dahil",
            "id",
            "tur",
            "aciklama",
            "tutar",
            "toplam_taksit",
            "kalan_taksit",
            "kalan_toplam_borc",
            "son_odeme",
        ]],
        column_config={
            "net_dahil": st.column_config.CheckboxColumn(
                "☑️ Dahil?", default=True
            ),
            "tutar": st.column_config.NumberColumn(
                "Aylık Tutar", format="%.2f TL"
            ),
            "kalan_toplam_borc": st.column_config.NumberColumn(
                "Kalan Toplam Borç", format="%.2f TL"
            ),
        },
        disabled=[
            "id",
            "tur",
            "aciklama",
            "tutar",
            "toplam_taksit",
            "kalan_taksit",
            "kalan_toplam_borc",
            "son_odeme",
        ],
        hide_index=True,
        use_container_width=True,
    )

    # Değişiklikleri Veritabanına Yansıt
    cursor = conn.cursor()
    for index, row in edited_df.iterrows():
      cursor.execute(
          "UPDATE finans SET net_dahil=? WHERE id=?",
          (1 if row["net_dahil"] else 0, row["id"]),
      )
    conn.commit()

with tab_islem:
  if not df.empty:
    selected_id = st.selectbox(
        "İşlem Yapılacak Kaydı Seçin",
        df["id"].tolist(),
        format_func=lambda x: (
            f"ID {x} - {df[df['id']==x]['aciklama'].values[0]} ("
            f"{df[df['id']==x]['tur'].values[0]})"
        ),
    )

    col_btn1, col_btn2 = st.columns(2)

    with col_btn1:
      if st.button("💳 1 Taksit Öde (-1 Taksit)"):
        cursor = conn.cursor()
        k_taksit = df[df["id"] == selected_id]["kalan_taksit"].values[0]
        if k_taksit > 0:
          cursor.execute(
              "UPDATE finans SET kalan_taksit=? WHERE id=?",
              (k_taksit - 1, selected_id),
          )
          conn.commit()
          st.success("Taksit düşüldü!")
          st.rerun()
        else:
          st.warning("Ödenecek taksit yok.")

    with col_btn2:
      if st.button("🗑️ Kaydı Sil", type="primary"):
        cursor = conn.cursor()
        cursor.execute("DELETE FROM finans WHERE id=?", (selected_id,))
        conn.commit()
        st.success("Kayıt silindi!")
        st.rerun()