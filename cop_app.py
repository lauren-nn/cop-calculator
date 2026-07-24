import streamlit as st

# --- 1. 기본 화면 및 상태 설정 ---
st.set_page_config(page_title="전문가용 COP 계산기", layout="wide")

st.title("❄️ 이원 냉동 사이클 통합 계산 프로그램")
st.markdown("현장 실무용 대시보드입니다. 탭을 이동하여 도면을 확인하거나 계산을 수행하세요.")
st.divider()

# --- 2. 자동 계산 로직 ---
def solve_stage(qe_str, w_str, qc_str, cop_str):
    def to_float(v):
        try: return float(v)
        except: return None
    
    qe, w, qc, cop = to_float(qe_str), to_float(w_str), to_float(qc_str), to_float(cop_str)
    
    for _ in range(3):
        if qe is not None and w is not None:
            if qc is None: qc = qe + w
            if cop is None and w != 0: cop = qe / w
        if qc is not None and w is not None:
            if qe is None: qe = qc - w
        if qe is not None and qc is not None:
            if w is None: w = qc - qe
        if cop is not None and w is not None:
            if qe is None: qe = cop * w
        if qe is not None and cop is not None and cop != 0:
            if w is None: w = qe / cop
        if qc is not None and cop is not None and cop != -1:
            if w is None: w = qc / (cop + 1)
            if qe is None: qe = qc - w
            
    return qe, w, qc, cop

def format_val(val, is_cop=False):
    if val is None: return "-"
    return f"{val:.4f}" if is_cop else f"{val:.2f}"

# --- 3. UI 렌더링 함수 (엑셀 표 스타일) ---
def render_grid_header():
    h1, h2, h3, h4, h5 = st.columns([2, 1, 1, 2, 2])
    h1.markdown("**매개변수**")
    h2.markdown("**기호**")
    h3.markdown("**단위**")
    h4.markdown("**알려진 값 (입력)**")
    h5.markdown("**계산된 값 (결과)**")
    st.markdown("<hr style='margin: 5px 0 15px 0;'>", unsafe_allow_html=True)

def render_grid_row(name, symbol, unit, key, result_val, is_cop=False):
    c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 2, 2])
    c1.markdown(f"<div style='padding-top:10px;'>{name}</div>", unsafe_allow_html=True)
    c2.markdown(f"<div style='padding-top:10px;'>{symbol}</div>", unsafe_allow_html=True)
    c3.markdown(f"<div style='padding-top:10px;'>{unit}</div>", unsafe_allow_html=True)
    
    # 텍스트 입력창 (라벨 숨김 처리로 표 형태 유지)
    with c4:
        input_val = st.text_input("입력", key=key, label_visibility="collapsed")
        
    # 결과값 출력 (강조 색상 적용)
    color = "#0066cc" if "H" in symbol else "#cc0000"
    res_str = format_val(result_val, is_cop)
    c5.markdown(f"<div style='padding-top:10px; color:{color}; font-weight:bold;'>{res_str}</div>", unsafe_allow_html=True)
    
    return input_val

# --- 4. 탭(Tab) 기반 화면 구성 ---
tab1, tab2 = st.tabs(["📊 COP & 열량 계산기", "📐 시스템 계통도 및 공식"])

with tab1:
    st.subheader("데이터 입력 및 결과 확인")
    st.caption("표의 '알려진 값' 열에 최소 2개의 데이터를 입력하면, 우측 '계산된 값' 열에 결과가 즉시 표시됩니다.")
    st.text("") # 여백
    
    # ====== 고단 사이클 (High Stage) ======
    st.markdown("#### 🔼 고단 사이클 (High Stage)")
    render_grid_header()
    
    # 1차적으로 입력창만 먼저 그리고, 이전 입력값을 가져와서 계산
    qe_h_in = st.session_state.get('qe_h', '')
    w_h_in = st.session_state.get('w_h', '')
    qc_h_in = st.session_state.get('qc_h', '')
    cop_h_in = st.session_state.get('cop_h', '')
    
    qe_h, w_h, qc_h, cop_h = solve_stage(qe_h_in, w_h_in, qc_h_in, cop_h_in)
    
    # 계산된 결과를 바탕으로 다시 표 렌더링
    render_grid_row("증발열량", "$q_{eH}$", "kW", "qe_h", qe_h)
    render_grid_row("압축기 일량", "$w_H$", "kW", "w_h", w_h)
    render_grid_row("응축열량", "$q_{cH}$", "kW", "qc_h", qc_h)
    render_grid_row("성적계수", "$COP_H$", "-", "cop_h", cop_h, True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # ====== 저단 사이클 (Low Stage) ======
    st.markdown("#### 🔽 저단 사이클 (Low Stage)")
    render_grid_header()
    
    qe_l_in = st.session_state.get('qe_l', '')
    w_l_in = st.session_state.get('w_l', '')
    qc_l_in = st.session_state.get('qc_l', '')
    cop_l_in = st.session_state.get('cop_l', '')
    
    qe_l, w_l, qc_l, cop_l = solve_stage(qe_l_in, w_l_in, qc_l_in, cop_l_in)
    
    render_grid_row("증발열량", "$q_{eL}$", "kW", "qe_l", qe_l)
    render_grid_row("압축기 일량", "$w_L$", "kW", "w_l", w_l)
    render_grid_row("응축열량", "$q_{cL}$", "kW", "qc_l", qc_l)
    render_grid_row("성적계수", "$COP_L$", "-", "cop_l", cop_l, True)

with tab2:
    col_img, col_desc = st.columns([1, 1])
    
    with col_img:
        st.subheader("이원 냉동 사이클 P&ID")
        # 실제 도면 이미지 파일명으로 변경하여 사용하세요 (예: "diagram.png")
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Cascade_refrigeration_system.svg/600px-Cascade_refrigeration_system.svg.png", use_container_width=True)
        
    with col_desc:
        st.subheader("표준 계산 공식")
        st.info("이 프로그램은 아래의 열역학 표준 공식을 기반으로 역산 로직을 수행합니다.")
        
        st.markdown("**고단 사이클 (High Stage)**")
        st.latex(r"q_{cH} = q_{eH} + w_H")
        st.latex(r"COP_H = \frac{q_{eH}}{w_H}")
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        st.markdown("**저단 사이클 (Low Stage)**")
        st.latex(r"q_{cL} = q_{eL} + w_L")
        st.latex(r"COP_L = \frac{q_{eL}}{w_L}")
