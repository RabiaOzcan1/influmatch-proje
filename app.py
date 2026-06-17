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

    # --- TAB 2: KUTULU EN UYGUN VE EN KÖTÜ ADAY ANALİZİ ---
    with tab2:
        st.header("🧠 Akıllı Eşleştirme Motoru")
        with st.form("wizard_form_v9_fixed"):
            w_sektor = st.selectbox("🎯 Hedef Sektör", sorted(list(df["sektor"].unique())))
            w_hedef = st.radio("🚀 Kampanya Amacı", ["Satış Yapmak (Dönüşüm Odaklı)", "Bilinirlik Kazanmak (Erişim Odaklı)"])
            w_tipler = st.multiselect("📊 İstenilen Segmentler", list(df["tip"].unique()), default=list(df["tip"].unique()))
            submit_wizard = st.form_submit_button("⚡ Aday Performans Kıyaslamasını Başlat")

        if submit_wizard:
            res = df[(df["sektor"] == w_sektor) & (df["tip"].isin(w_tipler))]
            if res.empty:
                st.warning("⚠️ Seçilen kriterlere uygun influencer bulunamadı. Genel veri kümesi taranıyor...")
                res = df.copy()
            
            best_math = res.sort_values(by="SMS", ascending=False).iloc[0]
            st.success(f"🥇 MATEMATİKSEL EN UYGUN ADAY: {best_math['ad']} (Smart-Match Skoru: {best_math['SMS']}/100)")
            
            st.markdown("---")
            with st.spinner("🧠 Yapay zeka verileri süzüyor, En Uygun ve En Riskli aday kartlarını hazırlıyor..."):
                try:
                    import json
                    from groq import Groq
                    
                    api_key = st.secrets.get("GROQ_API_KEY", None)
                    if not api_key:
                        st.error("❌ `secrets.toml` içerisinde GROQ_API_KEY anahtarı bulunamadı!")
                    else:
                        client = Groq(api_key=api_key)
                        veri_ozeti = res[['ad', 'sektor', 'tip', 'platform', 'takipci', 'etkilesim', 'SMS']].to_string(index=False)
                        
                        sistem_talimati = f"""
                        Sen dijital pazarlama veri analistisin. Verilen veri kümesinden en uygun ve en riskli influencer'ları seçmelisin.
                        Senden çıktıyı MUTLAKA ve sadece aşağıdaki JSON formatında vermeni istiyorum. Başka hiçbir açıklama yazma.

                        {{
                            "en_uygun_isim": "Maksimum verim sağlayacak influencer'ın sadece adı ve soyadı",
                            "en_uygun_sms": 96.4,
                            "en_uygun_segment": "Adayın segment metni",
                            "en_uygun_platform": "Instagram veya TikTok",
                            "en_uygun_takipci": "737,000",
                            "en_uygun_etkilesim": "%11.5",
                            "en_uygun_neden": "Detaylı matematiksel seçim nedeni açıklaması",
                            "en_riskli_isim": "En az uygun / yüksek riskli influencer'ın sadece adı ve soyadı",
                            "en_riskli_sms": 73.0,
                            "en_riskli_segment": "Adayın segment metni",
                            "en_riskli_platform": "Instagram veya TikTok",
                            "en_riskli_takipci": "1,100,000",
                            "en_riskli_etkilesim": "%4.5",
                            "en_riskli_neden": "Neden riskli ve uygun olmadığının detaylı açıklaması"
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
                        
                        cevap_json = json.loads(completion.choices[0].message.content)
                        
                        col_iyi, col_kötü = st.columns(2)
                        
                        with col_iyi:
                            st.markdown('<div style="background-color:#E8F5E9; padding:10px; border-radius:5px;"><h3 style="color:#2E7D32; margin:0;">🟢 EN UYGUN ADAY (Maksimum Verim)</h3></div>', unsafe_allow_html=True)
                            with st.container(border=True):
                                st.markdown(f"### ✨ {cevap_json.get('en_uygun_isim')}")
                                st.markdown(f"📊 Smart-Match Skoru: {cevap_json.get('en_uygun_sms')} / 100")
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
                                st.markdown(f"📊 Smart-Match Skoru: {cevap_json.get('en_riskli_sms')} / 100")
                                try: st.progress(float(cevap_json.get('en_riskli_sms')) / 100)
                                except: st.progress(0.70)
                                st.caption(f"Segment: {cevap_json.get('en_riskli_segment')} | Platform: {cevap_json.get('en_riskli_platform')}")
                                
                                st.markdown("<br><small>Takipçi Sayısı</small>", unsafe_allow_html=True)
                                st.markdown(f"## {cevap_json.get('en_riskli_takipci')}")
                                st.markdown("<small>Etkileşim Oranı</small>", unsafe_allow_html=True)
                                st.markdown(f"## {cevap_json.get('en_riskli_etkilesim')}")
                                
                                st.warning(cevap_json.get('en_riskli_neden'))
                                st.link_button(f"🔗 {cevap_json.get('en_riskli_isim')} Profilini İncele", get_social_link(cevap_json.get('en_riskli_isim'), cevap_json.get('en_riskli_platform', 'Instagram')), use_container_width=True)
                                
                except Exception as e:
                    st.error(f"Sihirbaz Yapay Zeka Hatası: {e}")

    with tab3:
        st.header("📈 Matematiksel Dağılım ve Matris Analizi")
        if not f_df.empty:
            fig = px.scatter(f_df, x="takipci", y="SMS", color="sektor" if len(f_df["sektor"].unique()) > 1 else None, size="etkilesim", hover_name="ad", title="Takipçi vs. SMS")
            st.plotly_chart(fig, use_container_width=True)
        st.dataframe(f_df, use_container_width=True)

    # --- TAB 4: RADYO BUTONLU VE SEKTÖR KORUMALI AI ASİSTAN PANELİ ---
    with tab4:
        st.header("🧠 Akıllı Reklam Senaryosu, Öneri ve Yasal Danışman")
        
        # Orijinal radyo buton yapısını buraya entegre ettik
        ai_modu = st.radio(
            "💡 Yapay Zekayı Hangi Amaçla Kullanmak İstersiniz?",
            options=["🎯 Reklam Senaryosu ve Bütçe Uyumlu Öneri Al", "⚖️ Sadece Yasal Soru Söyle (Mevzuat Danışmanı)"],
            horizontal=True,
            key="tab4_ai_mode_selector"
        )
        
        st.divider()
        
        if ai_modu == "🎯 Reklam Senaryosu ve Bütçe Uyumlu Öneri Al":
            st.markdown("Kampanya fikrinizi ve hedef kitlenizi yazın. AI, seçtiğiniz **bütçe aralığına tam uyan** influencer sınıflarını veritabanından süzerek size özel bir strateji ve yasal uyum raporu hazırlar.")
            
            # Alakasız infuların dökülmesini engelleyen kritik Sektör Seçim kutusu
            kampanya_sektoru = st.selectbox("🎯 Reklam Yapacağınız Sektör Nedir?", options=sorted(list(df["sektor"].unique())), key="groq_sector_selector")
            
            kampanya_butcesi = st.selectbox(
                "Kampanya Bütçeniz Nedir?",
                options=[
                    "Düşük Bütçe (Nano)", 
                    "Orta-Düşük Bütçe (Nano & Micro)", 
                    "Orta Bütçe (Micro)", 
                    "Orta-Yüksek Bütçe (Macro & Mega)", 
                    "Yüksek Bütçe (Mega)"
                ],
                help="Seçtiğiniz bütçe aralığına uygun influencer tipleri yapay zekaya kesin kural olarak dikte edilir.",
                key="groq_budget_selector_tab4"
            )
            
            user_prompt = st.text_area(
                "Kampanya Detaylarını ve Hedef Kitleyi Yazın:",
                placeholder="Örn: Yeni bir kozmetik markası çıkarıyoruz. Hedef kitlemiz 18-45 yaş arası ve kozmetik alanı. TikTok ve Instagram ana mecralarım. Muhtemel reklam senaryoları ve dikkat etmem gereken yasal zorunluluklar nelerdir?",
                key="groq_user_prompt"
            )
            
            if st.button("Yapay Zeka Analizini Başlat 🚀", key="groq_start_button"):
                if not user_prompt:
                    st.warning("Lütfen önce kampanya detaylarını yazın.")
                else:
                    with st.spinner("Yapay Zeka bütçe ve sektör filtrenize uygun analizleri hazırlıyor..."):
                        try:
                            from groq import Groq
                            api_key = st.secrets.get("GROQ_API_KEY", None)
                            
                            if not api_key:
                                st.error("Lütfen `.streamlit/secrets.toml` dosyasına GROQ_API_KEY anahtarınızı ekleyin.")
                            else:
                                client = Groq(api_key=api_key)
                                
                                # Sektör Filtreleme Koruması: Sadece seçilen sektörü süzüp AI'a gönderiyoruz
                                daraltilmis_df = df[df["sektor"] == kampanya_sektoru].copy()
                                if daraltilmis_df.empty:
                                    daraltilmis_df = df.copy() # Eğer o sektörde kimse yoksa emniyet kilidi
                                    
                                veri_ozeti = daraltilmis_df[['ad', 'sektor', 'tip', 'platform', 'takipci', 'etkilesim', 'SMS']].to_string(index=False)
                                
                                butce_talimati = f"""
                                KESİN BÜTÇE VE INFLUENCER TİPİ EŞLEŞTİRME KURALI: 
                                Kullanıcı bütçe seçeneği olarak '{kampanya_butcesi}' modelini seçmiştir.
                                Veritabanından influencer önerisi yaparken ŞU EŞLEŞTİRMELERE %100 UYMAK ZORUNDASIN:
                                
                                - Eğer 'Düşük Bütçe (Nano)' seçildiyse: SADECE 'Nano' tipindeki influencer'ları önerebilirsin.
                                - Eğer 'Orta-Düşük Bütçe (Nano & Micro)' seçildiyse: SADECE 'Nano' ve 'Micro' tipindeki influencer'ları BİRLİKTE veya karma olarak önerebilirsin. (Macro ve Mega Kesinlikle Yasak!)
                                - Eğer 'Orta Bütçe (Micro)' seçildiyse: SADECE 'Micro' tipindeki influencer'ları önerebilirsin.
                                - Eğer 'Orta-Yüksek Bütçe (Macro & Mega)' seçildiyse: SADECE 'Macro' ve 'Mega' tipindeki influencer'ları BİRLİKTE veya karma olarak önerebilirsin. (Nano ve Micro Kesinlikle Yasak!)
                                - Eğer 'Yüksek Bütçe (Mega)' seçildiyse: SADECE 'Mega' tipindeki influencer'ları önerebilirsin.
                                """
                                
                                kullanici_mesaji = f"""
                                Sen profesyonel bir Dijital Pazarlama Stratejistisi, Kreatif Reklam Yazarı ve Influencer Hukuku Danışmanısın.
                                
                                {butce_talimati}
                                
                                Yukarıdaki bütçe ve tip sınırlandırma kurallarına göre, sana aşağıda sağlanan influencer veritabanını filtrele ve sadece '{kampanya_sektoru}' sektöründeki kurallara uyan isimleri cımbızla seç.
                                
                                Mevcut Filtrelenmiş Influencer Veri Özeti:
                                {veri_ozeti}
                                
                                Kullanıcının Kampanya Talebi:
                                "{user_prompt}"
                                
                                Lütfen şu başlıklar altında harika bir Türkçe rapor hazırla:
                                
                                🎯 1. BÜTÇE ARALIĞINA UYGUN NOKTA ATIŞI INFLUENCER ÖNERİLERİ
                                (Kullanıcının seçtiği {kampanya_butcesi} durumuna göre veritabanından bulduğun uygun isimleri, takipçi ve etkileşim oranlarıyla listele. Seçtiğin isimlerin bütçe kuralıyla neden uyumlu olduğunu açıkla.)
                                
                                🎬 2. KREATİF REKLAM SENARYO ÖNERİLERİ
                                (Önerdiğin bu isimlerin tarzına, Instagram Reels ve TikTok formatına uygun, samimi en az 2 video senaryosu kurgula.)
                                
                                ⚖️ 3. YASAL ZORUNLULUKLAR VE DİKKAT EDİLMESİ GEREKENLER (TÜRKİYE MEVZUATI)
                                (Ticaret Bakanlığı kurallarına göre #reklam/#işbirliği kullanımı ve kozmetik ürünlerdeki sağlık beyanı yasaklarını maddeler halinde yaz.)
                                """
                                
                                completion = client.chat.completions.create(
                                    model="llama-3.3-70b-versatile",
                                    messages=[{"role": "user", "content": kullanici_mesaji}],
                                    temperature=0.3
                                )
                                
                                ai_raporu = completion.choices[0].message.content
                                
                                st.success("✨ Esnek Bütçe Uyumlu Strateji ve Yasal Rapor Hazır!")
                                st.markdown("---")
                                st.markdown(ai_raporu)
                                st.markdown("---")
                                
                                st.download_button(
                                    label="📄 Raporu İndir",
                                    data=ai_raporu,
                                    file_name="esnek_butceli_reklam_raporu.txt",
                                    mime="text/plain",
                                    key="groq_download_button"
                                )
                                
                        except Exception as ai_err:
                            st.error(f"AI Analiz Motoru Hatası: {ai_err}")
                            
        else:
            st.markdown("### ⚖️ T.C. Ticaret Bakanlığı Reklam ve Influencer Mevzuat Danışmanı")
            yasal_soru = st.text_area("❓ Sormak İstediğiniz Yasal Soru/Mevzuat Nedir?", placeholder="Örn: Instagram hikayelerinde iş birliği etiketi nereye konulmalı...", key="legal_query_box_tab4")
            if st.button("⚖️ Kanun ve Mevzuata Göre İncele", key="groq_yasal_start_tab4"):
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
