import os
import json
import requests
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

# =========================================================
# 1) Env + Page
# =========================================================
load_dotenv()
KAKAO_API_KEY = os.getenv("KAKAO_MAP_API_KEY")     # Kakao JS key
EXCHANGE_KEY = os.getenv("EXCHANGE_RATE_KEY")     # exchangerate-api.com key

st.set_page_config(page_title="Guide Intégré : Jeju + Séoul (FR)", layout="wide")


# =========================================================
# 2) Exchange Rate (KRW -> EUR)
# =========================================================
@st.cache_data(ttl=3600)
def get_eur_rate(api_key: str) -> float:
    """
    exchangerate-api.com에서 base=KRW 기준 EUR 환율을 가져옵니다.
    실패 시 대략값 사용.
    """
    fallback = 0.00068  # 1 KRW ~= 0.00068 EUR (대략)
    if not api_key:
        return fallback
    try:
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/KRW"
        r = requests.get(url, timeout=10)
        data = r.json()
        if data.get("result") == "success":
            return float(data["conversion_rates"]["EUR"])
        return fallback
    except Exception:
        return fallback


eur_rate = get_eur_rate(EXCHANGE_KEY)


def krw_to_eur(krw: int | float, rate: float) -> float:
    return float(krw) * float(rate)


# =========================================================
# 3) Data: JEJU + SEOUL (Spots & Restaurants)
# =========================================================

# -------------------------
# JEJU Areas (11)
# -------------------------
JEJU_AREAS_11 = [
    "Jeju-si (제주시)",
    "Seogwipo-si (서귀포시)",
    "Aewol-eup (애월읍)",
    "Hallim-eup (한림읍)",
    "Hankyung-myeon (한경면)",
    "Jocheon-eup (조천읍)",
    "Gujwa-eup (구좌읍)",
    "Seongsan-eup (성산읍)",
    "Pyoseon-myeon (표선면)",
    "Andeok-myeon (안덕면)",
    "Daejeong-eup (대정읍)",
]

# -------------------------
# SEOUL Areas (incl. Seongsu, Hongdae, Itaewon, Gangnam)
# -------------------------
SEOUL_AREAS = [
    "Seongsu (성수)",
    "Hongdae (홍대)",
    "Itaewon (이태원)",
    "Gangnam (강남)",
    "Myeongdong (명동)",
    "Insadong (인사동)",
    "Gyeongbokgung (경복궁/광화문)",
    "Bukchon (북촌)",
]

# -------------------------
# JEJU Spots
# -------------------------
JEJU_SPOTS = [
    {"name": "Seongsan Ilchulbong (성산일출봉)", "area": "Seongsan-eup (성산읍)", "lat": 33.4585, "lng": 126.9424,
     "price_krw": 5000, "type": "Spot",
     "desc_fr": "Cône de tuf volcanique classé UNESCO, célèbre pour le lever du soleil."},

    {"name": "Manjanggul (만장굴)", "area": "Gujwa-eup (구좌읍)", "lat": 33.5283, "lng": 126.7716,
     "price_krw": 4000, "type": "Spot",
     "desc_fr": "Un tunnel de lave impressionnant, très apprécié pour sa fraîcheur naturelle."},

    {"name": "Plage de Hyeopjae (협재해수욕장)", "area": "Hallim-eup (한림읍)", "lat": 33.3941, "lng": 126.2397,
     "price_krw": 0, "type": "Spot",
     "desc_fr": "Sable blanc et mer émeraude, vue sur l’île de Biyangdo."},

    {"name": "Marché Olle (서귀포 올레시장)", "area": "Seogwipo-si (서귀포시)", "lat": 33.2493, "lng": 126.5636,
     "price_krw": 0, "type": "Spot",
     "desc_fr": "Marché traditionnel animé : street food locale et ambiance authentique."},

    {"name": "O’sulloc Tea Museum (오설록 티뮤지엄)", "area": "Andeok-myeon (안덕면)", "lat": 33.3068, "lng": 126.2895,
     "price_krw": 0, "type": "Spot",
     "desc_fr": "Balade dans les champs de thé + dégustations, parfait pour les photos."},

    {"name": "Hallasan (한라산)", "area": "Jeju-si (제주시)", "lat": 33.3617, "lng": 126.5292,
     "price_krw": 0, "type": "Spot",
     "desc_fr": "Le sommet emblématique de Jeju : randonnée selon saison et niveau."},
]

