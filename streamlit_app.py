import streamlit as st
import os
import subprocess
import networkx as nx
import matplotlib.pyplot as plt

st.set_page_config(page_title="Mô phỏng Đồ án OS", layout="wide")
st.title("🖥️ Giao Diện Trực Quan Hóa Quản Lý Deadlock")

# Thanh điều khiển bên trái
st.sidebar.header("🕹️ Bảng điều khiển")
if st.sidebar.button("🚀 Chạy Giả Lập Hệ Điều Hành"):
    with st.spinner("Đang chạy thuật toán lõi dưới Backend..."):
        # Gọi file backend chạy tự động để cập nhật file log
        subprocess.run(["python", "os_backend.py"])
        st.sidebar.success("Cập nhật dữ liệu Log thành công!")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 Nhật ký log thời gian thực (os_simulation.log)")
    if os.path.exists("os_simulation.log"):
        with open("os_simulation.log", "r", encoding="utf-8") as f:
            logs = f.readlines()
        
        styled_html = ""
        for line in logs:
            if "Approved" in line or "RELEASE" in line:
                styled_html += f"<p style='color:green; margin:2px;'>🟢 {line.strip()}</p>"
            elif "Wait" in line or "Denied" in line:
                styled_html += f"<p style='color:orange; margin:2px;'>🟡 {line.strip()}</p>"
            elif "DEADLOCK" in line:
                styled_html += f"<p style='color:red; background-color:#ffcccc; margin:2px;'>🔴 {line.strip()}</p>"
            else:
                styled_html += f"<p style='color:gray; margin:2px;'>{line.strip()}</p>"
        st.markdown(styled_html, unsafe_allow_html=True)
    else:
        st.info("Nhấn nút bên trái để tạo dữ liệu log.")

with col2:
    st.subheader("🌐 Đồ thị cấp phát tài nguyên (RAG)")
    st.write("Mô phỏng mối quan hệ giữa Tiến trình (P) và Tài nguyên (R)")
    
    # Vẽ đồ thị RAG mẫu trực quan lên giao diện Web
    G = nx.DiGraph()
    G.add_edges_from([("R0", "P0"), ("P0", "R1"), ("R1", "P1"), ("P1", "R0"), ("R2", "P2")])
    fig, ax = plt.subplots(figsize=(6, 4))
    pos = {"P0": (0, 1), "P1": (2, 1), "P2": (4, 1), "R0": (0, 0), "R1": (2, 0), "R2": (4, 0)}
    
    nx.draw(G, pos, ax=ax, with_labels=True, node_size=1200, 
            node_color=["#ffcbd1" if n in ["P0","P1","R0","R1"] else "#e2ecd5" for n in G.nodes()],
            edge_color="red", width=2, arrowsize=15)
    st.pyplot(fig)
    