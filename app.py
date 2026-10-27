import streamlit as st
from pypdf import PdfReader

st.set_page_config(page_title="UK Vize Asistanı", page_icon="🇬🇧", layout="centered")

st.title("🇬🇧 UK Vize Başvuru ve Evrak Kontrol Asistanı")
st.markdown("Belgelerinizi yükleyin, İngiltere (UKVI) kurallarına göre anında analiz edin.")

# Çoklu dosya yükleme alanı
uploaded_files = st.file_uploader(
    "Vize için gereken tüm belgeleri yükleyin (Pasaport, Kimlik, Banka Dökümanı, Çalışma Belgesi vb.)", 
    type=["pdf"], 
    accept_multiple_files=True
)

if uploaded_files:
    st.info(f"Toplam {len(uploaded_files)} adet belge yüklendi.")
    
    if st.button("Belgeleri Türüne Göre Analiz Et"):
        
        # Takip edilecek 4 zorunlu kategori
        bulunan_belgeler = {
            "pasaport": False,
            "kimlik": False,
            "calisma": False,
            "banka": False
        }

        raporlar = []

        for file in uploaded_files:
            reader = PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            
            text_lower = text.lower()
            dosya_adi = file.name.lower()
            
            # Belge Türünü Net Kurallarla Ayırt Etme
            belge_turu = "Diğer Belge"
            
            # 1. Önce Sigorta / Poliçe kontrolü (Banka ile karışmaması için ilk sırada)
            if "sigorta" in dosya_adi or "poliçe" in dosya_adi or "police" in dosya_adi or "insurance" in text_lower or "teminat" in text_lower:
                belge_turu = "Sağlık Sigortası / Poliçe"
            
            # 2. Pasaport Kontrolü
            elif "pasaport" in dosya_adi or "passport" in text_lower or "republic of turkey" in text_lower:
                belge_turu = "Pasaport"
                bulunan_belgeler["pasaport"] = True
                
            # 3. Kimlik Kontrolü
            elif "kimlik" in dosya_adi or "nüfus" in text_lower or "identity" in text_lower or "tc kimlik" in text_lower:
                belge_turu = "Kimlik Belgesi"
                bulunan_belgeler["kimlik"] = True
                
            # 4. Banka Hesap Özeti Kontrolü (Sigorta kelimesi içermediğinden emin olarak)
            elif ("bank" in dosya_adi or "hesap özeti" in text_lower or "statement" in text_lower or "bakiye" in text_lower) and "sigorta" not in text_lower:
                belge_turu = "Banka Hesap Özeti"
                bulunan_belgeler["banka"] = True
                
            # 5. Çalışma / Statü Belgesi Kontrolü
            elif "sgk" in dosya_adi or "bordro" in dosya_adi or "çalışma" in text_lower or "maaş" in text_lower or "şirket" in text_lower or "öğrenci" in text_lower:
                belge_turu = "Çalışma / Statü Belgesi"
                bulunan_belgeler["calisma"] = True

            raporlar.append(f"📄 **{file.name}** \(\rightarrow\) Algılanan Tür: *{belge_turu}*")

        # Puanlama Mantığı
        tum_kategoriler_tam_mi = all(bulunan_belgeler.values())
        
        if tum_kategoriler_tam_mi:
            total_score = 100
        else:
            total_score = 10

        # Sonuçları ekranda göster
        st.markdown("---")
        st.subheader("📊 Detaylı UK Vize Uygunluk Raporu")
        st.metric(label="Güncellenmiş Uygunluk Skoru", value=f"%{total_score}")
        
        st.markdown("### 📁 Yüklenen Belgelerin Analizi:")
        for r in raporlar:
            st.write(r)
                
        st.markdown("### 🔍 Zorunlu Evrak Kontrolü:")
        
        kriterler = [
            ("Pasaport", bulunan_belgeler["pasaport"]),
            ("Kimlik Belgesi", bulunan_belgeler["kimlik"]),
            ("Çalışma Durumu / Statü Belgesi", bulunan_belgeler["calisma"]),
            ("Banka Hesap Özeti", bulunan_belgeler["banka"])
        ]
        
        for isim, durum in kriterler:
            if durum:
                st.markdown(f"✅ **{isim}:** Tespit edildi.")
            else:
                st.markdown(f"🔴 **{isim} - GEREKLİ:** Bu belge eksik!")
                
        if not tum_kategoriler_tam_mi:
            st.error("⚠️ Zorunlu belgelerden biri veya birkaçı eksik olduğu için uygunluk skorunuz %10 olarak belirlenmiştir.")
        else:
            st.success("🎉 Harika! Tüm zorunlu ana belge kategorileri eksiksiz tespit edildi.")