# -------------------------
# JEJU Restaurants (rating 3.5+ sample)
# menu items are KRW; displayed in EUR
# -------------------------
JEJU_RESTOS = [
    {"name": "Sukseongdo (숙성도)", "area": "Jeju-si (제주시)", "lat": 33.4851, "lng": 126.4817,
     "type": "Resto", "rating": 4.5,
     "desc_fr": "Porc noir de Jeju (heukdwaeji) maturé, très populaire.",
     "menu": [{"name": "Assortiment porc noir", "price_krw": 32000}, {"name": "Ragoût kimchi", "price_krw": 9000}]},

    {"name": "Myeongjin Jeonbok (명진전복)", "area": "Gujwa-eup (구좌읍)", "lat": 33.5351, "lng": 126.8525,
     "type": "Resto", "rating": 4.2,
     "desc_fr": "Spécialité d’ormeaux (abalone) : riz en marmite + grillé.",
     "menu": [{"name": "Riz en marmite à l’ormeau", "price_krw": 15000}, {"name": "Ormeau grillé", "price_krw": 22000}]},

    {"name": "Seongsan Seafood (성산 해산물)", "area": "Seongsan-eup (성산읍)", "lat": 33.4597, "lng": 126.9398,
     "type": "Resto", "rating": 3.7,
     "desc_fr": "Pratique près de Seongsan : soupe fruits de mer / abalone porridge.",
     "menu": [{"name": "Porridge à l’ormeau", "price_krw": 16000}, {"name": "Soupe fruits de mer", "price_krw": 14000}]},

    {"name": "Hyeopjae Noodles (협재 국수)", "area": "Hallim-eup (한림읍)", "lat": 33.3926, "lng": 126.2407,
     "type": "Resto", "rating": 3.7,
     "desc_fr": "Après la plage : nouilles / ramyeon aux fruits de mer.",
     "menu": [{"name": "Porridge à l’ormeau", "price_krw": 14000}, {"name": "Ramyeon fruits de mer", "price_krw": 11000}]},
]

# -------------------------
# SEOUL Spots (incl. Seongsu, Hongdae, Itaewon, Gangnam)
# -------------------------
SEOUL_SPOTS = [
    {"name": "Gyeongbokgung (경복궁)", "area": "Gyeongbokgung (경복궁/광화문)", "lat": 37.5796, "lng": 126.9770,
     "price_krw": 3000, "type": "Spot",
     "desc_fr": "Palais royal iconique : architecture, relève de la garde, photos."},

    {"name": "Bukchon Hanok Village (북촌한옥마을)", "area": "Bukchon (북촌)", "lat": 37.5826, "lng": 126.9830,
     "price_krw": 0, "type": "Spot",
     "desc_fr": "Ruelles traditionnelles de hanok, ambiance unique entre passé et présent."},

    {"name": "Insadong (인사동)", "area": "Insadong (인사동)", "lat": 37.5740, "lng": 126.9849,
     "price_krw": 0, "type": "Spot",
     "desc_fr": "Artisanat, thé traditionnel, souvenirs, galeries."},

    {"name": "Myeongdong (명동)", "area": "Myeongdong (명동)", "lat": 37.5637, "lng": 126.9850,
     "price_krw": 0, "type": "Spot",
     "desc_fr": "Shopping + street food, très pratique pour visiteurs."},

    {"name": "Hongdae Street (홍대거리)", "area": "Hongdae (홍대)", "lat": 37.5563, "lng": 126.9220,
     "price_krw": 0, "type": "Spot",
     "desc_fr": "Quartier jeune : cafés, musique, boutiques, ambiance nocturne."},

    {"name": "Itaewon (이태원)", "area": "Itaewon (이태원)", "lat": 37.5349, "lng": 126.9946,
     "price_krw": 0, "type": "Spot",
     "desc_fr": "Quartier international : restaurants du monde, bars, vues urbaines."},

    {"name": "Seongsu (성수)", "area": "Seongsu (성수)", "lat": 37.5445, "lng": 127.0557,
     "price_krw": 0, "type": "Spot",
     "desc_fr": "Le ‘Brooklyn de Séoul’ : cafés, concept stores, street vibes."},

    {"name": "Gangnam (강남)", "area": "Gangnam (강남)", "lat": 37.4979, "lng": 127.0276,
     "price_krw": 0, "type": "Spot",
     "desc_fr": "Quartier moderne : shopping, beauté, nightlife, COEX à proximité."},

    {"name": "N Seoul Tower (남산타워)", "area": "Myeongdong (명동)", "lat": 37.5512, "lng": 126.9882,
     "price_krw": 21000, "type": "Spot",
     "desc_fr": "Panorama sur Séoul. Idéal au coucher du soleil."},
]

