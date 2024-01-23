import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px

# sido_list 정의 부분에서 unique()를 제거하고, 전역 변수로 선언
sido_list = ["서울특별시", "부산광역시", "대구광역시", "인천광역시", "광주광역시", "대전광역시", "울산광역시", "세종특별자치시", "경기도", "강원도", "충청북도", "충청남도", "전라북도", "전라남도", "경상북도", "경상남도", "제주특별자치도"]
disease_list = ["조현병","불면증",]  # 질병 목록 추가   
     
st.markdown(
    """
    <style>
        .st-emotion-cache-1n76uvr{
            display: flex;
            position: relative;
            width: 720px;
            height: 500px;
        }

        .st-emotion-cache-q8sbsg p {
            word-break: break-word;
            margin-bottom: 0px;
            font-size: 17px;
        }

        .st-emotion-cache-uf99v8 {
            display: flex;
            flex-direction: column;
            width: 100%;
            overflow: auto;
            -webkit-box-align: center;
            align-items: center;
        }

        .mapboxgl-canvas{tabindex="0" aria-label="Map" width="584" height="500" style="width: 584px; height: 310px; left: 0px; top: 0px;)



        .st-emotion-cache-e92f0b{
            display: flex;
            position: relative;
            width: 100%; 
            height: 600px; 
            left: 0px; 
            top: 0px;
        }
        .sidebar.title {
            .sidebar .sidebar-content {
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .sidebar.title {
            width: 100%;
            text-align: center;
        }
        # .st-emotion-cache-1cwzzh4{
        #     display: flex;
        #     position: relative;
        #     width: 700px; 
        #     height: 600px; 
        #     left: 0px; 
        #     top: 0px;
        # }

        .st-e1{
            background-color: rgb(6, 200, 247);
        }

    </style>
    """, 
    unsafe_allow_html=True)

def load_data(disease, sido, sigungu=None, eupmyeondong=None):
    # 시군구 및 읍면동이 선택되었다면 해당 데이터만 불러오기
    if sigungu and eupmyeondong:
        return pd.read_csv(f"{disease}/{sido}/{sigungu}_{eupmyeondong}.csv")
    elif sigungu:
        return pd.read_csv(f"{disease}/{sido}/{sigungu}.csv")
    else:
        return pd.read_csv(f"{disease}/{sido}.csv")

def load_geojson(geojson_file):
    return gpd.read_file(geojson_file)

