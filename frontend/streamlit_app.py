import streamlit as st
import requests
import pandas as pd
import base64
import io
import os

API_BASE_URL = os.getenv("GRADEINSIGHT_API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="GradeInsight 成績管理系統", page_icon="📊", layout="wide")

st.title("📊 GradeInsight 成績管理系統")
st.write("歡迎使用成績管理平台，請先確保後端 API 已啟動。")

menu = st.sidebar.selectbox(
    "功能選單",
    [
        "系統狀態",
        "匯入成績",
        "成績分佈",
        "風險學生",
        "學生成績",
        "成績編輯",
        "匯出報告",
        "模擬資料"
    ]
)


def api_request(method, endpoint, json=None):
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method == "GET":
            res = requests.get(url, timeout=8)
        elif method == "POST":
            res = requests.post(url, json=json, timeout=10)
        elif method == "PUT":
            res = requests.put(url, json=json, timeout=10)
        else:
            return None

        if res.status_code in (200, 201):
            return res.json()
        else:
            st.error(f"API 錯誤：{res.status_code} - {res.text}")
            return None
    except requests.exceptions.RequestException as exc:
        st.error(f"無法連接後端 API：{exc}")
        return None


if menu == "系統狀態":
    st.header("系統狀態檢查")
    st.write(f"後端 API 位置：{API_BASE_URL}")
    health = api_request("GET", "/api/health")
    if health:
        st.success(health)

elif menu == "匯入成績":
    st.header("📥 匯入成績")
    uploaded = st.file_uploader("請上傳 CSV 或 Excel 檔案", type=["csv", "xlsx"])
    if uploaded is not None:
        file_bytes = uploaded.read()
        file_data = base64.b64encode(file_bytes).decode("utf-8")
        file_type = "csv" if uploaded.name.endswith(".csv") else "excel"

        if st.button("預覽匯入資料"):
            result = api_request("POST", "/api/grades/import/preview", {
                "file_data": file_data,
                "file_type": file_type
            })
            if result:
                st.subheader("匯入預覽")
                st.write(f"總筆數：{result['rows']}")
                st.dataframe(pd.DataFrame(result["preview"]))

        if st.button("確認匯入"):
            result = api_request("POST", "/api/grades/import", {
                "file_data": file_data,
                "file_type": file_type
            })
            if result:
                if result.get("success"):
                    st.success(result.get("message"))
                    if result.get("errors"):
                        st.warning("部分資料被跳過，請查看錯誤訊息。")
                        for err in result.get("errors", []):
                            st.write(f"- {err}")
                else:
                    st.error(result.get("message"))

elif menu == "成績分佈":
    st.header("📈 成績分佈")
    stats = api_request("GET", "/api/statistics/summary")
    dist = api_request("GET", "/api/statistics/distribution")
    if stats and dist:
        cols = st.columns(4)
        cols[0].metric("平均分", stats["average"])
        cols[1].metric("中位數", stats["median"])
        cols[2].metric("標準差", stats["std_dev"])
        cols[3].metric("及格率", f"{stats['pass_rate']}%")

        st.subheader("成績等級分佈")
        df = pd.DataFrame({"等級": list(stats["distribution"].keys()), "人數": list(stats["distribution"].values())})
        st.bar_chart(df.set_index("等級"))

        st.subheader("分數區間直方圖")
        st.bar_chart({"區間": [f"{dist['bins'][i]}-{dist['bins'][i+1]}" for i in range(len(dist['counts']))], "人數": dist['counts']})

elif menu == "風險學生":
    st.header("⚠️ 風險學生識別")
    threshold = st.slider("警戒分數閾值", 0, 100, 60)
    risk_students = api_request("GET", f"/api/grades")
    if risk_students is not None:
        filtered = [s for s in risk_students if s["total"] < threshold]
        st.write(f"目前共有 {len(filtered)} 位成績低於 {threshold} 分的學生。")
        for student in filtered:
            with st.expander(f"{student['name']} ({student['student_id']}) - {student['total']} 分"):
                st.write(f"平時：{student['usual']}")
                st.write(f"期中：{student['midterm']}")
                st.write(f"期末：{student['final']}")

elif menu == "學生成績":
    st.header("👥 學生成績檢視")
    students = api_request("GET", "/api/grades")
    if students is not None:
        df = pd.DataFrame(students)
        st.dataframe(df[["student_id", "name", "usual", "midterm", "final", "total"]])
        selected = st.selectbox("選擇學生查看詳情", [s["student_id"] for s in students])
        if selected:
            details = api_request("GET", f"/api/grades/student/{selected}")
            if details:
                st.write(f"**姓名**：{details['name']}")
                st.write(f"**學號**：{details['student_id']}")
                st.write(f"**平時**：{details['usual']}")
                st.write(f"**期中**：{details['midterm']}")
                st.write(f"**期末**：{details['final']}")
                st.write(f"**總成績**：{details['total']}")

elif menu == "成績編輯":
    st.header("✏️ 成績編輯")
    students = api_request("GET", "/api/grades")
    if students is not None:
        student_map = {f"{s['name']} ({s['student_id']})": s for s in students}
        selected = st.selectbox("選擇學生", list(student_map.keys()))
        if selected:
            student = student_map[selected]
            grade_type = st.selectbox("選擇成績類型", ["usual", "midterm", "final"], format_func=lambda x: {"usual":"平時","midterm":"期中","final":"期末"}[x])
            new_value = st.number_input("新成績", min_value=0.0, max_value=100.0, value=student[grade_type])
            reason = st.text_input("修改原因", value="成績修正")
            if st.button("提交修改"):
                payload = {
                    "student_id": student["student_id"],
                    "grade_type": grade_type,
                    "new_value": new_value,
                    "reason": reason
                }
                result = api_request("PUT", f"/api/grades/student/{student['student_id']}", json=payload)
                if result and result.get("success"):
                    st.success(result.get("message"))
                elif result:
                    st.error(result.get("message"))

elif menu == "匯出報告":
    st.header("📄 匯出成績報告")
    format_type = st.radio("選擇匯出格式", ["csv", "excel"])
    min_score = st.number_input("最低總分", min_value=0.0, max_value=100.0, value=0.0)
    max_score = st.number_input("最高總分", min_value=0.0, max_value=100.0, value=100.0)
    if st.button("匯出"): 
        payload = {"format": format_type, "filters": {"min_score": min_score, "max_score": max_score}}
        result = api_request("POST", "/api/export/class-report", json=payload)
        if result and result.get("success"):
            decoded = base64.b64decode(result["data"])
            if format_type == "csv":
                st.download_button("下載報告", data=decoded, file_name=result["filename"], mime="text/csv")
            else:
                st.download_button("下載報告", data=decoded, file_name=result["filename"], mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        elif result:
            st.error(result.get("message"))

elif menu == "模擬資料":
    st.header("🧪 生成模擬資料")
    if st.button("生成 30 筆模擬學生成績"):
        result = api_request("POST", "/api/data/generate-sample")
        if result and result.get("success"):
            st.success(result.get("message"))
        elif result:
            st.error(result.get("message"))