# -------------------------
# SEOUL Restaurants (rating 3.5+ sample)
# -------------------------
SEOUL_RESTOS = [
    {"name": "Seongsu BBQ Pick (성수 바비큐)", "area": "Seongsu (성수)", "lat": 37.5465, "lng": 127.0535,
     "type": "Resto", "rating": 4.1,
     "desc_fr": "BBQ coréen dans l’ambiance trendy de Seongsu.",
     "menu": [{"name": "Samgyeopsal (porc)", "price_krw": 17000}, {"name": "Kimchi-jjigae", "price_krw": 9000}]},

    {"name": "Hongdae Fried Chicken (홍대 치킨)", "area": "Hongdae (홍대)", "lat": 37.5568, "lng": 126.9214,
     "type": "Resto", "rating": 3.8,
     "desc_fr": "Classique pour une soirée : poulet frit + bière.",
     "menu": [{"name": "Poulet frit", "price_krw": 20000}, {"name": "Bière", "price_krw": 6000}]},

    {"name": "Itaewon International Bite (이태원)", "area": "Itaewon (이태원)", "lat": 37.5344, "lng": 126.9940,
     "type": "Resto", "rating": 4.0,
     "desc_fr": "Options variées (international) : parfait en groupe.",
     "menu": [{"name": "Plat signature", "price_krw": 18000}, {"name": "Cocktail", "price_krw": 14000}]},

    {"name": "Gangnam K-Food (강남 한식)", "area": "Gangnam (강남)", "lat": 37.4988, "lng": 127.0289,
     "type": "Resto", "rating": 3.9,
     "desc_fr": "Dîner facile à Gangnam : plats coréens populaires.",
     "menu": [{"name": "Bibimbap", "price_krw": 12000}, {"name": "Bulgogi", "price_krw": 17000}]},

    {"name": "Myeongdong Kalguksu (명동 칼국수)", "area": "Myeongdong (명동)", "lat": 37.5632, "lng": 126.9862,
     "type": "Resto", "rating": 3.7,
     "desc_fr": "Nouilles chaudes (kalguksu) + dumplings, très apprécié.",
     "menu": [{"name": "Kalguksu", "price_krw": 11000}, {"name": "Mandu", "price_krw": 10000}]},
]

# =========================================================
# 4) Integrated structures
# =========================================================
CITY_DATA = {
    "Jeju (제주)": {
        "areas": JEJU_AREAS_11,
        "spots": JEJU_SPOTS,
        "restos": JEJU_RESTOS,
        "map_center": (33.38, 126.55),
        "map_level": 10,
    },
    "Séoul (서울)": {
        "areas": SEOUL_AREAS,
        "spots": SEOUL_SPOTS,
        "restos": SEOUL_RESTOS,
        "map_center": (37.5665, 126.9780),
        "map_level": 8,
    }
}


def spot_by_name(city_key: str, name: str):
    return next((s for s in CITY_DATA[city_key]["spots"] if s["name"] == name), None)


