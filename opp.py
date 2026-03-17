import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO
import streamlit.components.v1 as components

# 1. 화면을 전체 너비로 넓게 쓰기 위해 layout="wide"를 추가합니다.
st.set_page_config(page_title="PDF to Excel 변환기", page_icon="📄", layout="wide")

# 2. 화면을 3개의 구역으로 나눕니다. (왼쪽 배너, 중앙 메인 화면, 오른쪽 배너)
left_col, main_col, right_col = st.columns([1.5, 7, 1.5])

# --- [왼쪽 구역] 쿠팡 배너 ---
with left_col:
    st.markdown("""
        <div style="text-align: center; position: sticky; top: 50px;">
            <a href="여기에_쿠팡_링크" target="_blank">
                <img src="https://via.placeholder.com/160x600?text=Coupang+Left" style="max-width: 100%;">
            </a>
        </div>
    """, unsafe_allow_html=True)


# --- [중앙 구역] 메인 변환기 및 롤링 배너 ---
with main_col:
    # --- 자동으로 넘어가는 상단 롤링 배너 시작 ---
    banner_html = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
      * { box-sizing: border-box; margin: 0; padding: 0; }
      .slideshow-container { 
        max-width: 100%; 
        position: relative; 
        margin: auto; 
        border-radius: 12px; 
        overflow: hidden; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
      }
      .mySlides { display: none; }
      img { width: 100%; vertical-align: middle; border-radius: 12px; }
      
      /* 페이드 애니메이션 */
      .fade {
        animation-name: fade;
        animation-duration: 1
