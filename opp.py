import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO
import streamlit.components.v1 as components
from pypdf import PdfReader, PdfWriter

# 1. 화면 설정
st.set_page_config(page_title="PDF & Excel 자동 변환기", page_icon="📄", layout="wide")

# --- 🎨 여백 제거 및 트렌디 컬러 CSS 스타일 적용 시작 ---
CSS_STYLE = """
<style>
    /* 0. 스트림릿 기본 상단/하단 쓸데없는 여백 완벽 제거! */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1rem !important;
        margin-top: 0 !important;
    }
    header {
        visibility: hidden !important; 
    }

    /* 1. 전체적인 텍스트 컬러 조절 */
    body {
        color: #333333 !important;
    }

    /* 2. 타이틀 및 글씨 스타일 정의 */
    .main-title {
        font-family: 'Noto Sans KR', sans-serif;
        color: #333333 !important;
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        margin-bottom: 5px !important;
        margin-top: 5px !important;
    }
    .main-subtitle {
        color: #666666 !important;
        font-size: 1rem !important;
        margin-bottom: 15px !important;
    }
    .step-title {
        color: #333333 !important;
        font-size: 1.15rem !important;
        font-weight: 600 !important;
        margin-top: 15px !important;
        margin-bottom: 5px !important;
    }

    /* 3. 입력창 및 파일 업로더 스타일 */
    .stTextInput input {
        border-color: #e0e0e0 !important;
        color: #333333 !important;
    }
    .stTextInput input:focus {
        border-color: #00a8cc !important;
        box-shadow: 0 0 0 0.2rem rgba(0, 168, 204, 0.25) !important;
    }
    .stFileUploader section div div {
        color: #333333 !important;
    }
    .stFileUploader button {
        background-color: #00a8cc !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: background-color 0.3s ease !important;
    }
    .stFileUploader button:hover {
        background-color: #008bb2 !important;
        color: white !important;
    }

    /* 4. 세 가지 메인 버튼 스타일 */
    .stButton button {
        background-color: #00a8cc !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 8px 16px !important;
        font-size: 0.95rem !important;
        transition: background-color 0.3s ease, box-shadow 0.3s ease !important;
    }
    .stButton button:hover {
        background-color: #008bb2 !important;
        color: white !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15) !important;
    }

    /* 5. 다운로드 버튼 스타일 */
    .stDownloadButton button {
        background-color: white !important;
        color: #00a8cc !important;
        border: 2px solid #00a8cc !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 8px 16px !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
    }
    .stDownloadButton button:hover {
        background-color: #00a8cc !important;
        color: white !important;
    }
</style>
"""
st.markdown(CSS_STYLE, unsafe_allow_html=True)
# --- 🎨 CSS 스타일 적용 끝 ---

# (다운로드 버튼 상태 저장)
if "dl_pdf" not in st.session_state:
    st.session_state.dl_pdf = None
if "dl_excel" not in st.session_state:
    st.session_state.dl_excel = None
if "process_done" not in st.session_state:
    st.session_state.process_done = False

# 2. 화면 분할
spacer_left, left_col, main_col, right_col, spacer_right = st.columns([1.5, 1.2, 5.5, 1.2, 1.5])

# --- [왼쪽 구역] 쿠팡 배너 (대표님 코드 적용 완료!) ---
with left_col:
    st.markdown("""
        <div style="text-align: center; position: sticky; top: 20px;">
            <iframe src="https://ads-partners.coupang.com/widgets.html?id=973247&template=carousel&trackingCode=AF8747713&subId=&width=160&height=600&tsource=" width="160" height="600" frameborder="0" scrolling="no" referrerpolicy="unsafe-url" browsingtopics></iframe>
        </div>
    """, unsafe_allow_html=True)