# =========================================================
# 5) Itineraries (Jeju + Seoul) : 2D1N ~ 6D5N
# =========================================================
JEJU_ROUTES = {
    "2 jours / 1 nuit (2D1N) - Essentiel": [
        {"day": "Jour 1 (Ouest)", "spots": ["Plage de Hyeopjae (협재해수욕장)", "O’sulloc Tea Museum (오설록 티뮤지엄)"]},
        {"day": "Jour 2 (Est)", "spots": ["Seongsan Ilchulbong (성산일출봉)", "Manjanggul (만장굴)"]},
    ],
    "3 jours / 2 nuits (3D2N) - Équilibré": [
        {"day": "Jour 1 (Ouest)", "spots": ["Plage de Hyeopjae (협재해수욕장)"]},
        {"day": "Jour 2 (Sud)", "spots": ["Marché Olle (서귀포 올레시장)"]},
        {"day": "Jour 3 (Est)", "spots": ["Seongsan Ilchulbong (성산일출봉)", "Manjanggul (만장굴)"]},
    ],
    "4 jours / 3 nuits (4D3N) - Détente": [
        {"day": "Jour 1", "spots": ["Plage de Hyeopjae (협재해수욕장)"]},
        {"day": "Jour 2", "spots": ["O’sulloc Tea Museum (오설록 티뮤지엄)"]},
        {"day": "Jour 3", "spots": ["Marché Olle (서귀포 올레시장)"]},
        {"day": "Jour 4", "spots": ["Seongsan Ilchulbong (성산일출봉)"]},
    ],
    "5 jours / 4 nuits (5D4N) - Grand tour": [
        {"day": "Jour 1", "spots": ["Hallasan (한라산)"]},
        {"day": "Jour 2", "spots": ["Plage de Hyeopjae (협재해수욕장)"]},
        {"day": "Jour 3", "spots": ["O’sulloc Tea Museum (오설록 티뮤지엄)"]},
        {"day": "Jour 4", "spots": ["Marché Olle (서귀포 올레시장)"]},
        {"day": "Jour 5", "spots": ["Seongsan Ilchulbong (성산일출봉)", "Manjanggul (만장굴)"]},
    ],
    "6 jours / 5 nuits (6D5N) - Très complet": [
        {"day": "Jour 1", "spots": ["Hallasan (한라산)"]},
        {"day": "Jour 2", "spots": ["Plage de Hyeopjae (협재해수욕장)"]},
        {"day": "Jour 3", "spots": ["O’sulloc Tea Museum (오설록 티뮤지엄)"]},
        {"day": "Jour 4", "spots": ["Marché Olle (서귀포 올레시장)"]},
        {"day": "Jour 5", "spots": ["Manjanggul (만장굴)"]},
        {"day": "Jour 6", "spots": ["Seongsan Ilchulbong (성산일출봉)"]},
    ],
}

SEOUL_ROUTES = {
    "2 jours / 1 nuit (2D1N) - Classiques": [
        {"day": "Jour 1 (Histoire)", "spots": ["Gyeongbokgung (경복궁)", "Bukchon Hanok Village (북촌한옥마을)", "Insadong (인사동)"]},
        {"day": "Jour 2 (Ville)", "spots": ["Myeongdong (명동)", "N Seoul Tower (남산타워)"]},
    ],
    "3 jours / 2 nuits (3D2N) - Mix": [
        {"day": "Jour 1", "spots": ["Gyeongbokgung (경복궁)", "Bukchon Hanok Village (북촌한옥마을)"]},
        {"day": "Jour 2", "spots": ["Myeongdong (명동)", "N Seoul Tower (남산타워)"]},
        {"day": "Jour 3", "spots": ["Hongdae Street (홍대거리)", "Itaewon (이태원)"]},
    ],
    "4 jours / 3 nuits (4D3N) - Quartiers": [
        {"day": "Jour 1 (Tradition)", "spots": ["Gyeongbokgung (경복궁)", "Insadong (인사동)"]},
        {"day": "Jour 2 (Namsan)", "spots": ["Myeongdong (명동)", "N Seoul Tower (남산타워)"]},
        {"day": "Jour 3 (Tendance)", "spots": ["Seongsu (성수)", "Hongdae Street (홍대거리)"]},
        {"day": "Jour 4 (International)", "spots": ["Itaewon (이태원)", "Gangnam (강남)"]},
    ],
    "5 jours / 4 nuits (5D4N) - Très confortable": [
        {"day": "Jour 1", "spots": ["Gyeongbokgung (경복궁)", "Bukchon Hanok Village (북촌한옥마을)"]},
        {"day": "Jour 2", "spots": ["Insadong (인사동)", "Myeongdong (명동)"]},
        {"day": "Jour 3", "spots": ["N Seoul Tower (남산타워)"]},
        {"day": "Jour 4", "spots": ["Seongsu (성수)", "Hongdae Street (홍대거리)"]},
        {"day": "Jour 5", "spots": ["Itaewon (이태원)", "Gangnam (강남)"]},
    ],
    "6 jours / 5 nuits (6D5N) - Full vibes": [
        {"day": "Jour 1", "spots": ["Gyeongbokgung (경복궁)"]},
        {"day": "Jour 2", "spots": ["Bukchon Hanok Village (북촌한옥마을)", "Insadong (인사동)"]},
        {"day": "Jour 3", "spots": ["Myeongdong (명동)"]},
        {"day": "Jour 4", "spots": ["N Seoul Tower (남산타워)"]},
        {"day": "Jour 5", "spots": ["Seongsu (성수)", "Hongdae Street (홍대거리)"]},
        {"day": "Jour 6", "spots": ["Itaewon (이태원)", "Gangnam (강남)"]},
    ],
}

