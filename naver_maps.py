import streamlit as st 
from dotenv import load_dotenv 
import os 
import requests 
import streamlit.components.v1 as components # Iframe 렌더링을 위해 추가
from streamlit_geolocation import streamlit_geolocation 
import math 

# 1. 환경 변수 로드
load_dotenv() 
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID") 
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET") 

# 2. 페이지 설정
st.set_page_config(
    page_title="네이버 지도 대시보드", 
    page_icon="🗺️", 
    layout="wide" 
)

st.title("🗺️ 네이버 검색 + 네이버 지도 (Iframe)")

# 3. API 키 유효성 검사
if not NAVER_CLIENT_ID:
    st.error("⚠️ .env 파일에 NAVER_CLIENT_ID를 설정해주세요!") 
    st.stop() 

# 4. Session State 초기화
if "search_results" not in st.session_state:
    st.session_state.search_results = [] 
if "last_query" not in st.session_state:
    st.session_state.last_query = "" 
if "user_location" not in st.session_state:
    st.session_state.user_location = None 

# 5. 현재 위치 가져오기
st.subheader("📍 내 위치")
location = streamlit_geolocation()

if location and location.get("latitude") and location.get("longitude"):
    st.session_state.user_location = {
        "lat": location["latitude"],
        "lng": location["longitude"]
    }
    st.success(f"현재 위치 감지됨: {location['latitude']:.6f}, {location['longitude']:.6f}")
else:
    st.info("위치 버튼을 클릭하여 현재 위치를 가져오세요.")

# 6. 거리 계산 함수
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371 
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# 7. 네이버 검색 API (기존 로직 유지)
def search_places(query, user_lat=None, user_lng=None):
    if not query: return []
    url = "https://openapi.naver.com/v1/search/local.json"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    params = {"query": query, "display": 10, "sort": "random"}
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            items = response.json().get("items", [])
            results = []
            for item in items:
                lng = int(item.get("mapx", 0)) / 10000000.0
                lat = int(item.get("mapy", 0)) / 10000000.0
                if lat > 0 and lng > 0:
                    dist = calculate_distance(user_lat, user_lng, lat, lng) if user_lat else None
                    results.append({
                        "title": item.get("title", "").replace("<b>", "").replace("</b>", ""),
                        "address": item.get("roadAddress", "") or item.get("address", ""),
                        "lat": lat, "lng": lng, "distance": dist
                    })
            if user_lat: results.sort(key=lambda x: x["distance"] or 9999)
            return results
    except: return []
    return []

# 8. 검색 UI
st.subheader("🔍 장소 검색")
with st.form(key="search_form"):
    search_query = st.text_input("검색할 장소", placeholder="예: 무역협회, 유라코퍼레이션")
    search_clicked = st.form_submit_button("검색")

if search_clicked and search_query:
    u_lat = st.session_state.user_location["lat"] if st.session_state.user_location else None
    u_lng = st.session_state.user_location["lng"] if st.session_state.user_location else None
    st.session_state.search_results = search_places(search_query, u_lat, u_lng)
    st.session_state.last_query = search_query

# 9. 네이버 지도 HTML 생성 (Iframe 방식)
def generate_naver_map_html():
    # 지도 중심점 설정
    if st.session_state.user_location:
        c_lat, c_lng = st.session_state.user_location["lat"], st.session_state.user_location["lng"]
    elif st.session_state.search_results:
        c_lat, c_lng = st.session_state.search_results[0]["lat"], st.session_state.search_results[0]["lng"]
    else:
        c_lat, c_lng = 37.5665, 126.9780 # 서울시청

    # 마커 데이터를 JSON처럼 문자열화
    markers_js = ""
    if st.session_state.user_location:
        markers_js += f"""
        new naver.maps.Marker({{
            position: new naver.maps.LatLng({st.session_state.user_location['lat']}, {st.session_state.user_location['lng']}),
            map: map,
            icon: {{ content: '<div style="color:blue; font-size:20px;">🔵</div>', anchor: new naver.maps.Point(10, 10) }}
        }});
        """
    
    for idx, p in enumerate(st.session_state.search_results, 1):
        markers_js += f"""
        var marker{idx} = new naver.maps.Marker({{
            position: new naver.maps.LatLng({p['lat']}, {p['lng']}),
            map: map,
            title: "{p['title']}"
        }});
        """

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <script type="text/javascript" src="https://openapi.map.naver.com/openapi/v3/maps.js?ncpClientId={NAVER_CLIENT_ID}"></script>
        <style>#map {{ width: 100%; height: 500px; }} body {{ margin: 0; }}</style>
    </head>
    <body>
        <div id="map"></div>
        <script>
            var mapOptions = {{
                center: new naver.maps.LatLng({c_lat}, {c_lng}),
                zoom: 14
            }};
            var map = new naver.maps.Map('map', mapOptions);
            {markers_js}
        </script>
    </body>
    </html>
    """
    return html_code

# 10. 화면 렌더링
col_map, col_list = st.columns([2, 1])

with col_map:
    st.subheader("🗺️ 네이버 지도")
    map_html = generate_naver_map_html()
    components.html(map_html, height=520)

with col_list:
    st.subheader("📋 목록")
    if st.session_state.search_results:
        for p in st.session_state.search_results:
            st.write(f"**{p['title']}**")
            st.caption(f"{p['address']}")
            if p['distance']: st.write(f"📏 {p['distance']:.2f} km")
            st.divider()
    else:
        st.write("검색 결과가 없습니다.")

st.caption("© 2026 - Naver Maps JS API v3")