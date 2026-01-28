import streamlit as st
from dotenv import load_dotenv
import os
import requests
import folium
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation
import math

# 1. 환경 변수 로드
load_dotenv()
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

# 2. 페이지 설정
st.set_page_config(
    page_title="네이버 검색 + 지도",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ 네이버 검색 + 지도 (위치 기반)")

# 3. API 키 유효성 검사
if not NAVER_CLIENT_ID or NAVER_CLIENT_ID == "your_naver_client_id_here":
    st.error("⚠️ .env 파일에 네이버 API 키를 설정해주세요!")
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
    st.success(f"현재 위치: {location['latitude']:.6f}, {location['longitude']:.6f}")
else:
    st.info("위치 버튼을 클릭하여 현재 위치를 가져오세요. 위치 권한을 허용해야 합니다.")

# 6. 거리 계산 함수 (Haversine)
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # 지구 반지름 (km)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# 7. 네이버 검색 API 호출 함수 (위치 기반)
def search_places(query, user_lat=None, user_lng=None):
    if not query:
        return []

    url = "https://openapi.naver.com/v1/search/local.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    params = {
        "query": query,
        "display": 10,
        "sort": "random"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])

            results = []
            for item in items:
                mapx = int(item.get("mapx", 0))
                mapy = int(item.get("mapy", 0))

                lng = mapx / 10000000.0
                lat = mapy / 10000000.0

                if lat > 0 and lng > 0:
                    distance = None
                    if user_lat and user_lng:
                        distance = calculate_distance(user_lat, user_lng, lat, lng)

                    results.append({
                        "title": item.get("title", "").replace("<b>", "").replace("</b>", ""),
                        "address": item.get("roadAddress", "") or item.get("address", ""),
                        "category": item.get("category", ""),
                        "lat": lat,
                        "lng": lng,
                        "distance": distance
                    })

            # 거리순 정렬 (가까운 순)
            if user_lat and user_lng:
                results.sort(key=lambda x: x["distance"] if x["distance"] else float('inf'))

            return results
        else:
            st.error(f"검색 API 오류: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"검색 중 오류 발생: {e}")
        return []

# 8. 검색 UI
st.subheader("🔍 장소 검색")
with st.form(key="search_form"):
    search_query = st.text_input("검색할 장소를 입력하세요", placeholder="예: 카페, 음식점, 편의점")
    search_clicked = st.form_submit_button("검색", type="primary")

# 9. 검색 실행
if search_clicked and search_query:
    user_lat = st.session_state.user_location["lat"] if st.session_state.user_location else None
    user_lng = st.session_state.user_location["lng"] if st.session_state.user_location else None

    results = search_places(search_query, user_lat, user_lng)
    if results:
        st.session_state.search_results = results
        st.session_state.last_query = search_query
        st.success(f"🎯 '{search_query}' 검색 결과: {len(results)}개 (거리순 정렬)")
    else:
        st.warning("검색 결과가 없습니다.")

# 10. 지도 생성
def create_map():
    # 지도 중심 결정
    if st.session_state.user_location:
        center = [st.session_state.user_location["lat"], st.session_state.user_location["lng"]]
        zoom = 14
    elif st.session_state.search_results:
        center = [st.session_state.search_results[0]["lat"], st.session_state.search_results[0]["lng"]]
        zoom = 14
    else:
        center = [37.5665, 126.9780]
        zoom = 12

    m = folium.Map(location=center, zoom_start=zoom, tiles="OpenStreetMap")

    # 현재 위치 마커 (파란색)
    if st.session_state.user_location:
        folium.Marker(
            location=[st.session_state.user_location["lat"], st.session_state.user_location["lng"]],
            popup="📍 내 위치",
            tooltip="내 위치",
            icon=folium.Icon(color="blue", icon="user", prefix="fa")
        ).add_to(m)

    # 검색 결과 마커
    if st.session_state.search_results:
        for idx, place in enumerate(st.session_state.search_results, 1):
            distance_text = f"<br>📏 {place['distance']:.2f}km" if place.get('distance') else ""
            popup_html = f"""
            <div style="width:200px;">
                <b>{idx}. {place['title']}</b><br>
                <span style="color:#666;">📍 {place['address']}</span>
                {distance_text}
            </div>
            """

            folium.Marker(
                location=[place["lat"], place["lng"]],
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"{idx}. {place['title']}",
                icon=folium.Icon(color="red", icon="map-marker", prefix="fa")
            ).add_to(m)

    return m

# 11. 지도 렌더링
st.subheader("🗺️ 지도")
map_obj = create_map()
st_folium(map_obj, width=None, height=500, use_container_width=True)

# 12. 검색 결과 목록
if st.session_state.search_results:
    st.subheader(f"📋 '{st.session_state.last_query}' 검색 결과")

    for idx, place in enumerate(st.session_state.search_results, 1):
        col1, col2, col3 = st.columns([1, 6, 2])
        with col1:
            st.markdown(f"### {idx}")
        with col2:
            st.markdown(f"**{place['title']}**")
            st.caption(f"📍 {place['address']}")
            if place['category']:
                st.caption(f"🏷️ {place['category']}")
        with col3:
            if place.get('distance'):
                st.metric("거리", f"{place['distance']:.2f} km")
        st.divider()

# 13. 안내
with st.expander("📖 사용 방법"):
    st.markdown("""
    1. **위치 버튼 클릭** → 현재 위치 허용
    2. **검색어 입력** → 검색 버튼 클릭
    3. 결과가 **가까운 순**으로 정렬됩니다
    """)

st.caption("© 2026 - Naver Search API + OpenStreetMap")