CITY_ROUTES = {
    "Jeju (제주)": JEJU_ROUTES,
    "Séoul (서울)": SEOUL_ROUTES,
}


# =========================================================
# 6) Sidebar (French UI)
# =========================================================
st.sidebar.title("🗺️ Guide Intégré (Jeju + Séoul)")
st.sidebar.markdown(f"**Taux de change (approx.) :** 1 KRW = `{eur_rate:.6f}` EUR")

city = st.sidebar.selectbox("🌍 Choisissez une ville", list(CITY_DATA.keys()))
routes_dict = CITY_ROUTES[city]

st.sidebar.subheader("🗓️ Itinéraires (2D1N → 6D5N)")
route_name = st.sidebar.selectbox("Sélectionnez un itinéraire", list(routes_dict.keys()))
route_days = routes_dict[route_name]

# Spot details (click)
st.sidebar.subheader("📍 Infos lieux (cliquez)")
spot_names = [s["name"] for s in CITY_DATA[city]["spots"]]
selected_spot_name = st.sidebar.radio("Choisissez un lieu", spot_names)
selected_spot = spot_by_name(city, selected_spot_name)

with st.sidebar.expander("Détails", expanded=True):
    if selected_spot:
        p_eur = krw_to_eur(selected_spot["price_krw"], eur_rate)
        price_txt = "Gratuit" if selected_spot["price_krw"] == 0 else f"{p_eur:.2f} €"
        st.write(f"**Nom :** {selected_spot['name']}")
        st.write(f"**Zone :** {selected_spot['area']}")
        st.write(f"**Description :** {selected_spot['desc_fr']}")
        st.write(f"**Prix (estimé) :** {price_txt}")

st.sidebar.subheader("🍴 Restaurants (3.5+)")
area_filter = st.sidebar.selectbox("Filtrer par zone", ["Tous"] + CITY_DATA[city]["areas"])
show_restaurants = st.sidebar.checkbox("Afficher restaurants sur la carte", value=True)
min_rating = st.sidebar.slider("Note minimale", 3.5, 5.0, 3.5, 0.1)


# =========================================================
# 7) Main Layout
# =========================================================
st.title("🇫🇷 Guide Touristique : Jeju + Séoul (Prix en €)")
st.write(f"Taux actuel (approx.) : **1 KRW = {eur_rate:.6f} EUR**")

left, right = st.columns([3, 1], vertical_alignment="top")

# Right: itinerary + restaurant list
with right:
    st.subheader("🧭 Résumé de l’itinéraire")
    for d in route_days:
        with st.expander(d["day"], expanded=True):
            for nm in d["spots"]:
                sp = spot_by_name(city, nm)
                if not sp:
                    continue
                p_eur = krw_to_eur(sp["price_krw"], eur_rate)
                p_txt = "Gratuit" if sp["price_krw"] == 0 else f"{p_eur:.2f} €"
                st.markdown(f"- **{sp['name']}**  · {sp['area']} · {p_txt}")

    st.divider()
    st.subheader("🍽️ Restaurants recommandés")
    restos = [r for r in CITY_DATA[city]["restos"] if r.get("rating", 0) >= min_rating]
    if area_filter != "Tous":
        restos = [r for r in restos if r["area"] == area_filter]

    if not restos:
        st.info("Aucun restaurant trouvé avec ce filtre.")
    else:
        for r in restos:
            st.markdown(f"**{r['name']}**  (⭐ {r['rating']})")
            st.caption(r["area"])
            st.write(r["desc_fr"])
            menu_preview = ", ".join(
                [f"{m['name']} ({krw_to_eur(m['price_krw'], eur_rate):.2f} €)" for m in r["menu"][:2]]
            )
            st.write(f"Menu (ex.) : {menu_preview}")
            st.divider()

