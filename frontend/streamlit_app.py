import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import base64
import io
from datetime import datetime

# 後端 API 基礎 URL
API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="GradeInsight 成績管理系統",
    page_icon="📊",
    layout="wide"
)

st.title("📊 GradeInsight 成績管理系統")
st.markdown("歡迎使用智慧成績管理平台")

# 側邊欄導航
st.sidebar.title("功能選單")
page = st.sidebar.radio(
    "選擇功能",
    ["儀表板", "學生列表", "成績統計", "風險學生", "成績分佈", "匯入成績", "編輯成績", "匯出報告", "備份管理"]
)

def api_request(method, endpoint, data=None, files=None):
    """通用 API 請求函數"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            if files:
                response = requests.post(url, files=files, data=data)
            else:
                response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API 請求失敗: {response.text}")
            return None
    except Exception as e:
        st.error(f"連接後端失敗: {str(e)}")
        return None

# 儀表板頁面
if page == "儀表板":
    st.header("📈 系統儀表板")

    col1, col2, col3 = st.columns(3)

    # 獲取統計數據
    stats = api_request("GET", "/statistics")
    if stats:
        with col1:
            st.metric("平均成績", f"{stats['average']:.1f}")
        with col2:
            st.metric("及格率", f"{stats['pass_rate']:.1f}%")
        with col3:
            st.metric("學生總數", len(api_request("GET", "/students") or []))

    # 成績分佈圖
    st.subheader("成績分佈")
    dist_data = api_request("GET", "/distribution")
    if dist_data and dist_data['grades']:
        fig, ax = plt.subplots()
        ax.hist(dist_data['grades'], bins=dist_data['bins'], edgecolor='black')
        ax.set_title("成績分佈直方圖")
        ax.set_xlabel("成績")
        ax.set_ylabel("人數")
        st.pyplot(fig)

# 學生列表頁面
elif page == "學生列表":
    st.header("👥 學生列表")

    students = api_request("GET", "/students")
    if students:
        df = pd.DataFrame([
            {
                "學號": s["student_id"],
                "姓名": s["name"],
                "平時": s["grades"]["usual"],
                "期中": s["grades"]["midterm"],
                "期末": s["grades"]["final"],
                "總分": s["grades"]["total"]
            } for s in students
        ])
        st.dataframe(df, use_container_width=True)

        # 學生詳情
        selected_student = st.selectbox("選擇學生查看詳情", [s["student_id"] for s in students])
        if selected_student:
            detail = api_request("GET", f"/students/{selected_student}")
            if detail:
                st.subheader(f"學生詳情: {detail['student']['name']}")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**學號:** {detail['student']['student_id']}")
                    st.write(f"**平時成績:** {detail['student']['grades']['usual']}")
                    st.write(f"**期中成績:** {detail['student']['grades']['midterm']}")
                with col2:
                    st.write(f"**期末成績:** {detail['student']['grades']['final']}")
                    st.write(f"**總成績:** {detail['student']['grades']['total']}")

# 成績統計頁面
elif page == "成績統計":
    st.header("📊 成績統計分析")

    stats = api_request("GET", "/statistics")
    if stats:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("平均分", f"{stats['average']:.1f}")
        with col2:
            st.metric("中位數", f"{stats['median']:.1f}")
        with col3:
            st.metric("標準差", f"{stats['std_dev']:.1f}")
        with col4:
            st.metric("及格率", f"{stats['pass_rate']:.1f}%")

        st.subheader("成績等級分佈")
        dist = stats['distribution']
        fig, ax = plt.subplots()
        ax.bar(dist.keys(), dist.values())
        ax.set_title("成績等級分佈")
        ax.set_xlabel("等級")
        ax.set_ylabel("人數")
        st.pyplot(fig)

# 風險學生頁面
elif page == "風險學生":
    st.header("⚠️ 風險學生識別")

    threshold = st.slider("不及格閾值", 0, 100, 60)
    at_risk = api_request("GET", f"/at-risk?threshold={threshold}")

    if at_risk:
        st.write(f"發現 {len(at_risk)} 位風險學生")

        for student in at_risk:
            with st.expander(f"{student['student']['name']} ({student['student']['student_id']}) - 風險等級: {student['risk_level']}"):
                st.write(f"**總成績:** {student['student']['grades']['total']}")
                st.write("**風險原因:**")
                for reason in student['reasons']:
                    st.write(f"- {reason}")

# 成績分佈頁面
elif page == "成績分佈":
    st.header("📈 成績分佈圖表")

    dist_data = api_request("GET", "/distribution")
    if dist_data and dist_data['grades']:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("直方圖")
            fig, ax = plt.subplots()
            ax.hist(dist_data['grades'], bins=10, edgecolor='black')
            ax.set_title("成績分佈")
            ax.set_xlabel("成績")
            ax.set_ylabel("人數")
            st.pyplot(fig)

        with col2:
            st.subheader("圓餅圖")
            stats = api_request("GET", "/statistics")
            if stats:
                labels = list(stats['distribution'].keys())
                sizes = list(stats['distribution'].values())
                fig, ax = plt.subplots()
                ax.pie(sizes, labels=labels, autopct='%1.1f%%')
                ax.set_title("成績等級比例")
                st.pyplot(fig)

# 匯入成績頁面
elif page == "匯入成績":
    st.header("📥 匯入成績數據")

    uploaded_file = st.file_uploader("選擇 CSV 或 Excel 檔案", type=['csv', 'xlsx'])

    if uploaded_file is not None:
        file_data = base64.b64encode(uploaded_file.read()).decode()
        file_type = 'csv' if uploaded_file.name.endswith('.csv') else 'excel'

        if st.button("開始匯入"):
            with st.spinner("正在匯入..."):
                result = api_request("POST", "/import", {
                    "file_data": file_data,
                    "file_type": file_type
                })
                if result and result.get("success"):
                    st.success(result["message"])
                    st.rerun()
                else:
                    st.error(result.get("message", "匯入失敗"))

# 編輯成績頁面
elif page == "編輯成績":
    st.header("✏️ 編輯單個成績")

    students = api_request("GET", "/students")
    if students:
        student_options = {f"{s['name']} ({s['student_id']})": s['student_id'] for s in students}
        selected = st.selectbox("選擇學生", list(student_options.keys()))

        if selected:
            student_id = student_options[selected]
            student = next((s for s in students if s['student_id'] == student_id), None)

            if student:
                col1, col2, col3 = st.columns(3)
                with col1:
                    usual = st.number_input("平時成績", 0.0, 100.0, student['grades']['usual'])
                with col2:
                    midterm = st.number_input("期中成績", 0.0, 100.0, student['grades']['midterm'])
                with col3:
                    final = st.number_input("期末成績", 0.0, 100.0, student['grades']['final'])

                reason = st.text_input("修改原因")

                if st.button("更新成績"):
                    # 這裡簡化，只更新一個成績類型，實際應支持選擇
                    result = api_request("PUT", "/edit-grade", {
                        "student_id": student_id,
                        "grade_type": "final",  # 假設修改期末
                        "new_value": final,
                        "reason": reason
                    })
                    if result and result.get("success"):
                        st.success("成績已更新")
                        st.rerun()
                    else:
                        st.error(result.get("message", "更新失敗"))

# 匯出報告頁面
elif page == "匯出報告":
    st.header("📄 匯出成績報告")

    format_type = st.selectbox("選擇格式", ["csv", "excel"])
    min_score = st.number_input("最低分數篩選", 0, 100, 0)
    max_score = st.number_input("最高分數篩選", 0, 100, 100)

    if st.button("匯出報告"):
        filters = {"min_score": min_score, "max_score": max_score}
        result = api_request("POST", "/export", {
            "format": format_type,
            "filters": filters
        })

        if result and result.get("success"):
            data = result["data"]
            filename = result["filename"]

            if format_type == "csv":
                b64 = base64.b64encode(data.encode()).decode()
            else:
                b64 = data

            href = f'<a href="data:file/{format_type};base64,{b64}" download="{filename}">下載 {filename}</a>'
            st.markdown(href, unsafe_allow_html=True)
        else:
            st.error(result.get("message", "匯出失敗"))

# 備份管理頁面
elif page == "備份管理":
    st.header("💾 備份管理")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("立即備份"):
            with st.spinner("正在備份..."):
                result = api_request("POST", "/backup")
                if result and result.get("success"):
                    st.success(result["message"])
                else:
                    st.error(result.get("message", "備份失敗"))

    with col2:
        if st.button("查看備份狀態"):
            status = api_request("GET", "/backup/status")
            if status:
                st.write(f"**狀態:** {status['status']}")
                if status['last_backup']:
                    st.write(f"**最後備份:** {status['last_backup']}")
                if status['message']:
                    st.write(f"**訊息:** {status['message']}")

    # 重新生成模擬數據
    st.subheader("開發者工具")
    if st.button("重新生成模擬數據"):
        result = api_request("POST", "/generate-mock-data")
        if result:
            st.success("模擬數據已重新生成")
            st.rerun()

# 頁面底部
st.sidebar.markdown("---")
st.sidebar.markdown("© 2024 GradeInsight 系統")