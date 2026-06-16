import streamlit as st
import pandas as pd
import plotly.express as px

# Sayfa Yapılandırması
st.set_page_config(page_title="InfluMatch AI Pro v6.5 🔥", layout="wide")

# Oturum Durumu Kontrolü (Giriş yapıldı mı?)
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# Giriş Yapılmadıysa SADECE Giriş Panelini Göster
if not st.session_state['logged_in']:
    st.title("🔐 Giriş Paneli")
    
    # Form kullanarak her girişte sayfanın gereksiz tetenmesini önlüyoruz
    with st.form("login_form"):
        user = st.text_input("Kullanıcı Adı", placeholder="admin")
        pw = st.text_input("Şifre", type="password", placeholder="1234")
        submit_login = st.form_submit_button("Sisteme Giriş Yap 🚀")
        
        if submit_login:
            if user == "admin" and pw == "1234":
                st.session_state['logged_in'] = True
                st.rerun()  # Sayfayı baştan yükle, böylece bu if bloğu atlansın!
            else:
                st.error("❌ Hatalı kullanıcı adı veya şifre!")
                
    st.stop()  # Giriş yapılmadıysa alt taraftaki uygulamanın ana kodlarını ASLA çalıştırma!

# --- BURADAN SONRASI SADECE GİRİŞ YAPILDIYSA ÇALIŞIR VE GÖRÜNÜR ---
st.success("🔓 Başarıyla Giriş Yapıldı! Hoş geldiniz.")

