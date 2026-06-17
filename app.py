import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Sayfa Yapılandırması
st.set_page_config(page_title="InfluMatch AI Pro v9.0 🚀", layout="wide")

# 2. Oturum Durumu Kontrolü
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("🔐 Giriş Paneli")
    with st.form("login_form"):
        user = st.text_input("Kullanıcı Adı", placeholder="admin")
        pw = st.text_input("Şifre", type="password", placeholder="1234")
        submit_login = st.form_submit_button("Sisteme Giriş Yap 🚀")
        if submit_login:
            if user == "admin" and pw == "1234":
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("❌ Hatalı kullanıcı adı veya şifre!")
    st.stop()

# Veri setini yükleme ve temizleme
@st.cache_data
def load_and_clean_data():
    try:
        raw_df = pd.read_csv("influencers.csv", on_bad_lines='skip')
        df = raw_df.copy()
        df['takipci'] = pd.to_numeric(df['takipci'].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce').fillna(0)
        df['etkilesim'] = pd.to_numeric(df['etkilesim'].astype(str).str.replace(',', '.'), errors='coerce').fillna(5.0)
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
    st.warning("⚠️ Lütfen 'influencers.csv' dosyanızın mevcut olduğundan emin olun.")
    st.stop()

def get_social_link(name, platform):
    clean_name = name.lower().replace(" ", "").replace("ı", "i").replace("ö", "o").replace("ü", "u").replace("ç", "c").replace("ş", "s").replace("ğ", "g")
    if "tiktok" in platform.lower(): return f"https://www.tiktok.com/@{clean_name}"
    elif "instagram" in platform.lower(): return f"https://instagram.com/{clean_name}"
    elif "youtube" in platform.lower(): return f"https://youtube.com/@{clean_name}"
    return "https://google.com"

if 'advisor_mode' not in st.session_state: st.session_state['advisor_mode'] = None 
if 'pre_selected_type' not in st.session_state: st.session_state['pre_selected_type'] = "Tümü"

# MENTOR SEÇİMİ VE ANKET EKRANLARI
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

    tab1, tab2, tab3, tab4 = st.tabs(["💎 Influencer Vitrini", "🧙‍♂️ Akıllı Sihirbaz & AI Analizi", "📈 Veri Analizi", "⚖️ Yasal Danışman Panel"])
    
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

    # --- TAM ARADIĞIN ESKİ AI INSIGHT RAPORLU TAB 2 ---
    with tab2:
        st.header("🧠 Akıllı Eşleştirme Motoru & Yapay Zeka Analizi")
        with st.form("wizard_form_v9"):
            w_sektor = st.selectbox("🎯 Hedef Sektör", sorted(list(df["sektor"].unique())))
            w_hedef = st.radio("🚀 Kampanya Amacı", ["Satış Yapmak (Dönüşüm Odaklı)", "Bilinirlik Kazanmak (Erişim Odaklı)"])
            w_tipler = st.multiselect("📊 İstenilen Segmentler", list(df["tip"].unique()), default=list(df["tip"].unique()))
            submit_wizard = st.form_submit_button("⚡ Aday Performans Kıyaslamasını Başlat")

        if submit_wizard:
            res = df[(df["sektor"] == w_sektor) & (df["tip"].isin(w_tipler))]
            if res.empty:
                st.warning("⚠️ Seçilen kriterlere uygun influencer bulunamadı. Genel liste taranıyor...")
                res = df.copy()
            
            best_math = res.sort_values(by="SMS", ascending=False).iloc[0]
            st.success(f"🥇 MATEMATİKSEL EN UYGUN ADAY: {best_math['ad']} (Smart-Match Skoru: {best_math['SMS']}/100)")
            
            st.markdown("---")
            with st.spinner("🧠 Yapay zeka veri tabanını analiz ediyor, En Uygun ve En Riskli adayları çıkartıyor..."):
                try:
                    import json
                    from groq import Groq
                    
                    api_key = st.secrets.get("GROQ_API_KEY", None)
                    if not api_key:
                        st.error("❌ `secrets.toml` içerisinde GROQ_API_KEY anahtarı bulunamadı!")
                    else:
                        client = Groq(api_key=api_key)
                        veri_ozeti = res[['ad', 'sektor', 'tip', 'platform', 'takipci', 'etkilesim', 'SMS']].to_string(index=False)
                        
                        # Yapay zekaya senin tam değişken isimlerini dikte ediyoruz
                        sistem_talimati = f"""
                        Sen dijital pazarlama veri analistisin. Verilen veri kümesinden en uygun ve en riskli influencer'ları seçmelisin.
                        Senden çıktıyı MUTLAKA ve tam olarak aşağıdaki JSON formatında vermeni istiyorum. Başka hiçbir metin ekleme.

                        {{
                            "en_uygun_isim": "Maksimum verim sağlayacak influencer'ın sadece adı ve soyadı",
                            "en_uygun_sms": 96.4,
                            "en_uygun_segment": "Adayın segment metni",
                            "en_uygun_platform": "Instagram veya TikTok",
                            "en_uygun_takipci": "737,000",
                            "en_uygun_etkilesim": "%11.5",
                            "en_uygun_neden": "Bu adayın neden seçildiğinin detaylı matematiksel açıklaması",
                            "en_riskli_isim": "En az uygun / yüksek riskli influencer'ın sadece adı ve soyadı",
                            "en_riskli_sms": 73.0,
                            "en_riskli_segment": "Adayın segment metni",
                            "en_riskli_platform": "Instagram veya TikTok",
                            "en_riskli_takipci": "1,100,000",
                            "en_riskli_etkilesim": "%4.5",
                            "en_riskli_neden": "Bu adayın bütçe veya hedefleme açısından neden uygun olmadığının detaylı açıklaması",
                            "kreatif_senaryolar": "Adayların tarzına uygun video senaryoları ve portfolyo kurguları",
                            "yasal_zoorunluluklar": "Ticaret Bakanlığı kılavuzuna göre uyması gereken yasal reklam kuralları"
                        }}

                        Veri kümesi:
                        {veri_ozeti}
                        """
                        
                        completion = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[{"role": "user", "content": sistem_talimati + f"\nSektör: {w_sektor}, Hedef: {w_hedef}"}],
                            temperature=0.2,
                            response_format={"type": "json_object"}
                        )
                        
                        # Tam istediğin o orijinal JSON ayrıştırma bloğu
                        cevap_json = json.loads(completion.choices[0].message.content)
                        
                        st.success("✨ Yapay Zeka Stratejik Analizi Tamamlandı!")
                        st.markdown("---")
                        
                        # --- 1. KISIM: AI INSIGHT (GÖRSELDEKİ KUTULU REZALET/MÜKEMMEL ADAY KARTLARI) ---
                        st.subheader("🎯 AI Insight: Sihirbaz Eşleştirmesi")
                        col_iyi, col_kötü = st.columns(2)
                        
                        with col_iyi:
                            st.markdown('<div style="background-color:#E8F5E9; padding:10px; border-radius:5px;"><h3 style="color:#2E7D32; margin:0;">🟢 EN UYGUN ADAY (Maksimum Verim)</h3></div>', unsafe_allow_html=True)
                            with st.container(border=True):
                                st.markdown(f"### ✨ {cevap_json.get('en_uygun_isim')}")
                                st.markdown(f"📊 Smart-Match Skoru: {cevap_json.get('en_uygun_sms', 90.0)} / 100")
                                try: st.progress(float(cevap_json.get('en_uygun_sms')) / 100)
                                except: st.progress(0.95)
                                st.caption(f"Segment: {cevap_json.get('en_uygun_segment')} | Platform: {cevap_json.get('en_uygun_platform')}")
                                
                                st.markdown("<br><small>Takipçi Sayısı</small>", unsafe_allow_html=True)
                                st.markdown(f"## {cevap_json.get('en_uygun_takipci')}")
                                st.markdown("<small>Etkileşim Oranı</small>", unsafe_allow_html=True)
                                st.markdown(f"## {cevap_json.get('en_uygun_etkilesim')}")
                                
                                st.info(cevap_json.get('en_uygun_neden'))
                                st.link_button(f"🔗 {cevap_json.get('en_uygun_isim')} Profilini İncele", get_social_link(cevap_json.get('en_uygun_isim'), cevap_json.get('en_uygun_platform', 'Instagram')), use_container_width=True)
                                
                        with col_kötü:
                            st.markdown('<div style="background-color:#FFEBEE; padding:10px; border-radius:5px;"><h3 style="color:#C62828; margin:0;">🔴 EN AZ UYGUN ADAY (Yüksek Risk / Düşük Verim)</h3></div>', unsafe_allow_html=True)
                            with st.container(border=True):
                                st.markdown(f"### ⚠️ {cevap_json.get('en_riskli_isim')}")
                                st.markdown(f"📊 Smart-Match Skoru: {cevap_json.get('en_riskli_sms', 70.0)} / 100")
                                try: st.progress(float(cevap_json.get('en_riskli_sms')) / 100)
                                except: st.progress(0.70)
                                st.caption(f"Segment: {cevap_json.get('en_riskli_segment')} | Platform: {cevap_json.get('en_riskli_platform')}")
                                
                                st.markdown("<br><small>Takipçi Sayısı</small>", unsafe_allow_html=True)
                                st.markdown(f"## {cevap_json.get('en_riskli_takipci')}")
                                st.markdown("<small>Etkileşim Oranı</small>", unsafe_allow_html=True)
                                st.markdown(f"## {cevap_json.get('en_riskli_etkilesim')}")
                                
                                st.warning(cevap_json.get('en_riskli_neden'))
                                st.link_button(f"🔗 {cevap_json.get('en_riskli_isim')} Profilini İncele", get_social_link(cevap_json.get('en_riskli_isim'), cevap_json.get('en_riskli_platform', 'Instagram')), use_container_width=True)
                                
                        st.markdown("---")
                        
                        # --- 2. KISIM: REKLAM SENARYOLARI VE PORTFOLYO KURGUSU ---
                        st.subheader("🎬 Kreatif Portfolyo & Video Senaryoları")
                        st.write(cevap_json.get('kreatif_senaryolar'))
                        
                        st.markdown("---")
                        
                        # --- 3. KISIM: YASAL DANIŞMANLIK REHBERİ ---
                        st.subheader("⚖️ Hukuki Mevzuat ve Yasal Zorunluluklar")
                        st.write(cevap_json.get('yasal_zoorunluluklar'))
                        
                        st.markdown("---")
                        
                        # --- 4. KISIM: ESKİ METİN DERLEME VE İNDİRME BUTONU ---
                        tam_rapor = f"""=== AI INFLUENCER STRATEJİ RAPORU ===\n\n
EN UYGUN INFLUENCER: {cevap_json.get('en_uygun_isim')}\nNeden: {cevap_json.get('en_uygun_neden')}\n\n
EN RİSKLİ INFLUENCER: {cevap_json.get('en_riskli_isim')}\nNeden: {cevap_json.get('en_riskli_neden')}\n\n
KREATİF REKLAM SENARYOLARI:\n{cevap_json.get('kreatif_senaryolar')}\n\n
YASAL ZORUNLULUKLAR:\n{cevap_json.get('yasal_zoorunluluklar')}"""

                        st.download_button(
                            label="📥 Tam Strateji Raporunu Bilgisayara İndir (.txt)",
                            data=tam_rapor,
                            file_name="influ_match_ai_rapor.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                        
                except Exception as e:
                    st.error(f"Yapay Zeka Ayrıştırma Hatası: {e}")

    with tab3:
        st.header("📈 Matematiksel Dağılım ve Matris Analizi")
        if not f_df.empty:
            fig = px.scatter(f_df, x="takipci", y="SMS", color="sektor" if len(f_df["sektor"].unique()) > 1 else None, size="etkilesim", hover_name="ad", title="Takipçi vs. SMS")
            st.plotly_chart(fig, use_container_width=True)
        st.dataframe(f_df, use_container_width=True)

    with tab4:
        st.header("### ⚖️ T.C. Ticaret Bakanlığı Reklam ve Influencer Mevzuat Danışmanı")
        yasal_soru = st.text_area("❓ Sormak İstediğiniz Yasal Soru/Mevzuat Nedir?", placeholder="Örn: Instagram hikayelerinde iş birliği etiketi nereye konulmalı...", key="legal_query_box")
        if st.button("⚖️ Kanun ve Mevzuata Göre İncele", key="groq_yasal_start"):
            if not yasal_soru:
                st.warning("⚠️ Lütfen yasal sorunuzu buraya yazın.")
            else:
                with st.spinner("📜 Mevzuat taranıyor..."):
                    try:
                        from groq import Groq
                        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                        yasal_mesaj = f"Kullanıcı Sorusu: {yasal_soru}\nTicaret Bakanlığı Influencer kılavuzuna göre maddeler halinde yasal zorunlulukları açıkla."
                        completion = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": yasal_mesaj}], temperature=0.1)
                        st.success("⚖️ Hukuki Mevzuat Analizi Tamamlandı!")
                        st.markdown("---")
                        st.markdown(completion.choices[0].message.content)
                    except Exception as e:
                        st.error(f"AI Bağlantı Hatası: {e}")
