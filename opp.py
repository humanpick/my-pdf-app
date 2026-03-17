import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO

# 웹페이지 기본 설정
st.set_page_config(page_title="PDF to Excel 변환기", page_icon="📄")

st.title("📄 PDF 표 데이터 → 엑셀 변환기")
st.write("병원 진료 내역이나 규격화된 표가 있는 PDF 파일을 업로드하시면, 엑셀 파일로 깔끔하게 변환해 드립니다.")

# 파일 업로드 창 만들기
uploaded_file = st.file_uploader("여기에 PDF 파일을 올려주세요", type="pdf")

if uploaded_file is not None:
    with st.spinner('파일을 분석하고 엑셀로 변환하는 중입니다...'):
        all_data = []
        
        # 업로드된 PDF 파일 읽기
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    # 줄바꿈(\n) 기호 없애기 및 데이터 정리
                    cleaned_table = []
                    for row in table:
                        cleaned_row = [
                            cell.replace('\n', ' ').strip() if isinstance(cell, str) else cell 
                            for cell in row
                        ]
                        cleaned_table.append(cleaned_row)
                    all_data.extend(cleaned_table)

        if all_data:
            # 첫 번째 줄을 헤더(열 이름)로 사용하고, 중복되는 헤더는 제거
            columns = all_data[0]
            data = [row for row in all_data[1:] if row != columns]
            
            df = pd.DataFrame(data, columns=columns)
            
            # 엑셀 파일로 변환하기 위해 메모리(BytesIO)에 임시 저장
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='추출데이터')
            
            excel_data = output.getvalue()
            
            st.success("✅ 변환이 완료되었습니다! 아래 버튼을 눌러 다운로드하세요.")
            
            # 엑셀 다운로드 버튼 만들기
            st.download_button(
                label="📥 엑셀 파일 다운로드",
                data=excel_data,
                file_name="PDF_변환결과.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("PDF에서 표 데이터를 찾을 수 없습니다. 문서 형태를 다시 확인해 주세요.")
