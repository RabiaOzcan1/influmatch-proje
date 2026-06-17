import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Sayfa Yapılandırması (Her zaman en üstte olmalı)
st.set_page_config(page_title="InfluMatch AI Pro v9.0 🚀", layout="wide")

# 2. Oturum Durumu Kontrolü (Giriş Yapıldı mı?)
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# Giriş Yapılmadıysa SADECE Giriş Ekranını Göster
if not st.session_state['logged_in']:
    st.title("🔐 Giriş Paneli")
    
    with st.form("login_form"):
        user = st.text_input("Kullanıcı Adı", placeholder="admin")
        pw = st.text_input("Şifre", type="password", placeholder="1234")
        submit_login = st.form_submit_button("Sisteme Giriş Yap 🚀")
        
        if submit_login:
            if user == "admin" and pw == "1234":
                st.session_state['logged_in'] = True
                st.rerun()  # Sayfayı hemen tazele
            else:
                st.error("❌ Hatalı kullanıcı adı veya şifre!")
                
    st.stop()  # Giriş yapılmadıysa uygulamanın kalan kodlarını asla yürütme!

# --- BURADAN SONRASI SADECE GİRİŞ YAPILDIYSA ÇALIŞIR ---
st.success("🔓 Başarıyla Giriş Yapıldı! Hoş geldiniz.")