# Left: Kakao map with hover tooltips
with left:
    st.subheader("🗺️ Carte (survolez pour menu / prix / infos)")

    # route spots only shown
    route_spot_names = [nm for day in route_days for nm in day["spots"]]
    route_spots = [s for s in CITY_DATA[city]["spots"] if s["name"] in route_spot_names]

    # restaurants (optional)
    restos_map = [r for r in CITY_DATA[city]["restos"] if r.get("rating", 0) >= min_rating]
    if area_filter != "Tous":
        restos_map = [r for r in restos_map if r["area"] == area_filter]
    if not show_restaurants:
        restos_map = []

    # pack for JS
    map_items = []
    for s in route_spots:
        map_items.append({
            "name": s["name"],
            "lat": s["lat"],
            "lng": s["lng"],
            "type": "Spot",
            "area": s["area"],
            "desc_fr": s["desc_fr"],
            "price_krw": s["price_krw"],
            "rating": None,
            "menu": []
        })

    for r in restos_map:
        map_items.append({
            "name": r["name"],
            "lat": r["lat"],
            "lng": r["lng"],
            "type": "Resto",
            "area": r["area"],
            "desc_fr": r["desc_fr"],
            "price_krw": 0,
            "rating": r.get("rating"),
            "menu": r.get("menu", [])
        })

    center_lat, center_lng = CITY_DATA[city]["map_center"]
    level = CITY_DATA[city]["map_level"]

    map_items_json = json.dumps(map_items, ensure_ascii=False)

    map_html = f"""
    <div id="map" style="width:100%;height:660px;border-radius:16px;box-shadow:0 4px 12px rgba(0,0,0,0.12);"></div>
    <script type="text/javascript" src="https://dapi.kakao.com/v2/maps/sdk.js?appkey={KAKAO_API_KEY}"></script>
    <script>
        var container = document.getElementById('map');
        var options = {{ center: new kakao.maps.LatLng({center_lat}, {center_lng}), level: {level} }};
        var map = new kakao.maps.Map(container, options);

        var rate = {eur_rate};
        var data = {map_items_json};

        function eur(krw) {{
            return (krw * rate).toFixed(2);
        }}

        data.forEach(function(item) {{
            var pos = new kakao.maps.LatLng(item.lat, item.lng);

            var marker = new kakao.maps.Marker({{
                map: map,
                position: pos,
                title: item.name
            }});

            var header = '<div style="font-weight:700;font-size:13px;margin-bottom:4px;">' + item.name + '</div>';
            var meta = '<div style="font-size:12px;color:#666;margin-bottom:6px;">' + item.area + '</div>';

            var priceBlock = '';
            if (item.type === "Spot") {{
                priceBlock = (item.price_krw === 0)
                    ? '<div style="font-size:12px;color:#2ecc71;">Gratuit</div>'
                    : '<div style="font-size:12px;color:#2ecc71;">Prix (estimé) : ' + eur(item.price_krw) + ' €</div>';
            }}

            var ratingBlock = '';
            if (item.type === "Resto" && item.rating) {{
                ratingBlock = '<div style="font-size:12px;">⭐ ' + item.rating + '</div>';
            }}

            var menuBlock = '';
            if (item.type === "Resto" && item.menu && item.menu.length > 0) {{
                var rows = item.menu.slice(0,3).map(function(m) {{
                    return '<div style="display:flex;justify-content:space-between;gap:10px;font-size:12px;">'
                        + '<span>' + m.name + '</span>'
                        + '<span style="color:#2ecc71;">' + eur(m.price_krw) + ' €</span>'
                        + '</div>';
                }}).join('');
                menuBlock = '<div style="margin-top:6px;padding-top:6px;border-top:1px solid #eee;">'
                        + '<div style="font-weight:600;font-size:12px;margin-bottom:4px;">Menu phare</div>'
                        + rows
                        + '</div>';
            }}

            var desc = '<div style="font-size:12px;color:#333;margin-top:6px;line-height:1.35;">' + item.desc_fr + '</div>';

            var content =
                '<div style="padding:10px 12px;min-width:230px;max-width:280px;font-family:sans-serif;">'
                + header + meta + priceBlock + ratingBlock + menuBlock + desc
                + '</div>';

            var infowindow = new kakao.maps.InfoWindow({{ content: content }});

            kakao.maps.event.addListener(marker, 'mouseover', function() {{
                infowindow.open(map, marker);
            }});
            kakao.maps.event.addListener(marker, 'mouseout', function() {{
                infowindow.close();
            }});
        }});
    </script>
    """
    components.html(map_html, height=700)

st.success("💡 Astuce : Survolez les marqueurs pour voir les prix en €, les menus et les descriptions. Utilisez la barre latérale pour changer de ville, itinéraire et filtres.")
