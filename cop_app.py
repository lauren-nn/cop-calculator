import streamlit as st

# --- 1. 기본 화면 설정 (넓은 화면 모드) ---
st.set_page_config(page_title="냉동 사이클 COP 계산기", layout="wide")

st.title("❄️ 이원 냉동 사이클 (Cascade) COP 계산기")
st.markdown("다이어그램을 참고하여 빈칸에 **알려진 값(어떤 조합이든 최소 2개)**을 입력하면 나머지가 자동 계산됩니다.")
st.divider()

# --- 2. 초보자를 위한 개념 설명 (접기/펴기 기능) ---
with st.expander("💡 COP와 이원 냉동 사이클이란? (초보자용 가이드 클릭!)"):
    st.markdown("""
    * **COP (Coefficient of Performance, 성적계수):** 냉동기가 얼마나 효율적으로 일하는지 나타내는 점수입니다. 
        * 쉽게 말해 **"내가 낸 전기세(압축기 일량) 대비 얼마나 시원해졌는가(증발열량)?"**를 의미합니다. (값이 클수록 고효율)
    * **이원 냉동 사이클 (Cascade Cycle):** 엄청나게 차가운 온도(초저온)를 만들기 위해, 냉동기 2개(고단/저단)를 직렬로 연결해 힘을 합치는 시스템입니다.
    * **주요 용어:**
        * $q_e$ (증발열량): 주변의 열을 빼앗아 시원하게 만드는 양 (우리가 얻고자 하는 목적)
        * $w$ (압축기 일량): 기계를 돌리기 위해 투입한 에너지 (전기에너지)
        * $q_c$ (응축열량): 밖으로 버려지는 뜨거운 열량
    """)

# --- 3. 완벽해진 자동 계산 로직 (모든 경우의 수 커버) ---
def solve_stage(qe_str, w_str, qc_str, cop_str):
    def to_float(v):
        try: return float(v)
        except: return None
    
    qe = to_float(qe_str)
    w = to_float(w_str)
    qc = to_float(qc_str)
    cop = to_float(cop_str)
    
    # 3번 반복 돌면서 빈칸을 모두 역산하여 채워 넣습니다.
    for _ in range(3):
        # 1. qe와 w를 알 때
        if qe is not None and w is not None:
            if qc is None: qc = qe + w
            if cop is None and w != 0: cop = qe / w
        # 2. qc와 w를 알 때
        if qc is not None and w is not None:
            if qe is None: qe = qc - w
        # 3. qe와 qc를 알 때
        if qe is not None and qc is not None:
            if w is None: w = qc - qe
        # 4. cop와 w를 알 때
        if cop is not None and w is not None:
            if qe is None: qe = cop * w
        # 5. qe와 cop를 알 때
        if qe is not None and cop is not None and cop != 0:
            if w is None: w = qe / cop
        # 6. qc와 cop를 알 때 (추가된 핵심 로직: W = Qc / (COP + 1) )
        if qc is not None and cop is not None and cop != -1:
            if w is None: w = qc / (cop + 1)
            if qe is None: qe = qc - w
            
    return qe, w, qc, cop

def format_val(val, is_cop=False):
    if val is None: return "-"
    return f"{val:.4f}" if is_cop else f"{val:.2f}"

def create_input_row(label, unit, key):
    col1, col2, col3 = st.columns([1.5, 1, 1])
    col1.markdown(f"**{label}** [{unit}]" if unit else f"**{label}**")
    val_in = col2.text_input("입력", key=key, label_visibility="collapsed")
    return val_in, col3

# --- 4. 메인 레이아웃 (좌측: 이미지, 우측: 계산기) ---
col_img, col_calc = st.columns([1, 1.2], gap="large")

