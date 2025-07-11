import streamlit as st
import sqlite3
import os

# Database path for Streamlit Cloud
DB_PATH = os.path.join(os.path.dirname(__file__), 'socialmedia.db')
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Ensure tables exist
cur.executescript("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    email TEXT
);

CREATE TABLE IF NOT EXISTS posts (
    post_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    content TEXT,
    post_date TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS likes (
    like_id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER,
    FOREIGN KEY (post_id) REFERENCES posts(post_id)
);
""")
conn.commit()

# Page setup
st.set_page_config(page_title="Social App with Likes", layout="centered")
st.title("📱 Social Media App + ❤️ Likes")

# Load users
users = cur.execute("SELECT * FROM users").fetchall()

# Layout
tab1, tab2 = st.tabs(["📄 View Posts", "➕ Add Post"])

# ==== View Posts ====
with tab1:
    st.subheader("📝 Posts Feed")
    posts = cur.execute("""
        SELECT posts.post_id, posts.content, users.username, posts.post_date
        FROM posts JOIN users ON posts.user_id = users.user_id
        ORDER BY posts.post_date DESC
    """).fetchall()

    if not posts:
        st.info("No posts yet. Add one from the next tab.")
    else:
        for post_id, content, username, post_date in posts:
            st.markdown(f"""
<div style='padding: 10px; border-bottom: 1px solid #ccc;'>
    <b style='color:#1f77b4;'>{username}</b> said:<br>
    <p style='margin-top:5px;'>{content}</p>
    <small>🕒 {post_date}</small><br>
</div>
            """, unsafe_allow_html=True)

            like_count = cur.execute("SELECT COUNT(*) FROM likes WHERE post_id = ?", (post_id,)).fetchone()[0]
            if st.button(f"❤️ Like ({like_count})", key=f"like_{post_id}"):
                cur.execute("INSERT INTO likes (post_id) VALUES (?)", (post_id,))
                conn.commit()
                st.experimental_rerun()

# ==== Add Post ====
with tab2:
    st.subheader("➕ Create a New Post")

    if not users:
        st.warning("⚠️ No users found. Please add users to the database manually.")
    else:
        with st.form("post_form"):
            username = st.selectbox("Select a user", [u[1] for u in users])
            content = st.text_area("What's on your mind?")
            submitted = st.form_submit_button("Post")

            if submitted and content.strip():
                user_id = [u[0] for u in users if u[1] == username][0]
                cur.execute("INSERT INTO posts (user_id, content) VALUES (?, ?)", (user_id, content.strip()))
                conn.commit()
                st.success("✅ Post added!")
                st.experimental_rerun()
            elif submitted:
                st.error("Post cannot be empty!")

# Close DB
conn.close()
