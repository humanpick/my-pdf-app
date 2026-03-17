import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO
import streamlit.components.v1 as components
from pypdf import PdfReader, PdfWriter  # 암호를 풀고 PDF로 다시 저장하기 위한 도구

# 1. 화면 설정
st.set_page_config(page_title="PDF & Excel 자동 변환기", page_icon="📄", layout="wide")

# (다운로드 버튼이 사라지지 않도록 상태를 저장하는 공간)
if "dl_pdf" not in st.session_state:
    st.session_state.dl_pdf = None
if "dl_excel" not in st.session_state:
    st.session_state.dl_excel = None
if "process_done" not in st.session_state:
    st.session_state.process_done = False

# 2. 화면을 5개의 구역으로 나눕니다.
spacer_left, left_col, main_col, right_col, spacer_right = st.columns([1.5, 1.2, 5.5, 1.2, 1.5])

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
    components.html(banner_html, height=220)

    st.title("📄 PDF 표 데이터 → 엑셀 변환기")
    st.write("비밀번호가 걸린 문서도 OK! 원하시는 작업을 선택해 주세요.")

    # 파일 업로드 창
    uploaded_file = st.file_uploader("1. PDF 파일을 올려주세요", type="pdf")

    # 비밀번호 입력 창
    pdf_password = st.text_input("2. 비밀번호 입력 (암호가 없는 파일은 비워두세요)", type="password")

    if uploaded_file is not None:
        # 파일 이름에서 원본 이름 추출 및 넘버링(_1) 추가
        base_name = uploaded_file.name.rsplit('.', 1)[0]
        pdf_filename = f"{base_name}_1.pdf"
        excel_filename = f"{base_name}_1.xlsx"

        # 3. 세 가지 액션 버튼 가로로 배치하기
        st.write("**3. 원하시는 작업을 선택하세요:**")
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        btn_pdf = col_btn1.button("🔓 암호 풀기 (PDF)")
        btn_excel = col_btn2.button("📊 엑셀 변환 (Excel)")
        btn_both = col_btn3.button("✨ 둘 다 실행하기")

        # 버튼 중 하나라도 클릭되었을 때 실행
        if btn_pdf or btn_excel or btn_both:
            st.session_state.dl_pdf = None
            st.session_state.dl_excel = None
            st.session_state.process_done = False
            
            with st.spinner('선택하신 작업을 진행하는 중입니다...'):
                try:
                    # (1) 암호 해제 기능 (PDF로 저장)
                    if btn_pdf or btn_both:
                        uploaded_file.seek(0) # 파일을 처음부터 읽도록 초기화
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

                    # (2) 엑셀 변환 기능
                    if btn_excel or btn_both:
                        uploaded_file.seek(0) # 파일을 처음부터 읽도록 초기화
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

        # 작업 완료 후 다운로드 버튼 표시 구역
        if st.session_state.process_done:
            st.success("✅ 작업이 완료되었습니다! 아래 버튼을 눌러 결과물을 다운로드하세요.")
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
        <hr style="margin-top: 50px; margin-bottom: 30px; border-top: 1px solid #ddd;">
        <div style="text-align: center; margin-bottom: 20px;">
            <a href="https://forms.gle/YSwS7anZucY1Lv6bA" target="_blank">
                <img src="https://i.imgur.com/f4MCwFD.jpeg" style="max-width: 100%; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
            </a>
        </div>
    """, unsafe_allow_html=True)

# --- [오른쪽 구역] 쿠팡 배너 ---
with right_col:
    st.markdown("""
        <div style="text-align: center; position: sticky; top: 50px;">
            <a href="여기에_쿠팡_링크" target="_blank">
                <img src="https://via.placeholder.com/160x600?text=Coupang+Right" style="max-width: 100%;">
            </a>
        </div>
    """, unsafe_allow_html=True)
