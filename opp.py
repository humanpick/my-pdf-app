import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO
import streamlit.components.v1 as components
from pypdf import PdfReader, PdfWriter

# [1. 설정] 무조건 맨 첫 줄에 위치해야 합니다.
st.set_page_config(
    page_title="HumanPick PDF 앱 - 엑셀 변환 및 암호해제",
    page_icon="📄",
    layout="wide"
)

# [2. 보안/인증 설정] 구글 검색 콘솔 인증용 (HTML 오류 수정 완료)
# 나중에 st.secrets["google_verification"]으로 관리하면 더 안전합니다.
google_code = "BROeHYj6XbgJPuAr4edlJvKQ_m9Ld0ZL0RYuZq_laDg"
verification_tag = f'<meta name="google-site-verification" content="{google_code}" />'
components.html(verification_tag, height=0)

# --- 🎨 CSS 스타일 적용 (가독성을 위해 상단 배치) ---
CSS_STYLE = """
<style>
    .block-container { padding-top: 1.5rem !important; padding-bottom: 1rem !important; }
    header { visibility: hidden !important; }
    body { color: #333333 !important; }
    .main-title { font-family: 'Noto Sans KR', sans-serif; color: #333333; font-size: 2.2rem; font-weight: 700; margin: 5px 0; }
    .main-subtitle { color: #666666; font-size: 1rem; margin-bottom: 15px; }
    .step-title { color: #333333; font-size: 1.15rem; font-weight: 600; margin: 15px 0 5px 0; }
    .stButton button { background-color: #00a8cc !important; color: white !important; border-radius: 8px; font-weight: 600; }
</style>
"""
st.markdown(CSS_STYLE, unsafe_allow_html=True)

# [3. 세션 상태 초기화]
for key in ["dl_pdf", "dl_excel", "process_done"]:
    if key not in st.session_state:
        st.session_state[key] = None if key != "process_done" else False

# [4. 레이아웃 구성]
spacer_left, left_col, main_col, right_col, spacer_right = st.columns([1.5, 1.2, 5.5, 1.2, 1.5])

# --- 왼쪽 쿠팡 배너 ---
with left_col:
    st.markdown("""
        <div style="text-align: center; position: sticky; top: 20px;">
            <iframe src="https://ads-partners.coupang.com/widgets.html?id=973247&template=carousel&trackingCode=AF8747713&width=160&height=600" width="160" height="600" frameborder="0" scrolling="no"></iframe>
        </div>
    """, unsafe_allow_html=True)

# --- 중앙 메인 기능 ---
with main_col:
    # 상단 롤링 배너
    banner_html = """
    <div style="border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
        <a href="http://pf.kakao.com/_SnxiZX" target="_blank">
            <img src="https://i.imgur.com/4d11BuP.jpeg" style="width:100%;">
        </a>
    </div>
    """
    st.components.v1.html(banner_html, height=220)

    st.markdown('<div class="main-title">📄 PDF 표 데이터 → 엑셀 변환기</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">비밀번호가 걸린 문서도 OK! 평생 완전 무료로 이용하세요.</div>', unsafe_allow_html=True)

    st.markdown('<div class="step-title">1. PDF 파일을 올려주세요</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type="pdf")

    st.markdown('<div class="step-title">2. 비밀번호 입력 (필요한 경우만)</div>', unsafe_allow_html=True)
    pdf_password = st.text_input("", type="password", placeholder="비밀번호가 없다면 비워두세요")

    if uploaded_file is not None:
        base_name = uploaded_file.name.rsplit('.', 1)[0]
        
        st.markdown('<div class="step-title">3. 작업을 선택하세요</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 1, 1.3])
        btn_pdf = c1.button("1. 암호 제거")
        btn_excel = c2.button("2. 엑셀 변환")
        btn_both = c3.button("3. 암호제거 + 엑셀변환")

        if btn_pdf or btn_excel or btn_both:
            with st.spinner('처리 중...'):
                try:
                    # PDF 처리 로직 (암호 해제)
                    if btn_pdf or btn_both:
                        uploaded_file.seek(0)
                        reader = PdfReader(uploaded_file)
                        if reader.is_encrypted:
                            if pdf_password: reader.decrypt(pdf_password)
                            else: st.error("암호를 입력해주세요!"); st.stop()
                        
                        writer = PdfWriter()
                        for page in reader.pages: writer.add_page(page)
                        pdf_out = BytesIO()
                        writer.write(pdf_out)
                        st.session_state.dl_pdf = pdf_out.getvalue()

                    # 엑셀 변환 로직
                    if btn_excel or btn_both:
                        uploaded_file.seek(0)
                        all_data = []
                        with pdfplumber.open(uploaded_file, password=pdf_password if pdf_password else None) as pdf:
                            for page in pdf.pages:
                                table = page.extract_table()
                                if table:
                                    for row in table:
                                        all_data.append([c.replace('\n', ' ') if isinstance(c, str) else c for c in row])

                        if all_data:
                            df = pd.DataFrame(all_data[1:], columns=all_data[0])
                            excel_out = BytesIO()
                            with pd.ExcelWriter(excel_out, engine='openpyxl') as ex:
                                df.to_excel(ex, index=False)
                            st.session_state.dl_excel = excel_out.getvalue()
                    
                    st.session_state.process_done = True
                except Exception as e:
                    st.error("오류가 발생했습니다. 비밀번호를 확인해주세요.")

        if st.session_state.process_done:
            st.success("✅ 완료되었습니다!")
            col_dl1, col_dl2 = st.columns(2)
            if st.session_state.dl_pdf:
                col_dl1.download_button("📥 암호제거 PDF 다운로드", st.session_state.dl_pdf, f"{base_name}_unlocked.pdf")
            if st.session_state.dl_excel:
                col_dl2.download_button("📥 엑셀 파일 다운로드", st.session_state.dl_excel, f"{base_name}.xlsx")

    # 하단 설문 배너
    st.markdown('<hr><div style="text-align: center;"><a href="https://forms.gle/YSwS7anZucY1Lv6bA" target="_blank"><img src="https://i.imgur.com/f4MCwFD.jpeg" style="max-width: 100%; border-radius: 12px;"></a></div>', unsafe_allow_html=True)

# --- 오른쪽 쿠팡 배너 ---
with right_col:
    st.markdown("""
        <div style="text-align: center; position: sticky; top: 20px;">
            <iframe src="https://ads-partners.coupang.com/widgets.html?id=973247&template=carousel&trackingCode=AF8747713&width=160&height=600" width="160" height="600" frameborder="0" scrolling="no"></iframe>
        </div>
    """, unsafe_allow_html=True)
