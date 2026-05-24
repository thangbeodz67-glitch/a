import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from sklearn.tree import DecisionTreeClassifier

# --- 1. CẤU HÌNH GIAO DIỆN DASHBOARD ---
st.set_page_config(page_title="OS Deadlock Simulation Dashboard", layout="wide")

st.markdown("""
    <style>
    .main-title { font-size: 38px; font-weight: bold; color: #1E3A8A; text-align: center; margin-bottom: 20px; }
    .sub-title { font-size: 18px; text-align: center; color: #4B5563; margin-bottom: 40px; }
    .card { background-color: #F3F4F6; padding: 20px; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>🖥️ Hệ Thống Trực Quan Hóa & Dự Báo Deadlock Hệ Điều Hành</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Đồ án Mô phỏng Thuật toán Banker & Đồ thị Cấp phát Tài nguyên (RAG) nâng cao</div>", unsafe_allow_html=True)

# --- 2. TRÍ TUỆ NHÂN TẠO DỰ BÁO SỚM (SCIKIT-LEARN) ---
@st.cache_resource
def train_deadlock_model():
    # X: [Tài nguyên tự do R0, R1, R2, Số lượng Tiến trình đang đợi]
    X_train = np.array([
        [3, 3, 2, 0], [1, 1, 1, 2], [0, 0, 1, 5], [5, 5, 5, 0],
        [2, 1, 1, 3], [0, 1, 0, 4], [4, 3, 3, 1], [0, 0, 0, 6]
    ])
    # y: 0 là Safe (An toàn), 1 là Unsafe (Nguy cơ nghẽn mạch cao)
    y_train = np.array([0, 0, 1, 0, 0, 1, 0, 1])
    model = DecisionTreeClassifier(random_state=42)
    model.fit(X_train, y_train)
    return model

ai_core = train_deadlock_model()

# --- 3. THANH ĐIỀU KHIỂN SIDEBAR ---
st.sidebar.markdown("### 🕹️ Bảng Điều Khiển Hệ Thống")
st.sidebar.write("Nhấn nút dưới đây để giả lập luồng chạy ngẫu nhiên từ file backend:")

if st.sidebar.button("🚀 Khởi Chạy Giả Lập OS", key="run_os_simulation"):
    st.session_state['os_sim_active'] = True
    st.sidebar.success("Kích hoạt luồng thành công!")

st.sidebar.write("---")
st.sidebar.markdown("### 🧠 AI Predictive Analytics (Scikit-learn)")
st.sidebar.write("Mô phỏng dự đoán rủi ro trước khi cấp phát tài nguyên thực tế:")
slider_r0 = st.sidebar.slider("Tài nguyên R0 tự do hiện tại:", 0, 10, 3)
slider_r1 = st.sidebar.slider("Tài nguyên R1 tự do hiện tại:", 0, 10, 3)
slider_r2 = st.sidebar.slider("Tài nguyên R2 tự do hiện tại:", 0, 10, 2)
input_wait = st.sidebar.number_input("Số luồng đang kẹt xếp hàng (Wait):", min_value=0, max_value=10, value=1)

# --- 4. PHÂN CHIA BỐ CỤC KHÔNG GIAN (LAYOUT) ---
col1, col2 = st.columns([1.1, 0.9])

# --- CỘT TẢI DỮ LIỆU NHẬT KÝ LOG ---
with col1:
    st.markdown("### 📝 Nhật ký tiến trình thời gian thực (`os_simulation.log`)")
    
    # Dữ liệu mẫu đồng bộ logic chuẩn từ file backend của bạn
    backend_logs = [
        "2026-05-24 16:04:08 - [INFO] - === BẮT ĐẦU GIẢ LẬP OS ===",
        "2026-05-24 16:04:08 - [INFO] - Trạng thái cấu hình tài nguyên ban đầu: [3, 3, 2]",
        "2026-05-24 16:04:08 - [INFO] - START: Tiến trình P0 bắt đầu khởi tạo.",
        "2026-05-24 16:04:08 - [INFO] - REQUEST: P0 đưa ra yêu cầu xin cấp phát tài nguyên [1, 0, 1]",
        "2026-05-24 16:04:08 - [INFO] - BANKER RESPONSE to P0: Approved: Cấp phát thành công! Đạt trạng thái Safe State. | Còn lại: [2, 3, 1]",
        "2026-05-24 16:04:08 - [INFO] - RAG CHECK: Đồ thị không tồn tại chu trình.",
        "2026-05-24 16:04:09 - [INFO] - START: Tiến trình P1 bắt đầu khởi tạo.",
        "2026-05-24 16:04:09 - [INFO] - REQUEST: P1 đưa ra yêu cầu xin cấp phát tài nguyên [4, 2, 2]",
        "2026-05-24 16:04:09 - [INFO] - BANKER RESPONSE to P1: Wait: Số lượng tài nguyên vượt quá Available, luồng bắt đầu ngủ đợi giải phóng... | Còn lại: [2, 3, 1]",
        "2026-05-24 16:04:09 - [INFO] - RAG CHECK: Phát hiện luồng đợi cạnh (P1 -> R0).",
        "2026-05-24 16:04:10 - [INFO] - START: Tiến trình P2 bắt đầu khởi tạo.",
        "2026-05-24 16:04:10 - [INFO] - REQUEST: P2 đưa ra yêu cầu xin cấp phát tài nguyên [3, 0, 2]",
        "2026-05-24 16:04:10 - [INFO] - BANKER RESPONSE to P2: Denied: Không thể cấp phát! Hệ thống sẽ rơi vào vòng Unsafe State nguy hiểm. | Còn lại: [2, 3, 1]",
        "2026-05-24 16:04:10 - [WARNING] - RAG CHECK: Đồ thị sinh chu trình ảo. Hệ thống chặn đứng nguy cơ Deadlock.",
        "2026-05-24 16:04:11 - [INFO] - RELEASE: P0 hoàn thành công việc, tự động giải phóng giải găng tài nguyên.",
        "2026-05-24 16:04:11 - [INFO] - === KẾT THÚC GIẢ LẬP OS ==="
    ]

    if st.session_state.get('os_sim_active', False):
        html_output = "<div style='background-color: #1E293B; padding: 15px; border-radius: 8px; font-family: monospace; height: 420px; overflow-y: auto;'>"
        for line in backend_logs:
            if "Approved" in line or "RELEASE" in line:
                html_output += f"<p style='color: #4ADE80; margin: 4px 0;'>🟢 {line}</p>"
            elif "Wait" in line or "Denied" in line:
                html_output += f"<p style='color: #FBBF24; margin: 4px 0;'>🟡 {line}</p>"
            elif "DEADLOCK" in line or "WARNING" in line:
                html_output += f"<p style='color: #F87171; background-color: rgba(220,38,38,0.2); padding: 2px; margin: 4px 0;'>🔴 {line}</p>"
            else:
                html_output += f"<p style='color: #9CA3AF; margin: 4px 0;'>{line}</p>"
        html_output += "</div>"
        st.markdown(html_output, unsafe_allow_html=True)
    else:
        st.info("💡 Trạng thái hệ thống đang chờ. Hãy nhấn nút 'Khởi Chạy Giả Lập OS' ở thanh menu điều khiển bên trái để kích hoạt luồng.")

# --- CỘT TRỰC QUAN HÓA TOÁN HỌC ĐỒ THỊ ---
with col2:
    st.markdown("### 🌐 Trực quan hóa Đồ thị Động RAG (NetworkX)")
    
    # Thiết lập phân tích đồ thị toán học bằng NetworkX
    RAG = nx.DiGraph()
    RAG.add_nodes_from(["P0", "P1", "P2"], bipartite=0)
    RAG.add_nodes_from(["R0", "R1", "R2"], bipartite=1)
    
    # Thiết lập chu trình mô phỏng găng cho thuật toán chấm điểm đồ thị
    RAG.add_edges_from([("R0", "P0"), ("P0", "R1"), ("R1", "P1"), ("P1", "R0"), ("R2", "P2")])
    
    fig, ax = plt.subplots(figsize=(6, 4.5))
    node_positions = {"P0": (0, 1), "P1": (2, 1), "P2": (4, 1), "R0": (0, 0), "R1": (2, 0), "R2": (4, 0)}
    
    # Phân phối màu sắc cấu trúc đồ thị động
    color_map = ["#FED7D7" if node in ["P0", "P1", "R0", "R1"] else "#DEF7EC" for node in RAG.nodes()]
    edge_color_map = ["#E53E3E" if edge in [("P0","R1"),("R1","P1"),("P1","R0"),("R0","P0")] else "#9CA3AF" for edge in RAG.edges()]
    
    nx.draw(RAG, node_positions, ax=ax, with_labels=True, node_size=1400, 
            node_color=color_map, edge_color=edge_color_map, width=2.5, arrowsize=18, font_weight="bold")
    
    st.pyplot(fig)
    st.caption("🔴 Cạnh màu đỏ thể hiện các yêu cầu đang bị giữ và kẹt xoay vòng gây nguy hiểm (Circular Wait).")

# --- 5. PANEL HIỂN THỊ KẾT QUẢ AI DỰ BÁO XUỐNG DƯỚI CÙNG ---
st.write("---")
st.markdown("### 📊 Trạng thái phân tích rủi ro từ Trí Tuệ Nhân Tạo")

ai_input = np.array([[slider_r0, slider_r1, slider_r2, input_wait]])
ai_prediction = ai_core.predict(ai_input)

if ai_prediction[0] == 0:
    st.success("✅ MÔ HÌNH ML ĐÁNH GIÁ: Hệ thống hiện tại đang an toàn (Safe State). Xác suất xảy ra vòng khóa thấp.")
else:
    st.error("⚠️ AI PHÂN TÍCH CẢNH BÁO: Phân phối tài nguyên tự do quá ít trong khi hàng chờ quá tải! Nguy cơ sập hệ thống (Deadlock) cực kỳ cao.")