with col_img:
    st.subheader("이원 냉동 사이클 모식도")
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Cascade_refrigeration_system.svg/600px-Cascade_refrigeration_system.svg.png", 
             caption="이원 냉동 사이클 구조도", use_container_width=True)
    st.info("💡 **팁:** 본인이 그린 도면이나 직접 찍은 사진(`edited-image.jpg` 등)을 코드 폴더에 넣고, 코드 내 `st.image('edited-image.jpg')`로 수정하면 나만의 프로그램이 됩니다!")

with col_calc:
    # --- 고단 사이클 (High Stage) ---
    st.subheader("🔼 고단 사이클 (High Stage)")
    
    st.latex(r"q_{cH} = q_{eH} + w_H \quad \vert \quad COP_H = \frac{q_{eH}}{w_H}")
    
    h_h1, h_h2, h_h3 = st.columns([1.5, 1, 1])
    h_h2.caption("알려진 값 (입력)")
    h_h3.caption("→ 계산된 결과")

    qe_h_in, res_qe_h = create_input_row("증발열량 ($q_{eH}$)", "kW", "qe_h")
    w_h_in, res_w_h = create_input_row("압축기 일량 ($w_H$)", "kW", "w_h")
    qc_h_in, res_qc_h = create_input_row("응축열량 ($q_{cH}$)", "kW", "qc_h")
    cop_h_in, res_cop_h = create_input_row("성적계수 ($COP_H$)", "", "cop_h")

    qe_h, w_h, qc_h, cop_h = solve_stage(qe_h_in, w_h_in, qc_h_in, cop_h_in)
    res_qe_h.markdown(f"<span style='color:#0066cc; font-weight:bold; font-size:18px;'>{format_val(qe_h)} kW</span>", unsafe_allow_html=True)
    res_w_h.markdown(f"<span style='color:#0066cc; font-weight:bold; font-size:18px;'>{format_val(w_h)} kW</span>", unsafe_allow_html=True)
    res_qc_h.markdown(f"<span style='color:#0066cc; font-weight:bold; font-size:18px;'>{format_val(qc_h)} kW</span>", unsafe_allow_html=True)
    res_cop_h.markdown(f"<span style='color:#0066cc; font-weight:bold; font-size:18px;'>{format_val(cop_h, True)}</span>", unsafe_allow_html=True)

    st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)

    # --- 저단 사이클 (Low Stage) ---
    st.subheader("🔽 저단 사이클 (Low Stage)")
    
    st.latex(r"q_{cL} = q_{eL} + w_L \quad \vert \quad COP_L = \frac{q_{eL}}{w_L}")
    
    l_h1, l_h2, l_h3 = st.columns([1.5, 1, 1])
    l_h2.caption("알려진 값 (입력)")
    l_h3.caption("→ 계산된 결과")

    qe_l_in, res_qe_l = create_input_row("증발열량 ($q_{eL}$)", "kW", "qe_l")
    w_l_in, res_w_l = create_input_row("압축기 일량 ($w_L$)", "kW", "w_l")
    qc_l_in, res_qc_l = create_input_row("응축열량 ($q_{cL}$)", "kW", "qc_l")
    cop_l_in, res_cop_l = create_input_row("성적계수 ($COP_L$)", "", "cop_l")

    qe_l, w_l, qc_l, cop_l = solve_stage(qe_l_in, w_l_in, qc_l_in, cop_l_in)
    res_qe_l.markdown(f"<span style='color:#cc0000; font-weight:bold; font-size:18px;'>{format_val(qe_l)} kW</span>", unsafe_allow_html=True)
    res_w_l.markdown(f"<span style='color:#cc0000; font-weight:bold; font-size:18px;'>{format_val(w_l)} kW</span>", unsafe_allow_html=True)
    res_qc_l.markdown(f"<span style='color:#cc0000; font-weight:bold; font-size:18px;'>{format_val(qc_l)} kW</span>", unsafe_allow_html=True)
    res_cop_l.markdown(f"<span style='color:#cc0000; font-weight:bold; font-size:18px;'>{format_val(cop_l, True)}</span>", unsafe_allow_html=True)