try:
    raw_df = pd.read_csv("influencers.csv", on_bad_lines='skip')
    df = raw_df.copy()
    
    # Veri temizleme ve skorlama adımları
    df['takipci'] = pd.to_numeric(df['takipci'].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce').fillna(0)
    df['etkilesim'] = pd.to_numeric(df['etkilesim'].astype(str).str.replace(',', '.'), errors='coerce').fillna(5.0)
    
    df['G'] = (df['etkilesim'] * 4 + 50).clip(60, 98).round(1)   
    df['E'] = (df['etkilesim'] * 5 + 40).clip(55, 99).round(1)   
    df['O'] = (100 - df['takipci'] / 1000000).clip(70, 96).round(1) 
    df['S'] = (df['etkilesim'] * 3 + 65).clip(65, 95).round(1)   
    df['SMS'] = (0.40 * df['G'] + 0.30 * df['E'] + 0.20 * df['O'] + 0.10 * df['S']).round(1)
        
except Exception as e:
    st.error(f"Veri yükleme hatası: {e}")
    st.stop()

# Sosyal Medya Link Motoru
def get_social_link(name, platform):
    clean_name = name.lower().replace(" ", "").replace("ı", "i").replace("ö", "o").replace("ü", "u").replace("ç", "c").replace("ş", "s").replace("ğ", "g")
    if "tiktok" in platform.lower(): return f"https://www.tiktok.com/@{clean_name}"
    elif "instagram" in platform.lower(): return f"https://instagram.com/{clean_name}"
    elif "youtube" in platform.lower(): return f"https://youtube.com/@{clean_name}"
    return "https://google.com"

if 'advisor_mode' not in st.session_state: st.session_state['advisor_mode'] = None 
if 'pre_selected_type' not in st.session_state: st.session_state['pre_selected_type'] = "Tümü"

# EKRAN 1: AI MENTOR SEÇİMİ
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

# EKRAN 2: ANKET
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

# EKRAN 3: ANA PANEL
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

    tab1, tab2, tab3, tab4 = st.tabs(["💎 Influencer Vitrini", "🧙‍♂️ Akıllı Sihirbaz", "📈 Veri Analizi", "🤖 AI Serbest Arama"])
    
    with tab1:
        st.header("✨ Influencer Arama ve Portföy Vitrini")
        search_query = st.text_input("🔍 İsim ile Manuel Arama Yapın:")
        vitrin_df = df[df["ad"].astype(str).str.contains(search_query, case=False, na=False)] if search_query else f_df
        
        if vitrin_df.empty: st.warning("⚠️ Aday bulunamadı.")
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
                        m2.metric("⚡ Etkilesim", f"%{row['etkilesim']}")
                        st.link_button("🌐 Profili Gör", get_social_link(row['ad'], row['platform']), use_container_width=True)

    with tab2:
        st.header("🧠 Akıllı Eşleştirme Motoru")
        with st.form("wizard_form_v6"):
            w_sektor = st.selectbox("🎯 Hedef Sektör", df["sektor"].unique())
            w_hedef = st.radio("🚀 Kampanya Amacı", ["Satış Yapmak", "Bilinirlik Kazanmak"])
            w_tipler = st.multiselect("📊 İstenilen Segmentler", list(df["tip"].unique()), default=list(df["tip"].unique()))
            submit_wizard = st.form_submit_button("⚡ Aday Performans Kıyaslamasını Başlat")

        if submit_wizard:
            res = df[(df["sektor"] == w_sektor) & (df["tip"].isin(w_tipler))]
            if len(res) >= 1:
                best = res.sort_values(by="SMS", ascending=False).iloc[0]
                st.success(f"🥇 EN UYGUN ADAY: {best['ad']} (Skor: {best['SMS']})")

    with tab3:
        st.header("📈 Matematiksel Dağılım ve Matris Analizi")
        if not f_df.empty:
            fig = px.scatter(f_df, x="takipci", y="SMS", color="sektor" if len(f_df["sektor"].unique()) > 1 else None, size="etkilesim", hover_name="ad", title="Takipçi vs. SMS")
            st.plotly_chart(fig, use_container_width=True)
        st.dataframe(f_df, use_container_width=True)

    # --- TAB 4: SEKTÖREL YAPAY ZEKA FILTRE MOTORU ---
    with tab4:
        st.header("🤖 Akıllı Reklam Senaryosu ve Öneri Sistemi")
        st.markdown("Kampanya hedeflerinizi yazın. Yapay zeka, seçtiğiniz sektöre göre verileri filtreleyerek nokta atışı senaryo kurgular.")
        
        # Kesin filtreleme için zorunlu Sektör seçimi kutusu ekledik!
        kampanya_sektoru = st.selectbox("🎯 Reklam Yapacağınız Sektör Nedir?", options=list(df["sektor"].unique()))
        
        kampanya_butcesi = st.selectbox(
            "💰 Kampanya Bütçeniz Nedir?",
            options=["Düşük Bütçe (Nano)", "Orta-Düşük Bütçe (Nano & Micro)", "Orta Bütçe (Micro)", "Orta-Yüksek Bütçe (Macro & Mega)", "Yüksek Bütçe (Mega)"]
        )
        
        user_prompt = st.text_area(
            "📝 Kampanya Detaylarını ve İsteklerinizi Yazın:",
            placeholder="Örn: Yeni çıkardığım mobil strateji oyunu için düşük bütçeli, eğlenceli ve viral olabilecek video kurguları istiyorum..."
        )
        
        if st.button("🚀 Yapay Zeka Analizini Başlat", key="groq_v6_start"):
            if not user_prompt:
                st.warning("⚠️ Lütfen kampanya detaylarını boş bırakmayın.")
            else:
                with st.spinner("🧠 Yapay zeka alakasız sektörleri eliyor..."):
                    try:
                        # 1. Aşama: Bütçe/Tip Filtrelemesi
                        ai_df = df.copy()
                        if "Düşük Bütçe (Nano)" in kampanya_butcesi:
                            ai_df = ai_df[ai_df["tip"].astype(str).str.contains("Nano", case=False, na=False)]
                        elif "Orta-Düşük Bütçe (Nano & Micro)" in kampanya_butcesi:
                            ai_df = ai_df[ai_df["tip"].astype(str).str.contains("Nano|Micro", case=False, na=False)]
                        elif "Orta Bütçe (Micro)" in kampanya_butcesi:
                            ai_df = ai_df[ai_df["tip"].astype(str).str.contains("Micro", case=False, na=False)]
                        elif "Orta-Yüksek Bütçe (Macro & Mega)" in kampanya_butcesi:
                            ai_df = ai_df[ai_df["tip"].astype(str).str.contains("Macro|Mega", case=False, na=False)]
                        elif "Yüksek Bütçe (Mega)" in kampanya_butcesi:
                            ai_df = ai_df[ai_df["tip"].astype(str).str.contains("Mega", case=False, na=False)]

                        # 2. Aşama: Sert Sektör Filtresi (Kod düzeyinde yemek/moda hesaplarını engelliyoruz!)
                        ai_df = ai_df[ai_df["sektor"].astype(str).str.contains(kampanya_sektoru, case=False, na=False)]

                        if ai_df.empty:
                            st.error(f"❌ Veri tabanında şu an '{kampanya_sektoru}' sektörüne ait ve '{kampanya_butcesi}' aralığında bir influencer bulunamadı.")
                        else:
                            from groq import Groq
                            api_key = st.secrets.get("GROQ_API_KEY", None)
                            
                            if not api_key:
                                st.error("❌ GROQ_API_KEY bulunamadı. Lütfen Streamlit Cloud Secrets ayarlarınızı kontrol edin.")
                            else:
                                client = Groq(api_key=api_key)
                                veri_ozeti = ai_df[['ad', 'sektor', 'tip', 'platform', 'takipci', 'etkilesim', 'SMS']].to_string(index=False)
                                
                                kullanici_mesaji = f"""
                                Sen uzman bir dijital pazarlama direktörüsün.
                                Kullanıcı şu an kesin olarak sadece '{kampanya_sektoru}' sektöründe bir reklam çalışması yapmaktadır.
                                
                                Sana Python tarafında elenerek gelen SADECE '{kampanya_sektoru}' alanındaki influencer listesi:
                                {veri_ozeti}
                                
                                Kullanıcının İstemi: "{user_prompt}"
                                
                                Görevin:
                                1. Yukarıdaki listedeki influencer isimlerini kullanarak nokta atışı ortaklıklar öner. Yemek, Gıda, Yaşam Tarzı gibi alakasız sektörlerden tek bir isim bile seçme.
                                2. Önerdiğin isimler için tamamen '{kampanya_sektoru}' konseptine uygun kreatif reklam senaryoları yaz.
                                3. Ticaret Bakanlığı reklam kuralları uyarısı ekle.
                                """
                                
                                completion = client.chat.completions.create(
                                    model="llama-3.3-70b-versatile",
                                    messages=[{"role": "user", "content": kullanici_mesaji}],
                                    temperature=0.1
                                )
                                
                                ai_raporu = completion.choices[0].message.content
                                st.success("🎉 Seçilen Sektör ve Bütçeyle %100 Uyumlu Rapor Hazır!")
                                st.markdown("---")
                                st.markdown(ai_raporu)
                                
                    except Exception as ai_err:
                        st.error(f"❌ AI Analiz Hatası: {ai_err}")
