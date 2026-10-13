import streamlit as st
import cv2
import os
import pandas as pd
import hashlib
import zipfile
import io
from datetime import datetime

# ตั้งค่าหน้าจอและ Theme
st.set_page_config(
    page_title="Auto Product Capture - Multi-User System",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS ตกแต่งหน้าตาภาพรวมทั้งหมด ปรับสีปุ่มและช่องต่างๆ ให้สวยงามเด่นชัด
st.markdown("""
    <style>
    .stApp {
        background-color: #05070c;
        color: #f8fafc;
    }
    header[data-testid="stHeader"] {
        background-color: rgba(5, 7, 12, 0.95) !important;
        border-bottom: 1px solid #1e293b;
    }
    section[data-testid="stSidebar"] {
        background-color: #0b0f19;
        border-right: 1px solid #1e293b;
    }
    .stApp::before {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background-image: 
            radial-gradient(circle at 10% 15%, rgba(59, 130, 246, 0.18) 0%, transparent 45%),
            radial-gradient(circle at 90% 85%, rgba(168, 85, 247, 0.15) 0%, transparent 45%);
        z-index: 0;
        pointer-events: none;
    }
    .hero-container {
        background: linear-gradient(135deg, rgba(30, 58, 138, 0.85) 0%, rgba(15, 23, 42, 0.95) 100%);
        border: 1px solid #3b82f6;
        padding: 30px;
        border-radius: 16px;
        color: #ffffff;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
        position: relative;
        z-index: 1;
    }
    .hero-title {
        font-size: 1.9rem;
        font-weight: 800;
        color: #60a5fa;
        text-shadow: 0 2px 4px rgba(0,0,0,0.5);
        margin-bottom: 8px;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        color: #cbd5e1;
        font-weight: 500;
    }
    
    /* 🔵 ปรับแต่งกล่อง Expander ให้เป็นสีฟ้า/น้ำเงินเข้ม ตัวหนังสือสีขาวคมชัด */
    [data-testid="stExpander"] {
        background: linear-gradient(135deg, rgba(30, 64, 175, 0.85) 0%, rgba(15, 23, 42, 0.95) 100%) !important;
        border: 1px solid #3b82f6 !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3) !important;
    }
    [data-testid="stExpander"] summary {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    [data-testid="stExpander"] summary span, [data-testid="stExpander"] summary p {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    [data-testid="stExpander"] summary svg {
        fill: #60a5fa !important;
    }

    /* 🔵 ปรับแต่ง Toolbar ของตาราง (ช่อง Search และปุ่มควบคุมมุมขวาบน) ให้เป็นสีฟ้า */
    [data-testid="stElementToolbar"], div.stDataFrameToolbar, div[data-testid="stDataFrame"] > div > div > div {
        background-color: #1e3a8a !important;
        color: #ffffff !important;
    }
    [data-testid="stElementToolbar"] button, div.stDataFrameToolbar button {
        background-color: #2563eb !important;
        color: #ffffff !important;
        border: 1px solid #60a5fa !important;
        border-radius: 6px !important;
    }
    [data-testid="stElementToolbar"] button svg, div.stDataFrameToolbar button svg {
        fill: #ffffff !important;
    }
    [data-testid="stElementToolbar"] button span, div.stDataFrameToolbar button span,
    [data-testid="stElementToolbar"] button div, div.stDataFrameToolbar button div {
        color: #ffffff !important;
    }
    [data-testid="stElementToolbar"] input {
        background-color: #0f172a !important;
        color: #ffffff !important;
        border: 1px solid #60a5fa !important;
    }

    /* 🟢 ปรับแต่งกล่อง File Uploader และปุ่ม Upload ให้เป็นสีเขียว */
    [data-testid="stFileUploader"] {
        background-color: #0f172a;
        border: 2px dashed #3b82f6;
        padding: 15px;
        border-radius: 12px;
    }
    [data-testid="stFileUploader"] section {
        background-color: #0f172a !important;
    }
    [data-testid="stFileUploader"] button {
        background: linear-gradient(90deg, #22c55e, #16a34a) !important;
        color: #000000 !important;
        font-weight: 800 !important;
        border: 2px solid #86efac !important;
        border-radius: 8px !important;
    }
    [data-testid="stFileUploader"] button:hover {
        background: linear-gradient(90deg, #16a34a, #15803d) !important;
        color: #ffffff !important;
    }

    /* 🟢 ปุ่มทั่วไปในระบบ */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #2563eb, #9333ea);
        color: #ffffff !important;
        font-weight: 700;
        font-size: 1rem;
        border-radius: 10px;
        padding: 0.6rem 1rem;
        border: 1px solid #60a5fa;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.5);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #1d4ed8, #7e22ce);
        box-shadow: 0 6px 20px rgba(147, 51, 234, 0.8);
        border-color: #c084fc;
    }

    /* 🟢 ปุ่มดาวน์โหลดทั้งหมดให้เป็นสีเขียวสดใส ตัวหนังสือสีดำ คมชัด */
    [data-testid="stDownloadButton"]>button {
        width: 100% !important;
        background: linear-gradient(90deg, #22c55e, #16a34a) !important;
        color: #000000 !important;
        font-weight: 800 !important;
        font-size: 0.95rem !important;
        border-radius: 10px !important;
        padding: 0.5rem 1rem !important;
        border: 2px solid #86efac !important;
        box-shadow: 0 4px 15px rgba(34, 197, 94, 0.4) !important;
        transition: all 0.3s ease;
    }
    [data-testid="stDownloadButton"]>button:hover {
        background: linear-gradient(90deg, #16a34a, #15803d) !important;
        color: #ffffff !important;
        border-color: #4ade80 !important;
        box-shadow: 0 6px 20px rgba(34, 197, 94, 0.8) !important;
    }

    .login-card {
        background: rgba(15, 23, 42, 0.95);
        padding: 35px;
        border-radius: 20px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.8);
        border: 1px solid #334155;
        position: relative;
        z-index: 1;
    }
    .stTextInput label, .stSlider label, .stSelectbox label, .stRadio label, p, span {
        color: #f1f5f9 !important;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

def get_safe_folder_name(filename):
    hash_object = hashlib.md5(filename.encode('utf-8'))
    return "vid_" + hash_object.hexdigest()[:10]

def create_csv(df):
    return df.to_csv(index=False).encode('utf-8-sig')

def create_text_report(df):
    report_lines = [
        "=== AUTO PRODUCT CAPTURE SUMMARY REPORT ===",
        f"Generated Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Total Frames: {len(df)}",
        "=" * 50 + "\n"
    ]
    for _, row in df.iterrows():
        report_lines.append(f"User: {row.get('Username', 'N/A')} | Video: {row['Video Name']} | File: {row['File Name']} | Time: {row['Timestamp (s)']}s | Score: {row['Sharpness Score']}")
    return "\n".join(report_lines).encode('utf-8')

# ---------------------------------------------------------
# 1. ระบบฐานข้อมูลจำลองผู้ใช้และสิทธิ์ (Admin vs User)
# ---------------------------------------------------------
if "users_db" not in st.session_state:
    # ค่าเริ่มต้น: แอดมินหลัก (admin / admin1234) และผู้ใช้ทั่วไป (user1 / user1234)
    st.session_state["users_db"] = {
        "admin": {"password": "admin1234", "role": "admin"},
        "user1": {"password": "user1234", "role": "user"}
    }

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "auth_page" not in st.session_state:
    st.session_state["auth_page"] = "login"

if "current_user" not in st.session_state:
    st.session_state["current_user"] = ""

if "user_role" not in st.session_state:
    st.session_state["user_role"] = ""

# ---------------------------------------------------------
# หน้าจอเข้าสู่ระบบและสมัครสมาชิก
# ---------------------------------------------------------
if not st.session_state["logged_in"]:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #60a5fa; font-weight: 800;'>🛍️ Auto Product Capture</h2>", unsafe_allow_html=True)
        
        if st.session_state["auth_page"] == "login":
            st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 1.05rem;'>ระบบอัตโนมัติคัดเลือกภาพสินค้าคมชัดจากวิดีโอ (Multi-User)</p>", unsafe_allow_html=True)
            st.markdown("<hr style='border-color: #334155; margin: 20px 0;'>", unsafe_allow_html=True)
            
            with st.form("login_form"):
                username = st.text_input("👤 ชื่อผู้ใช้งาน (Username)", value="admin")
                password = st.text_input("🔑 รหัสผ่าน (Password)", type="password")
                st.markdown("<br>", unsafe_allow_html=True)
                submit_login = st.form_submit_button("🚀 เข้าสู่ระบบ")
                
                if submit_login:
                    db = st.session_state["users_db"]
                    if username in db and db[username]["password"] == password:
                        st.session_state["logged_in"] = True
                        st.session_state["current_user"] = username
                        st.session_state["user_role"] = db[username]["role"]
                        st.success("เข้าสู่ระบบสำเร็จ!")
                        st.rerun()
                    else:
                        st.error("❌ ชื่อผู้ใช้งานหรือรหัสผ่านไม่ถูกต้อง")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("📝 สมัครสมาชิกใหม่ (Sign Up)"):
                st.session_state["auth_page"] = "register"
                st.rerun()

        elif st.session_state["auth_page"] == "register":
            st.markdown("<p style='text-align: center; color: #38bdf8; font-size: 1.05rem;'>สร้างบัญชีผู้ใช้งานใหม่เพื่อเข้าใช้งานระบบ</p>", unsafe_allow_html=True)
            st.markdown("<hr style='border-color: #334155; margin: 20px 0;'>", unsafe_allow_html=True)
            
            with st.form("register_form"):
                new_user = st.text_input("👤 กำหนดชื่อผู้ใช้งานใหม่ (New Username)")
                new_pass = st.text_input("🔑 กำหนดรหัสผ่านใหม่ (New Password)", type="password")
                confirm_pass = st.text_input("🔑 ยืนยันรหัสผ่าน (Confirm Password)", type="password")
                st.markdown("<br>", unsafe_allow_html=True)
                submit_register = st.form_submit_button("✨ ลงทะเบียนบัญชีใหม่")
                
                if submit_register:
                    db = st.session_state["users_db"]
                    if not new_user or not new_pass:
                        st.warning("⚠️ กรุณากรอกข้อมูลให้ครบถ้วน")
                    elif new_user in db:
                        st.error("❌ ชื่อผู้ใช้นี้มีอยู่ในระบบแล้ว กรุณาใช้ชื่ออื่น")
                    elif new_pass != confirm_pass:
                        st.error("❌ รหัสผ่านและยืนยันรหัสผ่านไม่ตรงกัน")
                    else:
                        db[new_user] = {"password": new_pass, "role": "user"}
                        st.success("🎉 สมัครสมาชิกสำเร็จ! กรุณากลับไปหน้าเข้าสู่ระบบ")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("⬅ กลับไปหน้าเข้าสู่ระบบ"):
                st.session_state["auth_page"] = "login"
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ---------------------------------------------------------
# ส่วนของระบบหลัก (จำแนกสิทธิ์ Admin และ User)
# ---------------------------------------------------------
current_user = st.session_state["current_user"]
user_role = st.session_state["user_role"]

with st.sidebar:
    role_title = "👑 ผู้ดูแลระบบ (Admin)" if user_role == "admin" else "👤 ผู้ใช้งานทั่วไป (User)"
    st.markdown(f"<h3 style='color: #60a5fa;'>{role_title}</h3>", unsafe_allow_html=True)
    st.markdown(f"**ผู้ใช้งาน:** {current_user}")
    st.markdown("---")
    
    if user_role == "admin":
        menu_choice = st.radio("📌 เมนูควบคุมระบบ", ["🚀 ระบบคัดกรองภาพสินค้า", "⚙️ จัดการระบบแอดมิน (Admin Panel)"])
    else:
        menu_choice = "🚀 ระบบคัดกรองภาพสินค้า"
        
    st.markdown("---")
    min_sharpness = st.slider("✨ ค่าความคมชัดขั้นต่ำ (Sharpness Threshold)", 10.0, 300.0, 80.0, 5.0)
    step_frames = st.slider("🎞️ ความถี่ในการเช็คเฟรม (Step Frames)", 5, 60, 15)
    st.markdown("---")
    if st.button("🚪 ออกจากระบบ"):
        st.session_state["logged_in"] = False
        st.session_state["current_user"] = ""
        st.session_state["user_role"] = ""
        st.rerun()

# ---------------------------------------------------------
# หน้าจัดการแอดมิน (เฉพาะ Admin)
# ---------------------------------------------------------
if user_role == "admin" and menu_choice == "⚙️ จัดการระบบแอดมิน (Admin Panel)":
    st.markdown("""
        <div class="hero-container">
            <div class="hero-title">🛡️ แผงควบคุมระบบสำหรับผู้ดูแลระบบ (Admin Panel)</div>
            <div class="hero-subtitle">ควบคุมสิทธิ์ผู้ใช้งานทั้งหมดในระบบ ตรวจสอบภาพรวม และจัดการฐานข้อมูลประวัติกลาง</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.subheader("👥 รายชื่อบัญชีผู้ใช้งานในระบบทั้งหมด")
    users_list = [{"Username": u, "Role": data["role"], "Password": data["password"]} for u, data in st.session_state["users_db"].items()]
    st.dataframe(pd.DataFrame(users_list), use_container_width=True)
    
    st.markdown("---")
    st.subheader("📊 จัดการประวัติการประมวลผลส่วนกลางของระบบ")
    history_file = "product_processing_history.csv"
    if os.path.exists(history_file):
        df_all = pd.read_csv(history_file)
        st.write(f"จำนวนข้อมูลประวัติทั้งหมดในระบบ: **{len(df_all)}** รายการ")
        if st.button("🗑️ ล้างประวัติทั้งหมดของระบบ (Admin Action)"):
            os.remove(history_file)
            st.success("ล้างประวัติส่วนกลางทั้งหมดเรียบร้อยแล้ว!")
            st.rerun()
    else:
        st.info("ยังไม่มีประวัติการประมวลผลในระบบ")
    st.stop()

# ---------------------------------------------------------
# หน้าหลักระบบคัดกรองภาพสินค้า
# ---------------------------------------------------------
st.markdown("""
    <div class="hero-container">
        <div class="hero-title">🛍️ ระบบอัตโนมัติคัดเลือกภาพสินค้าที่คมชัดจากวิดีโอ</div>
        <div class="hero-subtitle">Auto Product Capture : ระบบสกัดและคัดกรองภาพสินค้าคุณภาพดีจากวิดีโออัตโนมัติ</div>
    </div>
""", unsafe_allow_html=True)

base_out_dir = "product_snaps"
os.makedirs(base_out_dir, exist_ok=True)
history_file = "product_processing_history.csv"

source_mode = st.radio("📌 เลือกวิธีนำเข้าวิดีโอเข้าสู่ระบบ:", ["📤 อัปโหลดไฟล์วิดีโอใหม่", "🗂️ เลือกวิดีโอที่มีอยู่แล้วในโฟลเดอร์เครื่อง"], horizontal=True)

target_videos = [] 
if source_mode == "📤 อัปโหลดไฟล์วิดีโอใหม่":
    uploaded_files = st.file_uploader("📂 เลือกไฟล์วิดีโอสินค้า (รองรับ MP4, AVI, MOV)", type=["mp4", "avi", "mov"], accept_multiple_files=True)
    if uploaded_files:
        for f in uploaded_files:
            temp_path = f"temp_{f.name}"
            with open(temp_path, "wb") as out_f:
                out_f.write(f.read())
            target_videos.append({"name": f.name, "path": temp_path, "is_uploaded": True})
else:
    video_extensions = (".mp4", ".avi", ".mov", ".mkv")
    local_video_files = [f for f in os.listdir(".") if f.lower().endswith(video_extensions)]
    if local_video_files:
        selected_local_files = st.multiselect("🗂️ เลือกไฟล์วิดีโอจากโฟลเดอร์หลักในเครื่อง:", local_video_files)
        for f_name in selected_local_files:
            target_videos.append({"name": f_name, "path": f_name, "is_uploaded": False})
    else:
        st.info("💡 ไม่พบไฟล์วิดีโอในโฟลเดอร์หลักปัจจุบัน")

if target_videos:
    col_info, col_btn = st.columns([3, 1])
    with col_info:
        st.info(f"📁 เลือกวิดีโอพร้อมประมวลผลทั้งหมด **{len(target_videos)}** ไฟล์")
    with col_btn:
        start_btn = st.button("🚀 เริ่มประมวลผลภาพ")
        
    if start_btn:
        all_logs = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        total_files = len(target_videos)
        
        for file_idx, vid_info in enumerate(target_videos):
            video_orig_name = vid_info["name"]
            video_name_clean = os.path.splitext(video_orig_name)[0]
            video_path = vid_info["path"]
            
            safe_folder_code = get_safe_folder_name(video_orig_name)
            video_out_dir = os.path.join(base_out_dir, safe_folder_code)
            os.makedirs(video_out_dir, exist_ok=True)
            
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps == 0: fps = 30.0
            
            count, saved_count = 0, 0
            status_text.text(f"กำลังประมวลผลไฟล์: {video_orig_name} ({file_idx+1}/{total_files})")
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret: break
                
                if count % step_frames == 0:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    sharpness_score = cv2.Laplacian(gray, cv2.CV_64F).var()
                    
                    if sharpness_score >= min_sharpness:
                        saved_count += 1
                        timestamp_sec = round(count / fps, 2)
                        current_time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                        
                        file_name = f"frame{count}_t{timestamp_sec}s.jpg"
                        save_path = os.path.join(video_out_dir, file_name)
                        cv2.imwrite(save_path, frame)
                        
                        all_logs.append({
                            "Username": current_user,  # บันทึกเจ้าของรายการ
                            "Video Name": video_name_clean,
                            "Folder Code": safe_folder_code,
                            "File Name": file_name,
                            "Frame No": count,
                            "Timestamp (s)": timestamp_sec,
                            "Sharpness Score": round(sharpness_score, 2),
                            "Saved Time": current_time_str,
                            "Path": save_path
                        })
                count += 1
            
            cap.release()
            if vid_info["is_uploaded"] and os.path.exists(video_path):
                os.remove(video_path)
            progress_bar.progress((file_idx + 1) / total_files)
            
        status_text.empty()
        if all_logs:
            df_new = pd.DataFrame(all_logs)
            if os.path.exists(history_file):
                df_old = pd.read_csv(history_file)
                df_combined = pd.concat([df_old, df_new], ignore_index=True)
                df_combined.to_csv(history_file, index=False)
            else:
                df_new.to_csv(history_file, index=False)
                
        st.balloons()
        st.success("🎉 ประมวลผลและจัดเก็บภาพสินค้าเรียบร้อยแล้ว!")

# แดชบอร์ดสรุปผล
st.markdown("---")
st.markdown("<h3 style='color: #60a5fa;'>📊 แดชบอร์ดสรุปผลและประวัติการคัดกรองภาพสินค้า</h3>", unsafe_allow_html=True)

if os.path.exists(history_file):
    df_history = pd.read_csv(history_file)
    
    # หากเป็น User ทั่วไป ให้ดูเฉพาะข้อมูลของตนเอง / แอดมินสามารถดูได้ทั้งหมด
    if user_role != "admin" and "Username" in df_history.columns:
        df_history = df_history[df_history["Username"] == current_user]

    if df_history.empty:
        st.info("👋 ยังไม่มีประวัติการประมวลผลในระบบ กรุณาอัปโหลดวิดีโอเพื่อเริ่มต้นใช้งาน")
        st.stop()

    col_sel, col_del = st.columns([3, 1])
    with col_sel:
        selected_video = st.selectbox("📌 เลือกดูผลลัพธ์ตามชื่อวิดีโอสินค้า:", ["ทั้งหมด"] + list(df_history["Video Name"].unique()))
    
    with col_del:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ ล้างประวัติ"):
            if os.path.exists(history_file):
                df_full = pd.read_csv(history_file)
                if user_role == "admin":
                    os.remove(history_file)
                else:
                    df_full = df_full[df_full["Username"] != current_user]
                    df_full.to_csv(history_file, index=False)
                st.success("ล้างประวัติสำเร็จ!")
                st.rerun()

    if selected_video != "ทั้งหมด":
        filtered_df = df_history[df_history["Video Name"] == selected_video]
    else:
        filtered_df = df_history
        
    m1, m2, m3 = st.columns(3)
    m1.metric("🖼️ ภาพสินค้าผ่านเกณฑ์", f"{len(filtered_df)} ภาพ")
    m2.metric("📼 วิดีโอสินค้าในระบบ", f"{df_history['Video Name'].nunique()} ไฟล์")
    m3.metric("⚡ เกณฑ์ความคมชัด", f"{min_sharpness}")

    # ปุ่มดาวน์โหลดรายงาน
    st.markdown("<br>", unsafe_allow_html=True)
    dl_col1, dl_col2, _ = st.columns([1.5, 1.5, 3])
    with dl_col1:
        st.download_button(
            label="📊 ดาวน์โหลดรายงานเป็น CSV (เปิดใน Excel ได้) (.csv)",
            data=create_csv(filtered_df),
            file_name=f"product_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    with dl_col2:
        st.download_button(
            label="📄 ดาวน์โหลดรายงานสรุป (.txt)",
            data=create_text_report(filtered_df),
            file_name=f"product_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )
    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("📄 เปิดดูตารางบันทึกข้อมูลภาพสินค้า (Log Data & Scores)"):
        st.dataframe(filtered_df, use_container_width=True)
        
    if not filtered_df.empty:
        st.markdown("<h4 style='color: #38bdf8; margin-top: 25px;'>🖼️ แกลเลอรีภาพสินค้าคุณภาพดีที่สุด (แยกตามโฟลเดอร์วิดีโอ)</h4>", unsafe_allow_html=True)
        unique_videos = filtered_df["Video Name"].unique()
        
        for v_name in unique_videos:
            st.markdown(f"##### 📁 โฟลเดอร์วิดีโอ: <span style='color: #60a5fa;'>{v_name}</span>", unsafe_allow_html=True)
            v_df = filtered_df[filtered_df["Video Name"] == v_name]
            valid_images = []
            
            for _, row in v_df.iterrows():
                img_path = str(row["Path"])
                if not os.path.exists(img_path):
                    folder_code = row["Folder Code"] if "Folder Code" in row and pd.notna(row["Folder Code"]) else get_safe_folder_name(str(row["Video Name"]))
                    alt_path = os.path.join(base_out_dir, str(folder_code), str(row["File Name"]))
                    if os.path.exists(alt_path):
                        img_path = alt_path
                if os.path.exists(img_path):
                    valid_images.append((img_path, row['File Name'], row['Sharpness Score']))

            if valid_images:
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    for img_path, file_name, _ in valid_images:
                        if os.path.exists(img_path):
                            zip_file.write(img_path, arcname=file_name)
                zip_buffer.seek(0)
                
                st.download_button(
                    label=f"📦 ดาวน์โหลดภาพทั้งหมดของวิดีโอนี้ (.zip) [{len(valid_images)} ภาพ]",
                    data=zip_buffer,
                    file_name=f"{v_name}_all_snapshots.zip",
                    mime="application/zip",
                    key=f"zip_{v_name}"
                )
                st.markdown("<br>", unsafe_allow_html=True)

                cols = st.columns(3)
                for idx, (img_path, file_name, score) in enumerate(valid_images):
                    caption_text = f"{file_name} (ความคมชัด: {score})"
                    with cols[idx % 3]:
                        st.image(img_path, caption=caption_text, use_container_width=True)
                        with open(img_path, "rb") as file_bytes:
                            st.download_button(
                                label=f"📥 บันทึกภาพนี้",
                                data=file_bytes,
                                file_name=file_name,
                                mime="image/jpeg",
                                key=f"dl_{v_name}_{idx}"
                            )
            else:
                st.warning(f"⚠️ ไม่พบไฟล์รูปภาพสำหรับวิดีโอ {v_name}")
            st.markdown("<hr style='border-color: #1e293b; margin: 20px 0;'>", unsafe_allow_html=True)
else:
    st.info("👋 ยังไม่มีประวัติการประมวลผล กรุณาเลือกวิดีโอสินค้าด้านบนเพื่อเริ่มต้นใช้งาน")