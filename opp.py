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
        animation-duration: 1.5s;
      }
      @keyframes fade {
        from {opacity: .4} 
        to {opacity: 1}
      }
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
      for (i = 0; i < slides.length; i++) {
        slides[i].style.display = "none";  
      }
      slideIndex++;
      if (slideIndex > slides.length) {slideIndex = 1}    
      slides[slideIndex-1].style.display = "block";  
      setTimeout(showSlides, 3500); // 3.5초마다 다음 배너로 전환
    }
    </script>

    </body>
    </html>
    """
    components.html(banner_html, height=220)
    # --- 상단 롤링 배너 끝 ---

    st.title("📄 PDF 표 데이터 → 엑셀 변환기")
    st.write("비밀번호가 걸린 문서도 OK! PDF 파일을 올리거나 마우스 드래그로 엑셀 깔끔하게 받아가세요.")

    # 파일 업로드 창
    uploaded_file = st.file_uploader("1. PDF 파일을 올려주세요", type="pdf")

    # 비밀번호 입력 창
    pdf_password = st.text_input("2. 비밀번호 입력 (암호가 없는 파일은 비워두세요)", type="password")

    if uploaded_file is not None:
        if st.button("🚀 변환 시작하기"):
            with st.spinner('파일의 암호를 풀고 데이터를 분석하는 중입니다...'):
                all_data = []
                try:
                    with pdfplumber.open(uploaded_file, password=pdf_password) as pdf:
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
                        
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            df.to_excel(writer, index=False, sheet_name='추출데이터')
                        excel_data = output.getvalue()
                        
                        st.success("✅ 변환이 완벽하게 끝났습니다! 아래 버튼을 눌러주세요.")
                        
                        st.download_button(
                            label="📥 엑셀 파일 다운로드",
                            data=excel_data,
                            file_name="PDF_자동변환결과.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    else:
                        st.warning("문서가 열리긴 했지만, 안에서 '표(Table)' 형태의 데이터를 찾을 수 없습니다.")

                except Exception as e:
                    st.error("❌ 비밀번호가 틀렸습니다. 다시 한번 확인해 주세요!")

    # --- [중앙 구역 하단] 단일 링크 배너 ---
    st.markdown("""
        <hr style="margin-top: 50px; margin-bottom: 30px; border-top: 1px solid #ddd;">
        <div style="text-align: center; margin-bottom: 20px;">
            <a href="여기에_하단_링크_주소_입력" target="_blank">
                <img src="https://via.placeholder.com/800x150?text=Bottom+Single+Banner" style="max-width: 100%; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
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
