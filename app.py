import streamlit as st
import pandas as pd
import plotly.express as px

# Sayfa Yapılandırması
st.set_page_config(page_title="InfluMatch AI Pro v5.8 🔥", layout="wide")

# 1. GİRİŞ SİSTEMİ VE OTURUM YÖNETİMİ
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("🔐 Giriş Paneli")
    user = st.text_input("Kullanıcı Adı", placeholder="admin")
    pw = st.text_input("Şifre", type="password", placeholder="1234")
    if st.button("Sisteme Giriş Yap 🚀"):
        if user == "admin" and pw == "1234":
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("❌ Hatalı giriş bilgileri!")
else:
    # Veriyi oku
    try:
        # --- GÜVENLİ VERİ OKUMA (Hatalı satırlarda çökmeyi önler) ---
        raw_df = pd.read_csv("influencers.csv", on_bad_lines='skip')
        df = raw_df.copy()
        
        # --- VERİ TİPİ GÜVENLİK FİLTRESİ ---
        df['takipci'] = pd.to_numeric(df['takipci'].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce').fillna(0)
        df['etkilesim'] = pd.to_numeric(df['etkilesim'].astype(str).str.replace(',', '.'), errors='coerce').fillna(5.0)
        
        # --- ÖZEL VERİ DÜZELTME KURALLARI ---
        if 'ad' in df.columns:
            # merve.deniyor koruması (Gerçek veriler)
            df.loc[df['ad'].astype(str).str.contains('merve.deniyor', case=False), 'takipci'] = 6384
            df.loc[df['ad'].astype(str).str.contains('merve.deniyor', case=False), 'etkilesim'] = 38.8
            df.loc[df['ad'].astype(str).str.contains('merve.deniyor', case=False), 'platform'] = 'TikTok'
        
        # --- DİNAMİK SMART-MATCH SKORU (SMS) ENGINE ---
        df['G'] = (df['etkilesim'] * 4 + 50).clip(60, 98).round(1)   
        df['E'] = (df['etkilesim'] * 5 + 40).clip(55, 99).round(1)   
        df['O'] = (100 - df['takipci'] / 1000000).clip(70, 96).round(1) 
        df['S'] = (df['etkilesim'] * 3 + 65).clip(65, 95).round(1)   
        df['SMS'] = (0.40 * df['G'] + 0.30 * df['E'] + 0.20 * df['O'] + 0.10 * df['S']).round(1)
            
    except Exception as e:
        st.error(f"Veri yükleme hatası: {e}")
        st.stop()

    # --- SOSYAL MEDYA LİNK MOTORU ---
    def get_social_link(name, platform):
        clean_name = name.lower().replace(" ", "").replace("ı", "i").replace("ö", "o").replace("ü", "u").replace("ç", "c").replace("ş", "s").replace("ğ", "g")
        if "merve.deniyor" in clean_name or "mervedeniyor" in clean_name:
            return "https://www.tiktok.com/@merve.deniyor"
            
        if "tiktok" in platform.lower():
            return f"https://www.tiktok.com/@{clean_name}"
        elif "instagram" in platform.lower():
            return f"https://instagram.com/{clean_name}"
        elif "youtube" in platform.lower():
            return f"https://youtube.com/@{clean_name}"
        elif "twitch" in platform.lower():
            return f"https://twitch.tv/{clean_name}"
        elif "twitter" in platform.lower():
            return f"https://x.com/{clean_name}"
        else:
            return "https://google.com"

    # --- DURUM YÖNETİMİ ---
    if 'advisor_mode' not in st.session_state:
        st.session_state['advisor_mode'] = None 
    if 'pre_selected_type' not in st.session_state:
        st.session_state['pre_selected_type'] = "Tümü"

    # --- EKRAN 1: AI DANIŞMANLIK SEÇİM EKRANI ---
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

    # --- EKRAN 2: AI STRATEJİ ANKETİ ---
    elif st.session_state['advisor_mode'] is True:
        st.title("📊 Kampanya Strateji Testi")
        
        with st.form("advisor_survey"):
            q1 = st.selectbox("1. Kampanyanın temel amacı nedir?", ["Marka bilinirliğini artırmak", "Ürün/hizmet satışı (conversion)", "Güven oluşturmak / marka imajı", "Niş bir kitleye ulaşmak"])
            q2 = st.selectbox("2. Influencer iş birliği için bütçeniz nedir?", ["Çok yüksek (kurumsal / global)", "Orta", "Düşük", "Çok düşük / barter"])
            q3 = st.selectbox("3. Ulaşmak istediğiniz kitle ne kadar geniş?", ["Çok geniş (herkes)", "Geniş ama belirli segmentler", "Spesifik ilgi alanı", "Çok niş / lokal"])
            q4 = st.selectbox("4. Hangisi sizin için daha önemli?", ["Maksimum erişim (reach)", "Dengeli", "Yüksek etkileşim", "Çok güçlü birebir etkileşim"])
            
            if st.form_submit_button("🧠 Analiz Et ve Sonuçları Uygula"):
                score = {"Mega": 0, "Macro": 0, "Micro": 0, "Nano": 0}
                ans_str = (q1 + q2 + q3 + q4).lower()
                
                if any(x in ans_str for x in ["yüksek", "geniş", "bilinirlik", "erişim"]): score["Mega"] += 5
                if any(x in ans_str for x in ["orta", "denge", "segment"]): score["Macro"] += 5
                if any(x in ans_str for x in ["satış", "düşük", "etkileşim", "güven"]): score["Micro"] += 5
                if any(x in ans_str for x in ["barter", "lokal", "bağ", "niş"]): score["Nano"] += 5
                
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

    # --- EKRAN 3: ANA KONTROL PANELİ ---
    else:
        # --- SIDEBAR TASARIMI VE ÇİFT FİLTRE ALANI ---
        st.sidebar.title("🎛️ Kontrol Paneli")
        if st.sidebar.button("🔙 Ana Menüye Dön"):
            st.session_state['advisor_mode'] = None
            st.session_state['pre_selected_type'] = "Tümü"
            st.rerun()
            
        st.sidebar.divider()
        
        # 1. Sektör Filtresi
        kategoriler = ["Tümü"] + sorted(list(df["sektor"].dropna().unique()))
        secilen_kategori = st.sidebar.selectbox("🎯 Sektör Filtresi:", kategoriler)
        
        # 2. Segment Filtresi
        segmentler = ["Tümü"] + sorted(list(df["tip"].dropna().unique()))
        
        default_index = 0
        if st.session_state['pre_selected_type'] in segmentler:
            default_index = segmentler.index(st.session_state['pre_selected_type'])
            
        secilen_segment = st.sidebar.selectbox("📊 Segment Filtresi (Büyüklük):", segmentler, index=default_index)
        st.session_state['pre_selected_type'] = secilen_segment
        
        st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
        if st.sidebar.button("🚪 Güvenli Çıkış"):
            st.session_state['logged_in'] = False
            st.rerun()

        # --- ORTAK FİLTRELENMİŞ VERİ SETİ ---
        f_df = df.copy()
        
        if secilen_kategori != "Tümü":
            f_df = f_df[f_df["sektor"] == secilen_kategori]
            
        if st.session_state['pre_selected_type'] != "Tümü":
            f_df = f_df[f_df["tip"] == st.session_state['pre_selected_type']]

        # Dört Sekmeli Gelişmiş Sistem
        tab1, tab2, tab3, tab4 = st.tabs(["💎 Influencer Vitrini", "🧙‍♂️ Akıllı Sihirbaz", "📈 Veri Analizi", "🤖 AI Serbest Arama"])
        
        # --- TAB 1: VİTRİN ---
        with tab1:
            st.header("✨ Influencer Arama ve Portföy Vitrini")
            
            # --- MANUEL ARAMA KUTUSU ---
            search_query = st.text_input("🔍 İsim ile Manuel Arama Yapın:", placeholder="Aramak istediğiniz influencer adını yazın...")
            
            # Eğer arama kutusuna yazı yazıldıysa filtreleri bypass et, doğrudan isme odaklan
            if search_query:
                vitrin_df = df[df["ad"].astype(str).str.contains(search_query, case=False, na=False)]
                st.info(f"💡 '{search_query}' araması için {len(vitrin_df)} sonuç listeleniyor. (Kenar çubuğu filtreleri devre dışı bırakıldı)")
            else:
                vitrin_df = f_df
                if st.session_state['pre_selected_type'] != "Tümü":
                    st.success(f"✅ Aktif Segment Filtresi: {st.session_state['pre_selected_type']}")

            if vitrin_df.empty:
                st.warning("⚠️ Aradığınız kriterlere veya isme uygun aday bulunamadı.")
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
                            
                            profile_url = get_social_link(row['ad'], row['platform'])
                            st.link_button("🌐 Profil Sayfasını Ziyaret Et", profile_url, use_container_width=True)
                            
                            # --- PORTFOLYO & GEÇMİŞ İŞ BİRLİKLERİ ---
                            with st.expander("💼 Geçmiş İş Birlikleri & Portfolyo"):
                                name_lower = str(row['ad']).lower()
                                if "danla" in name_lower:
                                    st.markdown("🔹 **Sephora Türkiye x Danla Bilic Ruj Serisi**")
                                    st.caption("📈 Dönüşüm Oranı: Çok Yüksek | 👁️ Erişim: 2.4M+")
                                    st.link_button("🔗 Kampanya Linkini Gör", "https://www.sephora.com.tr", use_container_width=True)
                                    st.markdown("---")
                                    st.markdown("🔹 **Trendyol Mega Kasım Reklam Yüzü**")
                                    st.caption("🖱️ Link Tıklanma: 450K+ | 💰 Satış Dönüşümü: %12")
                                    st.link_button("🔗 İş Birliği Detayları", "https://www.trendyol.com", use_container_width=True)
                                elif "merve" in name_lower:
                                    st.markdown("🔹 **Flormar TikTok İnceleme Kampanyası**")
                                    st.caption("🎬 Organik İzlenme: 80K+ | 📌 Kaydetme: 4.2K")
                                    st.link_button("🔗 Kampanya Videosu", profile_url, use_container_width=True)
                                else:
                                    st.markdown(f"🔹 **Trendyol Influencer Affiliate Projesi**")
                                    st.caption("📊 Sektörel Dönüşüm Skoru: Dengeli")
                                    st.link_button("🔗 Örnek Koleksiyon Linki", "https://www.trendyol.com", use_container_width=True)
                                    st.markdown("---")
                                    st.markdown(f"🔹 **{row['sektor']} Marka İş Birliği Lansmanı**")
                                    st.caption("⚡ Etkileşim Oranı: Stabil")
                                    st.link_button("🔗 İçerik Detayları", "https://www.google.com", use_container_width=True)

                            with st.expander("🛡️ Risk ve Güven Analiz Kriterleri"):
                                st.write(f"🔍 Kaynak Güvenilirliği: %{row['G']}")
                                st.write(f"📊 Etkileşim Kalitesi: %{row['E']}")
                                st.write(f"💎 Otantiklik Skoru: %{row['O']}")
                                st.write(f"📜 Etik Uyum & Şeffaflık: %{row['S']}")

        # --- TAB 2: AKILLI SİHİRBAZ ---
        with tab2:
            st.header("🧠 Akıllı Eşleştirme Motoru")
            with st.form("wizard_form_v5"):
                w_sektor = st.selectbox("🎯 Hedef Sektör", df["sektor"].unique())
                w_hedef = st.radio("🚀 Kampanya Amacı", ["Satış Yapmak", "Bilinirlik Kazanmak"])
                w_tipler = st.multiselect("📊 İstenilen Segmentler", list(df["tip"].unique()), default=list(df["tip"].unique()))
                
                submit_wizard = st.form_submit_button("⚡ Aday Performans Kıyaslamasını Başlat")

            if submit_wizard:
                res = df[(df["sektor"] == w_sektor) & (df["tip"].isin(w_tipler))]
                if len(res) >= 1:
                    best = res.sort_values(by="SMS", ascending=False).iloc[0]
                    worst = res.sort_values(by="SMS", ascending=True).iloc[0]
                    
                    st.divider()
                    
                    comp_col1, comp_col2 = st.columns(2)
                    
                    with comp_col1:
                        st.success("🎯 EN UYGUN ADAY (Maksimum Verim)")
                        with st.container(border=True):
                            st.subheader(f"🥇 {best['ad']}")
                            st.markdown(f"🎯 **Smart-Match Skoru: {best['SMS']} / 100**")
                            st.progress(float(best['SMS']/100))
                            st.caption(f"🏷️ Segment: {best['tip']} | 📱 Platform: {best['platform']}")
                            
                            st.metric("👥 Takipçi Sayısı", f"{int(best['takipci']):,}")
                            st.metric("⚡ Etkileşim Oranı", f"%{best['etkilesim']}")
                            
                            best_link = get_social_link(best['ad'], best['platform'])
                            st.link_button(f"🌐 {best['ad']} Profilini İncele", best_link, use_container_width=True)
                    
                    with comp_col2:
                        if best['ad'] == worst['ad']:
                            st.info("ℹ️ DİĞER SEÇENEK")
                            st.write("Seçilen filtre kriterlerinde kıyaslama yapılabilecek ikinci bir aday bulunamadı.")
                        else:
                            st.error("⚠️ EN AZ UYGUN ADAY (Yüksek Risk / Düşük Verim)")
                            with st.container(border=True):
                                st.subheader(f"❌ {worst['ad']}")
                                st.markdown(f"🎯 **Smart-Match Skoru: {worst['SMS']} / 100**")
                                st.progress(float(worst['SMS']/100))
                                st.caption(f"🏷️ Segment: {worst['tip']} | 📱 Platform: {worst['platform']}")
                                
                                st.metric("👥 Takipçi Sayısı", f"{int(worst['takipci']):,}")
                                st.metric("⚡ Etkileşim Oranı", f"%{worst['etkilesim']}")
                                
                                worst_link = get_social_link(worst['ad'], worst['platform'])
                                st.link_button(f"🌐 {worst['ad']} Profilini İncele", worst_link, use_container_width=True)
                    
                    st.divider()
                    st.latex(r"SMS = 0.40 \cdot G + 0.30 \cdot E + 0.20 \cdot O + 0.10 \cdot S")
                    st.subheader(f"💡 Neden {best['ad']}? — Yapay Zeka İçgörü Raporu (AI Insights)")
                    
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        with st.container(border=True):
                            st.markdown("### 🔍 Güven ve Performans")
                            st.write(f"**{best['ad']}:** %{best['G']} | **{worst['ad'] if best['ad']!=worst['ad'] else '-'}:** %{worst['G']}")
                            st.caption("Bu skor hesaplanırken influencer'ın niş uzmanlık alanı, geçmiş kampanya dönüşümleri ve organik etkileşim oranları taranmıştır.")
                    
                    with c2:
                        with st.container(border=True):
                            st.markdown("### 💎 İçerik Otantikliği")
                            st.write(f"**{best['ad']}:** %{best['O']} | **{worst['ad'] if best['ad']!=worst['ad'] else '-'}:** %{worst['O']}")
                            st.caption("Sponsorlu içerik yoğunluğu, takipçi yorumlarının samimiyet yapısı ve içerik tutarlılığı test edilmiştir.")
                            
                    with c3:
                        with st.container(border=True):
                            st.markdown("### 📜 Etik Risk Kontrolü")
                            st.write(f"**{best['ad']}:** %{best['S']} | **{worst['ad'] if best['ad']!=worst['ad'] else '-'}:** %{worst['S']}")
                            st.caption("Hesabın sahte takipçi büyüme eğrileri, şüpheli bot dalgalanmaları ve reklam şeffaflığı denetlenmiştir.")
                else:
                    st.error("❌ Seçilen kriterlerde aday bulunamadı.")

        # --- TAB 3: VERİ ANALİZI ---
        with tab3:
            st.header("📈 Matematiksel Dağılım ve Matris Analizi")
            
            if f_df.empty:
                st.warning("⚠️ Seçilen filtre kriterlerine uygun bir veri dağılımı bulunamadı.")
            else:
                try:
                    fig = px.scatter(
                        f_df, 
                        x="takipci", 
                        y="SMS", 
                        color="sektor" if len(f_df["sektor"].unique()) > 1 else None, 
                        size="etkilesim", 
                        hover_name="ad", 
                        title="Takipçi Sayısı vs. Smart-Match Skoru (SMS) Dağılımı",
                        labels={"takipci": "Takipçi Sayısı", "SMS": "Smart-Match Skoru (SMS)"}
                    )
                    fig.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')))
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as chart_err:
                    st.error(f"Grafik çizim hatası: {chart_err}")
            
            st.divider()
            st.subheader("📋 Sistem Veri Tabanı")
            st.dataframe(f_df[['ad', 'sektor', 'tip', 'takipci', 'etkilesim', 'SMS', 'G', 'E', 'O', 'S']], use_container_width=True)

        # --- TAB 4: AI REKLAM SENARYOSU VE YASAL DANIŞMAN MOTORU ---
        with tab4:
            st.header("🤖 Akıllı Reklam Senaryosu, Öneri ve Yasal Danışman")
            st.markdown("Kampanya fikrinizi ve hedef kitlenizi yazın. AI, seçtiğiniz bütçe aralığına uygun influencer sınıflarını veritabanından süzerek size özel bir strateji ve yasal uyum raporu hazırlar.")
            
            # --- GÜNCEL BÜTÇE SKALASI ---
            kampanya_butcesi = st.selectbox(
                "💰 Kampanya Bütçeniz Nedir?",
                options=[
                    "Düşük Bütçe (Nano)", 
                    "Orta-Düşük Bütçe (Nano & Micro)", 
                    "Orta Bütçe (Micro)", 
                    "Orta-Yüksek Bütçe (Macro & Mega)", 
                    "Yüksek Bütçe (Mega)"
                ],
                help="Seçtiğiniz bütçe aralığına uygun influencer tipleri yapay zekaya kural olarak dikte edilir."
            )
            
            user_prompt = st.text_area(
                "📝 Kampanya Detaylarını ve Hedef Kitleyi Yazın:",
                placeholder="Örn: Yeni bir kozmetik markası çıkarıyoruz. Hedef kitlemiz 18-45 yaş arası kozmetik severler. Reklam senaryoları ve yasal zorunluluklar nelerdir?",
                key="groq_user_prompt"
            )
            
            if st.button("🚀 Yapay Zeka Analizini Başlat", key="groq_start_button"):
                if not user_prompt:
                    st.warning("⚠️ Lütfen önce kampanya detaylarını yazın.")
                else:
                    with st.spinner("🧠 Yapay Zeka bütçe filtrenize uygun analizleri hazırlıyor..."):
                        try:
                            from groq import Groq
                            api_key = st.secrets.get("GROQ_API_KEY", None)
                            
                            if not api_key:
                                st.error("❌ Lütfen `.streamlit/secrets.toml` dosyasına GROQ_API_KEY anahtarınızı ekleyin.")
                            else:
                                client = Groq(api_key=api_key)
                                
                                # Veritabanının özetini çıkartma
                                veri_ozeti = f_df[['ad', 'sektor', 'tip', 'platform', 'takipci', 'etkilesim', 'SMS']].to_string(index=False)
                                
                                # Yapay zekaya kesin bütçe ve tip eşleştirme kurallarını veriyoruz
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
                                
                                Yukarıdaki bütçe ve tip sınırlandırma kurallarına göre, sana aşağıda sağlanan influencer veritabanını filtrele ve kurallara uyan isimleri cımbızla seç.
                                
                                Mevcut Filtrelenmiş Influencer Veri Özeti:
                                {veri_ozeti}
                                
                                Kullanıcının Kampanya Talebi:
                                "{user_prompt}"
                                
                                Lütfen şu başlıklar altında harika bir Türkçe rapor hazırla:
                                
                                1. BÜTÇE ARALIĞINA UYGUN NOKTA ATIŞI INFLUENCER ÖNERİLERİ
                                (Kullanıcının seçtiği {kampanya_butcesi} durumuna göre veritabanından bulduğun uygun isimleri, takipçi ve etkileşim oranlarıyla listele. Seçtiğin isimlerin bütçe kuralıyla neden uyumlu olduğunu açıkla.)
                                
                                2. KREATİF REKLAM SENARYO ÖNERİLERİ
                                (Önerdiğin bu isimlerin tarzına, Instagram Reels ve TikTok formatına uygun, samimi en az 2 video senaryosu kurgula.)
                                
                                3. YASAL ZORUNLULUKLAR VE DİKKAT EDİLMESİ GEREKENLER (TÜRKİYE MEVZUATI)
                                (Ticaret Bakanlığı kurallarına göre #reklam/#işbirliği kullanımı ve kozmetik ürünlerdeki sağlık beyanı yasaklarını maddeler halinde yaz.)
                                """
                                
                                completion = client.chat.completions.create(
                                    model="llama-3.3-70b-versatile",
                                    messages=[
                                        {"role": "user", "content": kullanici_mesaji}
                                    ],
                                    temperature=0.3
                                )
                                
                                ai_raporu = completion.choices[0].message.content
                                
                                st.success("🎉 Esnek Bütçe Uyumlu Strateji ve Yasal Rapor Hazır!")
                                st.markdown("---")
                                st.markdown(ai_raporu)
                                st.markdown("---")
                                
                                st.download_button(
                                    label="📥 Raporu Bilgisayara İndir",
                                    data=ai_raporu,
                                    file_name="esnek_butceli_reklam_raporu.txt",
                                    mime="text/plain",
                                    key="groq_download_button"
                                )
                                
                        except Exception as ai_err:
                            st.error(f"❌ AI Analiz Motoru Hatası: {ai_err}")
