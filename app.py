import streamlit as st
import pandas as pd

# --- Настройка страницы ---
st.set_page_config(page_title="Калькулятор ТПА", page_icon="🏭", layout="wide")

# --- Константы ---
TPA_LIST = [f"ТПА {i}" for i in range(1, 14)] + ["Малыш"]
MATERIALS = ["ПВХ серый", "ПВХ коричневый", "АБС", "PP"]

# --- Инициализация состояния (Авто-сохранение в рамках сессии) ---
def init_state():
    if 'tpa_data' not in st.session_state:
        st.session_state.tpa_data = {
            tpa: {'material': MATERIALS[0], 'per_box': 0, 'boxes': 0, 'defect': 0, 'weight': 0.0}
            for tpa in TPA_LIST
        }
    if 'bg_style' not in st.session_state:
        st.session_state.bg_style = "Спокойный"

init_state()

# --- Пользовательский CSS для тем и обоев ---
bg_css = {
    "Спокойный": "linear-gradient(135deg, #f0f4f8 0%, #d9e2ec 100%)",
    "Яркий": "linear-gradient(120deg, #a1c4fd 0%, #c2e9fb 100%)",
    "Глубокий": "radial-gradient(circle at 10% 20%, rgb(239, 246, 255) 0%, rgb(219, 228, 255) 90%)"
}

# Для тёмной темы Streamlit сам инвертирует цвета, но мы зададим базу
st.markdown(f"""
    <style>
    .stApp {{
        background: {bg_css[st.session_state.bg_style]} !important;
    }}
    /* Улучшаем вид карточек на мобильных */
    .block-container {{
        padding-top: 1rem;
        padding-bottom: 1rem;
    }}
    div[data-testid="stExpander"] {{
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        background-color: rgba(255, 255, 255, 0.8);
    }}
    </style>
""", unsafe_allow_html=True)

# --- Боковая панель (Настройки) ---
with st.sidebar:    st.header("⚙️ Настройки")
    st.session_state.bg_style = st.selectbox("🎨 Стиль фона", ["Спокойный", "Яркий", "Глубокий"])
    st.markdown("---")
    st.markdown("💡 *Совет: переключите светлую/тёмную тему через меню ☰ в правом верхнем углу!*")
    
    if st.button("🗑️ Очистить все данные", type="primary"):
        for tpa in TPA_LIST:
            st.session_state.tpa_data[tpa] = {'material': MATERIALS[0], 'per_box': 0, 'boxes': 0, 'defect': 0, 'weight': 0.0}
        st.rerun()

# --- Вкладки ---
tab1, tab2 = st.tabs(["🧮 Калькулятор", "🔧 Для наладчика"])

# --- Вкладка 1: Калькулятор ---
with tab1:
    st.markdown("### 🏭 Ввод данных по ТПА")
    
    for tpa in TPA_LIST:
        # Используем expander, чтобы на телефоне не было бесконечной прокрутки
        with st.expander(f"**{tpa}**", expanded=False):
            d = st.session_state.tpa_data[tpa]
            
            col1, col2 = st.columns(2)
            with col1:
                d['material'] = st.selectbox("Материал", MATERIALS, key=f"mat_{tpa}")
                d['per_box'] = st.number_input("Готовые: шт. в кор.", min_value=0, step=1, key=f"pb_{tpa}")
                d['weight'] = st.number_input("Вес 1 дет. (г)", min_value=0.0, step=0.001, format="%.3f", key=f"w_{tpa}")
            
            with col2:
                d['boxes'] = st.number_input("Готовые: кол-во кор.", min_value=0, step=1, key=f"bx_{tpa}")
                d['defect'] = st.number_input("Брак (шт)", min_value=0, step=1, key=f"df_{tpa}")

# --- Вкладка 2: Для наладчика (Сводка) ---
with tab2:
    st.markdown("### 📊 Сводка для наладчика")
    
    summary_data = []
    material_totals = {mat: {'total': 0.0, 'good': 0.0, 'defect': 0.0} for mat in MATERIALS}
    has_data = False

    for tpa in TPA_LIST:
        d = st.session_state.tpa_data[tpa]
        
        # Расчет
        good_parts = d['per_box'] * d['boxes']
        defect_parts = d['defect']
        
        good_w = (good_parts * d['weight']) / 1000
        defect_w = (defect_parts * d['weight']) / 1000
        total_w = good_w + defect_w        
        if good_parts > 0 or defect_parts > 0:
            has_data = True
            summary_data.append({
                "ТПА": tpa,
                "Материал": d['material'],
                "Готовые (шт)": good_parts,
                "Брак (шт)": defect_parts,
                "Вес готовых (кг)": f"{good_w:.3f}",
                "Вес брака (кг)": f"{defect_w:.3f}",
                "Общий вес (кг)": f"{total_w:.3f}"
            })
            
            # Суммируем по сырью
            mat = d['material']
            material_totals[mat]['total'] += total_w
            material_totals[mat]['good'] += good_w
            material_totals[mat]['defect'] += defect_w

    if has_data:
        # Таблица с данными
        df = pd.DataFrame(summary_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.markdown("### 📦 Итого по сырью:")
        
        mat_data = []
        for mat, stats in material_totals.items():
            if stats['total'] > 0:
                mat_data.append({
                    "Материал": mat,
                    "Всего (кг)": f"{stats['total']:.3f}",
                    "Готовые (кг)": f"{stats['good']:.3f}",
                    "Брак (кг)": f"{stats['defect']:.3f}"
                })
        
        if mat_data:
            df_mat = pd.DataFrame(mat_data)
            st.dataframe(df_mat, use_container_width=True, hide_index=True)
    else:
        st.info("Заполните данные во вкладке 'Калькулятор', чтобы увидеть сводку.")