# Veri setini yükleme ve güvenli hale getirme
@st.cache_data
def load_and_clean_data():
    try:
        raw_df = pd.read_csv("influencers.csv", on_bad_lines='skip')
        df = raw_df.copy()
        
        # Sayısal temizlikler
        df['takipci'] = pd.to_numeric(df['takipci'].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce').fillna(0)
        df['etkilesim'] = pd.to_numeric(df['etkilesim'].astype(str).str.replace(',', '.'), errors='coerce').fillna(5.0)
        
        # Skorlama motoru
        df['G'] = (df['etkilesim'] * 4 + 50).clip(60, 98).round(1)   
        df['E'] = (df['etkilesim'] * 5 + 40).clip(55, 99).round(1)   
        df['O'] = (100 - df['takipci'] / 1000000).clip(70, 96).round(1) 
        df['S'] = (df['etkilesim'] * 3 + 65).clip(65, 95).round(1)   
        df['SMS'] = (0.40 * df['G'] + 0.30 * df['E'] + 0.20 * df['O'] + 0.10 * df['S']).round(1)
        return df
    except Exception as e:
        st.error(f"CSV Dosyası Yüklenemedi: {e}")
        return pd.DataFrame()

df = load_and_clean_data()

if df.empty:
    st.warning("⚠️ Lütfen 'influencers.csv' dosyanızın reposunda mevcut olduğundan emin olun.")
    st.stop()

# Sosyal Medya Link Üretici
def get_social_link(name, platform):
    clean_name = name.lower().replace(" ", "").replace("ı", "i").replace("ö", "o").replace("ü", "u").replace("ç", "c").replace("ş", "s").replace("ğ", "g")
    if "tiktok" in platform.lower(): return f"https://www.tiktok.com/@{clean_name}"
    elif "instagram" in platform.lower(): return f"https://instagram.com/{clean_name}"
    elif "youtube" in platform.lower(): return f"https://youtube.com/@{clean_name}"
    return "https://google.com"

# Eyalet Kontrolleri (State)
if 'advisor_mode' not in st.session_state: st.session_state['advisor_mode'] = None 
if 'pre_selected_type' not in st.session_state: st.session_state['pre_selected_type'] = "Tümü"

# --- EKRAN 1: AI MENTOR SEÇİMİ ---
if st.session_state['advisor_mode'] is None:
    st.title("🧙‍♂️ InfluMatch AI Mentor")
    st.subheader("Kampanya stratejinizi nasıl belirlemek istersiniz?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🤖 AI Danışman Modu (Anketi Başlat)", use_container_width=True):
            st.session_state['advisor_mode'] = True
            st.rerun()
    with col2:
        if st.button("🎛️ Manuel Filtreleme / Doğrudan Giriş", use_container_width=True):
            st.session_state['advisor_mode'] = False
            st.rerun()

# --- EKRAN 2: ANKET ---
elif st.session_state['advisor_mode'] is True:
    st.title("📊 Kampanya Strateji Testi")
    with st.form("advisor_survey"):
        q1 = st.selectbox("1. Kampanyanın temel amacı nedir?", ["Marka bilinirliğini artırmak", "Ürün/hizmet satışı (conversion)", "Güven oluşturmak", "Niş bir kitleye ulaşmak"])
        q2 = st.selectbox("2. Influencer iş birliği için bütçeniz nedir?", ["Çok yüksek", "Orta", "Düşük", "Çok düşük / barter"])
        q3 = st.selectbox("3. Ulaşmak istediğiniz kitle ne kadar geniş?", ["Çok geniş", "Geniş ama belirli", "Spesifik ilgi alanı", "Çok niş"])
        q4 = st.selectbox("4. Hangisi sizin için daha önemli?", ["Maksimum erişim", "Dengeli", "Yüksek etkileşim", "Güçlü birebir bağ"])
        
        if st.form_submit_button("🧠 Analiz Et ve Sonuçları Uygula"):
            score = {"Mega": 0, "Macro": 0, "Micro": 0, "Nano": 0}
            ans_str = (q1 + q2 + q3 + q4).lower()
            if any(x in ans_str for x in ["yüksek", "geniş", "bilinirlik"]): score["Mega"] += 5
            if any(x in ans_str for x in ["orta", "denge"]): score["Macro"] += 5
            if any(x in ans_str for x in ["satış", "düşük", "etkileşim"]): score["Micro"] += 5
            if any(x in ans_str for x in ["barter", "niş", "bağ"]): score["Nano"] += 5
            
            winner = max(score, key=score.get)
            mapping = {
                "Mega": "🔴 1. MEGA INFLUENCER (1M+ takipçi)",
                "Macro": "🟠 2. MACRO INFLUENCER (100K – 1M)",
                "Micro": "🟡 3. MICRO INFLUENCER (10K – 100K)",
                "Nano": "🟢 4. NANO INFLUENCER (10K ve Altı)"
            }
            st.session_state['pre_selected_type'] = mapping[winner]
            st.session_state['advisor_mode'] = False
            st.rerun()

# --- EKRAN 3: ANA PANEL ---
else:
    st.sidebar.title("🎛️ Kontrol Paneli")
    if st.sidebar.button("🔙 Ana Menüye Dön"):
        st.session_state['advisor_mode'] = None
        st.session_state['pre_selected_type'] = "Tümü"
        st.rerun()
        
    st.sidebar.divider()
    kategoriler = ["Tümü"] + sorted(list(df["sektor"].dropna().unique()))
    secilen_kategori = st.sidebar.selectbox("🎯 Sektör Filtresi:", kategoriler)
    
    segmentler = ["Tümü"] + sorted(list(df["tip"].dropna().unique()))
    default_index = 0
    if st.session_state['pre_selected_type'] in segmentler:
        default_index = segmentler.index(st.session_state['pre_selected_type'])
        
    secilen_segment = st.sidebar.selectbox("📊 Segment Filtresi:", segmentler, index=default_index)
    st.session_state['pre_selected_type'] = secilen_segment
    
    st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
    if st.sidebar.button("🚪 Güvenli Çıkış"):
        st.session_state['logged_in'] = False
        st.rerun()

    f_df = df.copy()
    if secilen_kategori != "Tümü": f_df = f_df[f_df["sektor"] == secilen_kategori]
    if st.session_state['pre_selected_type'] != "Tümü": f_df = f_df[f_df["tip"] == st.session_state['pre_selected_type']]

    tab1, tab2, tab3, tab4 = st.tabs(["💎 Influencer Vitrini", "🧙‍♂️ Akıllı Sihirbaz", "📈 Veri Analizi", "🤖 AI Asistan & Sihirbaz"])
    
    with tab1:
        st.header("✨ Influencer Arama ve Portföy Vitrini")
        search_query = st.text_input("🔍 İsim ile Manuel Arama Yapın:")
        vitrin_df = df[df["ad"].astype(str).str.contains(search_query, case=False, na=False)] if search_query else f_df
        
        if vitrin_df.empty: st.warning("⚠️ Kriterlere uygun aday bulunamadı.")
        else:
            cols = st.columns(3)
            for index, row in vitrin_df.reset_index().iterrows():
                with cols[index % 3]:
                    with st.container(border=True):
                        st.subheader(f"👤 {row['ad']}")
                        st.caption(f"📱 {row['platform']} | 🏷️ {row['tip']} | 🎯 {row['sektor']}")
                        st.markdown(f"🎯 **Smart-Match Skoru: {row['SMS']}/100**")
                        st.progress(float(row['SMS']/100))
                        m1, m2 = st.columns(2)
                        m1.metric("👥 Takipçi", f"{int(row['takipci']):,}")
                        m2.metric("⚡ Etkileşim", f"%{row['etkilesim']}")
                        st.link_button("🌐 Profili Gör", get_social_link(row['ad'], row['platform']), use_container_width=True)

    with tab2:
        st.header("🧠 Akıllı Eşleştirme Motoru")
        with st.form("wizard_form_v8"):
            w_sektor = st.selectbox("🎯 Hedef Sektör", df["sektor"].unique())
            w_hedef = st.radio("🚀 Kampanya Amacı", ["Satış Yapmak", "Bilinirlik Kazanmak"])
            w_tipler = st.multiselect("📊 İstenilen Segmentler", list(df["tip"].unique()), default=list(df["tip"].unique()))
            submit_wizard = st.form_submit_button("⚡ Aday Performans Kıyaslamasını Başlat")

        if submit_wizard:
            res = df[(df["sektor"] == w_sektor) & (df["tip"].isin(w_tipler))]
            if len(res) >= 1:
                best = res.sort_values(by="SMS", ascending=False).iloc[0]
                st.success(f"🥇 EN UYGUN ADAY: {best['ad']} (Smart-Match Skoru: {best['SMS']}/100)")
            else:
                st.warning("⚠️ Seçilen kriterlere uygun influencer bulunamadı.")

    with tab3:
        st.header("📈 Matematiksel Dağılım ve Matris Analizi")
        if not f_df.empty:
            fig = px.scatter(f_df, x="takipci", y="SMS", color="sektor" if len(f_df["sektor"].unique()) > 1 else None, size="etkilesim", hover_name="ad", title="Takipçi vs. SMS")
            st.plotly_chart(fig, use_container_width=True)
        st.dataframe(f_df, use_container_width=True)

    # --- TAB 4: MOD SEÇİMLİ, BÜTÇE DUYARLI VE AI INSIGHT DESTEKLİ MOTOR ---
    with tab4:
        st.header("🤖 InfluMatch Akıllı AI Asistanı & Sihirbazı")
        
        ai_modu = st.radio(
            "💡 Yapay Zekayı Hangi Amaçla Kullanmak İstersiniz?",
            options=["🎯 Reklam Senaryosu ve Influencer Önerisi Al", "⚖️ Sadece Yasal Soru Sor (Mevzuat Danışmanı)"],
            horizontal=True,
            key="ai_mode_selector"
        )
        
        st.divider()
        
        # MOD 1: REKLAM SENARYOSU VE YAPAY ZEKA SİHİRBAZI
        if ai_modu == "🎯 Reklam Senaryosu ve Influencer Önerisi Al":
            st.markdown("Kampanya hedeflerinizi yazın. Sistem, seçtiğiniz bütçeye ve sektöre göre verileri süzerek **En İdeal** ve **En Riskli** adayları belirler, senaryolar hazırlar.")
            
            kampanya_sektoru = st.selectbox("🎯 Reklam Yapacağınız Sektör Nedir?", options=sorted(list(df["sektor"].unique())), key="ai_sector")
            
            kampanya_butcesi = st.selectbox(
                "💰 Kampanya Bütçeniz Nedir?",
                options=["Düşük Bütçe (Nano)", "Orta-Düşük Bütçe (Nano & Micro)", "Orta Bütçe (Micro)", "Orta-Yüksek Bütçe (Macro & Mega)", "Yüksek Bütçe (Mega)"],
                key="ai_budget"
            )
            
            user_prompt = st.text_area("📝 Kampanya Detaylarını ve İsteklerinizi Yazın:", placeholder="Örn: Yeni kozmetik serimiz için bütçemize uygun reklam senaryoları ve isim önerileri...", key="ai_prompt")
            
            if st.button("🚀 Yapay Zeka Analizini Başlat", key="groq_senaryo_start"):
                if not user_prompt:
                    st.warning("⚠️ Lütfen kampanya detaylarını boş bırakmayın.")
                else:
                    with st.spinner("🧠 Yapay zeka veritabanını tarıyor, bütçeyi optimize ediyor ve AI Insight raporunu hazırlıyor..."):
                        try:
                            import json
                            from groq import Groq
                            
                            # Sektör filtreleme
                            ai_df = df[df["sektor"].astype(str).str.contains(kampanya_sektoru, case=False, na=False)].copy()
                            
                            if ai_df.empty:
                                st.error(f"❌ Veri tabanında '{kampanya_sektoru}' sektörüne ait hiçbir influencer bulunamadı.")
                            else:
                                bütçe_notu = ""
                                # Bütçeye göre tip filtreleme
                                if "Düşük Bütçe (Nano)" in kampanya_butcesi:
                                    temp_df = ai_df[ai_df["tip"].astype(str).str.contains("Nano", case=False, na=False)]
                                    if temp_df.empty:
                                        ai_df = ai_df[ai_df["tip"].astype(str).str.contains("Micro", case=False, na=False)]
                                        bütçe_notu = "⚠️ Not: Sektörde 'Nano' aday bulunmadığından otomatik 'Micro' segmentine geçildi."
                                    else:
                                        ai_df = temp_df
                                elif "Orta-Düşük Bütçe (Nano & Micro)" in kampanya_butcesi:
                                    ai_df = ai_df[ai_df["tip"].astype(str).str.contains("Nano|Micro", case=False, na=False)]
                                elif "Orta Bütçe (Micro)" in kampanya_butcesi:
                                    ai_df = ai_df[ai_df["tip"].astype(str).str.contains("Micro", case=False, na=False)]
                                elif "Orta-Yüksek Bütçe (Macro & Mega)" in kampanya_butcesi:
                                    ai_df = ai_df[ai_df["tip"].astype(str).str.contains("Macro|Mega", case=False, na=False)]
                                elif "Yüksek Bütçe (Mega)" in kampanya_butcesi:
                                    ai_df = ai_df[ai_df["tip"].astype(str).str.contains("Mega", case=False, na=False)]

                                api_key = st.secrets.get("GROQ_API_KEY", None)
                                if not api_key:
                                    st.error("❌ `secrets.toml` içerisinde GROQ_API_KEY anahtarı bulunamadı!")
                                else:
                                    client = Groq(api_key=api_key)
                                    veri_ozeti = ai_df[['ad', 'sektor', 'tip', 'platform', 'takipci', 'etkilesim', 'SMS']].to_string(index=False)
                                    
                                    sistem_talimati = f"""
                                    Sen uzman bir dijital pazarlama direktörü ve veri analistisin. Kullanıcı '{kampanya_sektoru}' alanında kampanya yapıyor.
                                    Aşağıdaki veri kümesinde yer alan influencer'ların 'SMS' sütunu onların Smart-Match (Akıllı Eşleşme) skorudur.
                                    
                                    GÖREV:
                                    1. Verilen listeden SMS skoru, etkileşimi ve hedef kitle uyumu en yüksek olan 'En İdeal Adayı' seç.
                                    2. Verilen listeden veya genel veri tabanından bu senaryoya, bütçeye veya sektöre en az uyum sağlayan 'En Riskli / Uygun Olmayan Adayı' seç.
                                    3. Seçilen ideal adaylara özel kreatif video senaryoları yaz.
                                    4. Türkiye Cumhuriyeti Ticaret Bakanlığı mevzuat uyarılarını ekle.
                                    
                                    Senden çıktıyı MUTLAKA şu JSON formatında vermeni bekliyorum. JSON dışında hiçbir metin yazma:
                                    {{
                                        "en_ideal_aday": "En yüksek uyumlu influencer ismi ve Smart-Match Skoru",
                                        "en_ideal_neden": "Bu adayın portföy, etkileşim oranı ve SMS skoru baz alınarak neden en iyi tercih olduğunun matematiksel açıklaması",
                                        "en_riskli_aday": "Bu kampanya/bütçe için en uygunsuz olan influencer ismi ve Smart-Match Skoru",
                                        "en_riskli_neden": "Bu adayın bütçe aşımı, alakasız sektör veya düşük etkileşim nedeniyle neden riskli olduğunun açıklaması",
                                        "kreatif_senaryolar": "Önerilen ideal isimlerin tarzına uygun, Instagram Reels ve TikTok odaklı kreatif senaryolar",
                                        "yasal_mevzuat": "Ticaret Bakanlığı kurallarına göre reklam etiketleme ve kozmetik/sağlık beyanı kısıtlamaları kuralları"
                                    }}

                                    Veri kümesi:
                                    {veri_ozeti}

                                    Kullanıcı İsteği:
                                    "{user_prompt}"
                                    """
                                    
                                    completion = client.chat.completions.create(
                                        model="llama-3.3-70b-versatile",
                                        messages=[{"role": "user", "content": sistem_talimati}],
                                        temperature=0.2,
                                        response_format={"type": "json_object"}
                                    )
                                    
                                    # JSON Ayrıştırma
                                    cevap_json = json.loads(completion.choices[0].message.content)
                                    
                                    st.success("🎉 Yapay Zeka Sihirbaz Analizi Tamamlandı!")
                                    if bütçe_notu: st.warning(bütçe_notu)
                                    st.markdown("---")
                                    
                                    # --- GÖRSEL AI INSIGHT BÖLÜMÜ ---
                                    st.subheader("🎯 AI Insight: Sihirbaz Eşleştirmesi")
                                    col_iyi, col_kotu = st.columns(2)
                                    
                                    with col_iyi:
                                        st.success(f"🏆 **En İdeal Aday: {cevap_json.get('en_ideal_aday')}**")
                                        st.info(cevap_json.get('en_ideal_neden'))
                                        
                                    with col_kotu:
                                        st.error(f"⚠️ **En Riskli / Uygun Olmayan: {cevap_json.get('en_riskli_aday')}**")
                                        st.warning(cevap_json.get('en_riskli_neden'))
                                        
                                    st.markdown("---")
                                    
                                    # --- SENARYOLAR VE YASAL BÖLÜM ---
                                    st.subheader("🎬 Kreatif Video Senaryoları")
                                    st.markdown(cevap_json.get('kreatif_senaryolar'))
                                    
                                    st.markdown("---")
                                    st.subheader("⚖️ Hukuki Mevzuat ve Yasal Zorunluluklar")
                                    st.markdown(cevap_json.get('yasal_mevzuat'))
                                    
                        except Exception as e:
                            st.error(f"Hata: {e}")
                            
        # MOD 2: SADECE YASAL MEVZUAT DANIŞMANI
        else:
            st.markdown("### ⚖️ T.C. Ticaret Bakanlığı Reklam ve Influencer Mevzuat Danışmanı")
            st.markdown("Gizli reklam yasakları, sosyal medyada hashtag kullanımı (`#işbirliği`), sponsorlu içerik kuralları veya ceza maddeleri hakkında merak ettiğiniz her şeyi sorun.")
            
            yasal_soru = st.text_area("❓ Sormak İstediğiniz Yasal Soru/Mevzuat Nedir?", placeholder="Örn: Instagram hikayelerinde iş birliği etiketi nereye konulmalı, uymamanın cezası nedir?", key="legal_query_box")
            
            if st.button("⚖️ Kanun ve Mevzuata Göre İncele", key="groq_yasal_start"):
                if not yasal_soru:
                    st.warning("⚠️ Lütfen yasal sorunuzu buraya yazın.")
                else:
                    with st.spinner("📜 Resmi Gazete ve Ticaret Bakanlığı kılavuzları taranıyor..."):
                        try:
                            from groq import Groq
                            api_key = st.secrets.get("GROQ_API_KEY", None)
                            if not api_key:
                                st.error("❌ GROQ_API_KEY bulunamadı!")
                            else:
                                client = Groq(api_key=api_key)
                                
                                yasal_mesaj = f"""
                                Sen Türkiye Cumhuriyeti Ticaret Bakanlığı Reklam Kurulu mevzuatlarına, Influencer Bilgilendirme Kılavuzu'na ve Reklam Kanunu'na tamamen hakim bir hukuk ve dijital pazarlama danışmanısın.
                                
                                Kullanıcı sana şu soruyu sordu:
                                "{yasal_soru}"
                                
                                Lütfen bu soruyu şu kurallara göre cevapla:
                                1. Net ve yasal maddelere dayanan (Örn: Sosyal Medya Etkileyicileri Tarafından Yapılan Ticari Reklam ve Haksız Ticari Uygulamalar Haksız Ticari Uygulamalar Hakkında Kılavuz) bilgiler ver.
                                2. #İşbirliği, #Reklam gibi etiketlerin hangi platformda (YouTube, Instagram, TikTok vb.) nasıl, hangi boyutta ve nerede konumlandırılması gerektiğini açıkla.
                                3. Olası ihlal durumunda Reklam Kurulu'nun uygulayabileceği idari para cezası veya durdurma cezası risklerinden bahset.
                                4. Tamamen Türkçe ve profesyonel bir hukuki/danışmanlık dili kullan.
                                """
                                
                                completion = client.chat.completions.create(
                                    model="llama-3.3-70b-versatile",
                                    messages=[{"role": "user", "content": yasal_mesaj}],
                                    temperature=0.1
                                )
                                st.success("⚖️ Hukuki Mevzuat Analizi Tamamlandı!")
                                st.markdown("---")
                                st.markdown(completion.choices[0].message.content)
                        except Exception as e:
                            st.error(f"AI Bağlantı Hatası: {e}")