# --- [중앙 구역] 메인 변환기 및 롤링 배너 ---
with main_col:
    # --- 상단 롤링 배너 ---
    banner_html = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
      * { box-sizing: border-box; margin: 0; padding: 0; }
      .slideshow-container { max-width: 100%; position: relative; margin: auto; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
      .mySlides { display: none; }
      img { width: 100%; vertical-align: middle; border-radius: 12px; }
      .fade { animation-name: fade; animation-duration: 1.5s; }
      @keyframes fade { from {opacity: .4} to {opacity: 1} }
    </style>
    </head>
    <body>
    <div class="slideshow-container">
      <div class="mySlides fade">
        <a href="http://pf.kakao.com/_SnxiZX" target="_blank">
          <img src="https://i.imgur.com/4d11BuP.jpeg">
        </a>
      </div>
      <div class="mySlides fade">
        <a href="http://pf.kakao.com/_SnxiZX" target="_blank">
          <img src="https://i.imgur.com/qRv31wk.jpg">
        </a>
      </div>
      <div class="mySlides fade">
        <a href="http://pf.kakao.com/_SnxiZX" target="_blank">
          <img src="https://i.imgur.com/RWF8LwB.jpg">
        </a>
      </div>
    </div>
    <script>
    let slideIndex = 0;
    showSlides();
    function showSlides() {
      let i;
      let slides = document.getElementsByClassName("mySlides");
      for (i = 0; i < slides.length; i++) { slides[i].style.display = "none"; }
      slideIndex++;
      if (slideIndex > slides.length) {slideIndex = 1}    
      slides[slideIndex-1].style.display = "block";  
      setTimeout(showSlides, 3500);
    }
    </script>
    </body>
    </html>
    """
    components.html(banner_html, height=210) #상단 중앙 배너 사이즈 입니다.

    st.markdown('<div class="main-title">📄 PDF 표 데이터 → 엑셀 변환기</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">비밀번호가 걸린 문서도 OK! 원하시는 작업을 선택해 주세요.</div>', unsafe_allow_html=True)

    st.markdown('<div class="step-title">1. PDF 파일을 올려주세요</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type="pdf")

    st.markdown('<div class="step-title">2. 비밀번호 입력 (암호가 없는 파일은 비워두세요)</div>', unsafe_allow_html=True)
    pdf_password = st.text_input("", type="password")

    if uploaded_file is not None:
        base_name = uploaded_file.name.rsplit('.', 1)[0]
        pdf_filename = f"{base_name}_1.pdf"
        excel_filename = f"{base_name}_1.xlsx"

        st.markdown('<div class="step-title">3. 원하시는 작업을 선택하세요:</div>', unsafe_allow_html=True)
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1.3])
        btn_pdf = col_btn1.button("1. PDF파일 암호제거")
        btn_excel = col_btn2.button("2. PDF파일 엑셀로 변환")
        btn_both = col_btn3.button("3. PDF파일 암호제거 와 엑셀로 변환")

        if btn_pdf or btn_excel or btn_both:
            st.session_state.dl_pdf = None
            st.session_state.dl_excel = None
            st.session_state.process_done = False
            
            with st.spinner('선택하신 작업을 진행하는 중입니다...'):
                try:
                    if btn_pdf or btn_both:
                        uploaded_file.seek(0)
                        reader = PdfReader(uploaded_file)
                        if reader.is_encrypted:
                            if pdf_password:
                                reader.decrypt(pdf_password)
                            else:
                                st.error("❌ 이 문서는 암호가 걸려있습니다. 비밀번호를 입력해 주세요!")
                                st.stop()
                        writer = PdfWriter()
                        for page in reader.pages:
                            writer.add_page(page)
                        pdf_out = BytesIO()
                        writer.write(pdf_out)
                        st.session_state.dl_pdf = pdf_out.getvalue()

                    if btn_excel or btn_both:
                        uploaded_file.seek(0)
                        all_data = []
                        with pdfplumber.open(uploaded_file, password=pdf_password if pdf_password else None) as pdf:
                            for page in pdf.pages:
                                table = page.extract_table()
                                if table:
                                    cleaned_table = []
                                    for row in table:
                                        cleaned_row = [
                                            cell.replace('\n', ' ').strip() if isinstance(cell, str) else cell 
                                            for cell in row
                                        ]
                                        cleaned_table.append(cleaned_row)
                                    all_data.extend(cleaned_table)

                        if all_data:
                            columns = all_data[0]
                            data = [row for row in all_data[1:] if row != columns]
                            df = pd.DataFrame(data, columns=columns)
                            excel_out = BytesIO()
                            with pd.ExcelWriter(excel_out, engine='openpyxl') as excel_writer:
                                df.to_excel(excel_writer, index=False, sheet_name='추출데이터')
                            st.session_state.dl_excel = excel_out.getvalue()
                        else:
                            st.warning("문서 안에서 '표(Table)' 형태의 데이터를 찾을 수 없습니다.")
                    
                    st.session_state.process_done = True

                except Exception as e:
                    st.error("❌ 비밀번호가 틀렸거나 오류가 발생했습니다. 다시 확인해 주세요!")

        if st.session_state.process_done:
            st.success("✅ 작업 완료! 아래 버튼을 눌러주세요.")
            col_dl1, col_dl2 = st.columns(2)
            if st.session_state.dl_pdf:
                col_dl1.download_button(
                    label=f"📥 {pdf_filename} 다운로드",
                    data=st.session_state.dl_pdf,
                    file_name=pdf_filename,
                    mime="application/pdf"
                )
            if st.session_state.dl_excel:
                col_dl2.download_button(
                    label=f"📥 {excel_filename} 다운로드",
                    data=st.session_state.dl_excel,
                    file_name=excel_filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    # --- [중앙 구역 하단] 구글 폼 링크 배너 ---
    st.markdown("""
        <hr style="margin-top: 15px; margin-bottom: 15px; border-top: 1px solid #ddd;">
        <div style="text-align: center; margin-bottom: 10px;">
            <a href="https://forms.gle/YSwS7anZucY1Lv6bA" target="_blank">
                <img src="https://i.imgur.com/f4MCwFD.jpeg" style="max-width: 100%; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
            </a>
        </div>
    """, unsafe_allow_html=True)

# --- [오른쪽 구역] 쿠팡 배너 (대표님 코드 적용 완료!) ---
with right_col:
    st.markdown("""
        <div style="text-align: center; position: sticky; top: 20px;">
            <iframe src="https://ads-partners.coupang.com/widgets.html?id=973247&template=carousel&trackingCode=AF8747713&subId=&width=160&height=600&tsource=" width="160" height="600" frameborder="0" scrolling="no" referrerpolicy="unsafe-url" browsingtopics></iframe>
        </div>
    """, unsafe_allow_html=True)