def main():
    st.sidebar.title("질병 예측 마이크로맵")
    st.sidebar.subheader("(Disease Prediction Micromaps)")
    st.sidebar.subheader("ⓒ 2023 Eden AllLiVE HEALTHCARE R&D. All rights reserved.")
    st.sidebar.markdown("---")
    menu = ["서비스 개요"]
    
    choice = st.sidebar.selectbox("질병 선택", menu + disease_list)  # 질병 목록 추가
    st.sidebar.markdown("---")
    if choice in disease_list:  # 선택한 것이 질병 중 하나일 경우
        selected_disease = choice
        selected_sido = st.sidebar.selectbox("시 • 도 선택", sido_list)
        st.sidebar.markdown("---")
        DB = load_data(selected_disease, selected_sido)
        
        geojson_data = load_geojson(f"{selected_disease}/{selected_sido}.geojson")
        
        # GeoJSON 파일에서 좌표 범위 가져오기
        min_lon, min_lat, max_lon, max_lat = geojson_data.geometry.total_bounds

        # 선택된 시군구에 해당하는 데이터 필터링
        selected_sigungu_data = DB[DB['sido_nm_1'] == selected_sido]

        sigungu_list = selected_sigungu_data['sigungu__1'].unique()
        # 예측값에 따라 내림차순으로 정렬
        sigungu_list = sorted(sigungu_list, key=lambda x: selected_sigungu_data[selected_sigungu_data['sigungu__1'] == x]['Predicted'].max(), reverse=True)
        
        selected_sigungu = st.sidebar.multiselect("시 • 군 • 구 선택", sigungu_list)
        st.sidebar.markdown("---")
        # 선택된 시군구에 해당하는 모든 읍면동 가져오기
        selected_eupmyeondong_list = selected_sigungu_data[selected_sigungu_data['sigungu__1'].isin(selected_sigungu)]['adm_dr_nm'].unique()

        # 예측값에 따라 내림차순으로 정렬
        selected_eupmyeondong_list = sorted(selected_eupmyeondong_list, key=lambda x: selected_sigungu_data[selected_sigungu_data['adm_dr_nm'] == x]['Predicted'].max(), reverse=True)

        selected_eupmyeondong = st.sidebar.multiselect("읍 • 면 • 동 선택", selected_eupmyeondong_list)
        st.sidebar.markdown("---")
        # 시군구 및 읍면동 선택 상자 아래에 "지도 스타일" 선택 상자 추가
        selected_map_style = st.sidebar.radio("배경지도 선택", ["carto-positron", "open-street-map"], index=0)
        
        # 베이스맵 스타일 선택에 따라 mapbox_style을 설정
        base_map_style = "carto-positron" if selected_map_style == "carto-positron" else "open-street-map"
        st.sidebar.markdown("---")
        
        # 투명도 조절 사이드바
        opacity1 = st.sidebar.slider("시 • 도 투명도 조절", min_value=0.0, max_value=1.0, value=0.5, step=0.1)
        opacity2 = st.sidebar.slider("시 • 군 • 구 투명도 조절", min_value=0.0, max_value=1.0, value=0.5, step=0.1)
        opacity3 = st.sidebar.slider("읍 • 면 • 동 투명도 조절", min_value=0.0, max_value=1.0, value=0.5, step=0.1)
        
        # 선택된 지역 데이터로 필터링
        selected_data = selected_sigungu_data[(selected_sigungu_data['sigungu__1'].isin(selected_sigungu)) &
                                              (selected_sigungu_data['adm_dr_nm'].isin(selected_eupmyeondong))]

        with st.expander("데이터 보기"):
            selected_columns = ['sido_nm_1', 'sigungu__1', 'adm_dr_nm', 'Predicted', 'StdError']  # 보여주고 싶은 열 목록
            # 선택한 열만 추출하여 데이터프레임 생성
            selected_data_view = selected_data[selected_columns]

            # 선택한 열만 보여주기
            data_table_width = 1000  # 원하는 너비 값으로 조절
            st.dataframe(selected_data_view, width=data_table_width)
            
            
            # st.dataframe(selected_data)

        # 전체 지역의 예측값을 사용하여 범례 생성
        legend_data = DB['Predicted'].values

        with st.expander("지도 보기"):
                       
            # 전체 지도를 처음에 보여주기
            fig = px.choropleth_mapbox(DB,
                                        geojson=geojson_data.geometry,
                                        locations=DB.index,
                                        color='Predicted',
                                        mapbox_style=base_map_style,
                                        center={"lat": (min_lat + max_lat) / 2, "lon": (min_lon + max_lon) / 2},
                                        color_continuous_scale="Spectral_r",
                                        opacity=opacity1,  # 투명도 설정 적용
                                        labels={'color': 'Predicted'},
                                        hover_data={'sido_nm_1': True, 'sigungu__1': True, 'adm_dr_nm': True, 'Predicted': ':.4f'},
                                        zoom =9
                                                )
           
            # 전체 지도에 제목 추가 (선택한 도시 또는 시군구의 이름)
            fig.update_layout(title_text=f"■ {selected_sido}", height=600)

            # Mapbox의 center와 zoom 속성을 사용하여 전체 지도가 보이도록 조절
            fig.update_layout(mapbox=dict(center={"lat": (min_lat + max_lat) / 2, "lon": (min_lon + max_lon) / 2}
                                          ),
                           clickmode='event+select')  # 클릭 이벤트 활성화 )

            # 전체 레이아웃에 대한 autosize 설정
            fig.update_layout(autosize=True)
            
            # legend의 색상 투명도 조절
            fig.update_layout(legend=dict(bgcolor=f'rgba(255, 255, 255, {opacity1})'))
                    
            st.plotly_chart(fig)

            # 선택된 지역에 대한 각각의 choropleth map을 표시
            for selected_area in selected_sigungu:
                filtered_geojson = geojson_data[(geojson_data['sigungu__1'] == selected_area)]
                filtered_data = selected_sigungu_data[selected_sigungu_data['sigungu__1'] == selected_area]

                legend_min = selected_sigungu_data['Predicted'].min()
                legend_max = selected_sigungu_data['Predicted'].max()

                fig_filtered = px.choropleth_mapbox(filtered_data,
                                                    geojson=filtered_geojson.geometry,
                                                    locations=filtered_data.index,
                                                    color='Predicted',
                                                    mapbox_style=base_map_style,
                                                    center={"lat": (filtered_geojson.bounds.miny.min() + filtered_geojson.bounds.maxy.max()) / 2,
                                                            "lon": (filtered_geojson.bounds.minx.min() + filtered_geojson.bounds.maxx.max()) / 2},
                                                    color_continuous_scale="Spectral_r",
                                                    opacity=opacity2,  # 투명도 설정 적용
                                                    range_color=[legend_min, legend_max],
                                                    labels={'color': 'Predicted'},
                                                    hover_data={'sido_nm_1': True, 'sigungu__1': True, 'adm_dr_nm': True, 'Predicted': ':.4f'}
                                                    )

                # 선택된 지역의 이름을 제목으로 추가
                fig_filtered.update_layout(title_text=f"■ {selected_sido} 〉 {selected_area}", height=600)

                # Mapbox의 center와 zoom 속성을 사용하여 전체 지도가 보이도록 조절
                fig_filtered.update_layout(mapbox=dict(center={"lat": (filtered_geojson.bounds.miny.min() + filtered_geojson.bounds.maxy.max()) / 2,
                                                               "lon": (filtered_geojson.bounds.minx.min() + filtered_geojson.bounds.maxx.max()) / 2},
                                                       zoom=11))

                # 전체 레이아웃에 대한 autosize 설정
                fig_filtered.update_layout(autosize=True)
                
                 # legend의 색상 투명도 조절
                fig_filtered.update_layout(legend=dict(bgcolor=f'rgba(255, 255, 255, {opacity2})'))

                st.plotly_chart(fig_filtered)

            # 선택된 읍면동에 대한 choropleth map을 표시 (하나의 지도에 그림)
            if selected_eupmyeondong:
                # 선택된 시군구 모두를 나타내는 문자열 생성
                selected_areas_str = ", ".join(selected_sigungu)

                # 선택된 읍면동에 해당하는 데이터 필터링
                selected_eupmyeondong_data = selected_sigungu_data[selected_sigungu_data['adm_dr_nm'].isin(selected_eupmyeondong)]

                # 선택된 시군구에 속한 읍면동만 가져오도록 필터링
                selected_eupmyeondong_data = selected_eupmyeondong_data[selected_eupmyeondong_data['sigungu__1'].isin(selected_sigungu)]

                legend_min = selected_sigungu_data['Predicted'].min()
                legend_max = selected_sigungu_data['Predicted'].max()
                
                fig_filtered_eupmyeondong = px.choropleth_mapbox(selected_eupmyeondong_data,
                                                                geojson=geojson_data.geometry,
                                                                locations=selected_eupmyeondong_data.index,
                                                                color='Predicted',
                                                                mapbox_style=base_map_style,
                                                                center={"lat": (filtered_geojson.bounds.miny.min() + filtered_geojson.bounds.maxy.max()) / 2,
                                                                        "lon": (filtered_geojson.bounds.minx.min() + filtered_geojson.bounds.maxx.max()) / 2},
                                                                color_continuous_scale="Spectral_r",
                                                                opacity=opacity3,  # 투명도 설정 적용
                                                                # range_color=[legend_min, legend_max], #범례색을 삭제하면 동끼리 상대적 비교
                                                                labels={'color': 'Predicted'},
                                                                hover_data={'sido_nm_1': True, 'sigungu__1': True, 'adm_dr_nm': True, 'Predicted': ':.4f'}
                                                                )

                # 선택한 지역의 이름을 줄 바꿈 포함하여 표시
                # fig_filtered_eupmyeondong.update_layout(title_text=f"■ {selected_sido} 〉 {selected_areas_str} 〉 {', '.join(selected_eupmyeondong)}")
                title_text = f"■ {selected_sido} 〉 {selected_areas_str} 〉 {', '.join(selected_eupmyeondong)}"
                wrapped_title_text = "<br>".join(title_text[i:i+60] for i in range(0, len(title_text), 60))  # 적절한 길이로 나누기

                # 레이아웃 업데이트
                fig_filtered_eupmyeondong.update_layout(title_text=wrapped_title_text, height=600)
                
                # Mapbox의 center와 zoom 속성을 사용하여 전체 지도가 보이도록 조절
                fig_filtered_eupmyeondong.update_layout(mapbox=dict(center={"lat": (filtered_geojson.bounds.miny.min() + filtered_geojson.bounds.maxy.max()) / 2,
                                                                            "lon": (filtered_geojson.bounds.minx.min() + filtered_geojson.bounds.maxx.max()) / 2},
                                                       zoom=11))

                # 전체 레이아웃에 대한 autosize 설정
                fig_filtered_eupmyeondong.update_layout(autosize=True)
                
                # legend의 색상 투명도 조절
                fig_filtered_eupmyeondong.update_layout(legend=dict(bgcolor=f'rgba(255, 255, 255, {opacity3})'))

                st.plotly_chart(fig_filtered_eupmyeondong)

    elif choice == "Advanced":
        pass
    
    elif choice == "Attendees":
        pass
    
    else:
        st.header("질병지도의 목적")
        st.subheader("(주)올리브헬스케어 기업부설연구소에서 개발한 질병지도(disease map)는 국민건강보험공단의 지역별 의료이용통계연보와 건강보험심사평가원의 지역별 통계자료를 기반으로 시군구 자료를 읍면동 및 우편번호 단위의 미시적 공간자료(micro-spatial data)로 가공하여 질병의 발생률과 그 분포을 확인하기 위함이다.")
          

if __name__ == "__main__":
    main()