import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO
import streamlit.components.v1 as components
from pypdf import PdfReader, PdfWriter

# 1. 화면 설정: 깨끗한 기본 화이트 테마를 위해layout="wide"를 사용하고, 아래에서 너비를 제어합니다.
st.set_page_config(page_title="PDF & Excel 자동 변환기", page_icon="📄", layout="wide")

# --- 🎨 현대적인 트렌디 컬러 CSS 스타일 적용 시작 ---
CSS_STYLE = """
<style>
    /* 1. 전체적인 텍스트 컬러 조절 */
    body {
        color: #333333 !important; /* 메인 텍스트 컬러: 진한 그레이 */
    }

    /* 2. 타이틀 및 글씨 스타일 정의 */
    .main-title {
        font-family: 'Noto Sans KR', sans-serif;
        color: #333333 !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 10px !important;
    }
    .main-subtitle {
        color: #666666 !important; /* 보조 텍스트 컬러: 중간 그레이 */
        font-size: 1.1rem !important;
        margin-bottom: 30px !important;
    }
    .step-title {
        color: #333333 !important;
        font-size: 1.25rem !important;
        font-weight: 600 !important;
        margin-top: 25px !important;
        margin-bottom: 8px !important;
    }

    /* 3. 입력창 및 파일 업로더 스타일 */
    .stTextInput input {
        border-color: #e0e0e0 !important;
        color: #333333 !important;
    }
    .stTextInput input:focus {
        border-color: #00a8cc !important; /* 포인트 컬러: 뮤트 Teal */
        box-shadow: 0 0 0 0.2rem rgba(0, 168, 204, 0.25) !important;
    }
    .stFileUploader section div div {
        color: #333333 !important;
    }
    .stFileUploader button {
        background-color: #00a8cc !important; /* 포인트 컬러 */
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: background-color 0.3s ease !important;
    }
    .stFileUploader button:hover {
        background-color: #008bb2 !important; /* 조금 더 진한 Teal */
        color: white !important;
    }

    /* 4. 세
