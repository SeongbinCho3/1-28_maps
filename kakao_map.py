import streamlit as st
import os
from dotenv import load_dotenv
import streamlit.components.v1 as components

# .env 파일 로드
load_dotenv()
KAKAO_API_KEY = os.getenv("KAKAO_MAP_API_KEY")

st.set_page_config(page_title="카카오 맵 현재 위치", layout="wide")
st.title("📍 카카오 맵 현재 위치 서비스")

# f-string 내부의 JavaScript 중괄호를 {{ }}로 이중 처리했습니다.
kakao_map_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>카카오 맵 현재 위치</title>
    <script type="text/javascript" src="https://dapi.kakao.com/v2/maps/sdk.js?appkey={KAKAO_API_KEY}"></script>
    <style>
        #map {{ width: 100%; height: 500px; border-radius: 10px; }}
    </style>
</head>
<body>
    <div id="map"></div>
    <script>
        var mapContainer = document.getElementById('map'),
            mapOption = {{ 
                center: new kakao.maps.LatLng(37.5665, 126.9780), 
                level: 3 
            }}; 

        var map = new kakao.maps.Map(mapContainer, mapOption); 

        if (navigator.geolocation) {{
            navigator.geolocation.getCurrentPosition(function(position) {{
                var lat = position.coords.latitude,
                    lon = position.coords.longitude; 
                
                var locPosition = new kakao.maps.LatLng(lat, lon);
                displayMarker(locPosition);
            }});
        }}

        function displayMarker(locPosition) {{
            // JS 객체 표기법이므로 중괄호를 두 번 써서 파이썬 탈출 처리
            var marker = new kakao.maps.Marker({{
                map: map, 
                position: locPosition
            }}); 
            map.setCenter(locPosition);      
        }}
    </script>
</body>
</html>
"""

components.html(kakao_map_html, height=550)