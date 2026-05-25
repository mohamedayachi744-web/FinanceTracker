import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import arabic_reshaper
from bidi.algorithm import get_display

# إعداد كلمة السر (يمكنك تغييرها لاحقاً)
PASSWORD = "123"

# دالة تصحيح الخط العربي
def fix_arabic(text):
    reshaped_text = arabic_reshaper.reshape(text)
    return get_display(reshaped_text)

# دالة حفظ البيانات
def save_transaction(amount, category, description):
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY, date TEXT, amount REAL, category TEXT, description TEXT)")
    cursor.execute("INSERT INTO transactions (date, amount, category, description) VALUES (?, ?, ?, ?)",
                   (datetime.now().strftime("%Y-%m-%d"), amount, category, description))
    conn.commit()
    conn.close()

# صفحة تسجيل الدخول
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 تسجيل الدخول")
    password_input = st.text_input("أدخل كلمة السر:", type="password")
    if st.button("دخول"):
        if password_input == PASSWORD:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("كلمة السر خاطئة!")
else:
    # التطبيق الرئيسي (يعمل فقط بعد تسجيل الدخول)
    st.title("💰 مدير مصاريفي الشخصي")
    menu = ["إضافة عملية", "لوحة التحكم والتحليل"]
    choice = st.sidebar.selectbox("القائمة", menu)

    if choice == "إضافة عملية":
        st.subheader("سجل مصروفاً جديداً")
        with st.form("add_transaction"):
            amount = st.number_input("المبلغ (بالدرهم)", min_value=0.0)
            category = st.selectbox("التصنيف", ["مهني", "تعليم", "شخصي", "طوارئ"])
            description = st.text_input("وصف بسيط")
            submit = st.form_submit_button("حفظ العملية")
            if submit:
                save_transaction(amount, category, description)
                st.success("تم حفظ العملية!")

    elif choice == "لوحة التحكم والتحليل":
        st.subheader("تحليل مصاريفك")
        conn = sqlite3.connect('finance.db')
        df = pd.read_sql_query("SELECT * FROM transactions", conn)
        if not df.empty:
            st.write("سجل العمليات:", df)
            st.write("توزيع المصاريف حسب التصنيف:")
            fig, ax = plt.subplots()
            grouped = df.groupby('category')['amount'].sum()
            labels = [fix_arabic(cat) for cat in grouped.index]
            grouped.plot(kind='pie', labels=labels, autopct='%1.1f%%', ax=ax)
            ax.set_ylabel('')
            st.pyplot(fig)
        else:
            st.write("لا توجد بيانات بعد.")
        conn.close()
        
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.logged_in = False
        st.rerun()