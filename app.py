import streamlit as st
import sqlite3
import os

# Connect to database
DB_PATH = os.path.join(os.path.dirname(__file__), 'socialmedia.db')
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Ensure tables exist
cur.executescript("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS posts (
    post_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    content TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS likes (
    like_id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER,
    FOREIGN KEY(post_id) REFERENCES posts(post_id)
);
""")
conn.commit()

# Fetch users
users = cur.execute("SELECT user_id, username FROM users").fetchall()

st.title("📱 Social Media App + ❤️ Likes")

# Navigation
page = st.sidebar.radio("Navigate", ["View Posts", "Add Post"])

# View Posts Page
if page == "View Posts":
    st.subheader("📋 All Posts")
    posts = cur.execute("""
        SELECT posts.post_id, users.username, posts.content,
               COUNT(likes.like_id) as like_count
        FROM posts
        JOIN users ON posts.user_id = users.user_id
        LEFT JOIN likes ON posts.post_id = likes.post_id
        GROUP BY posts.post_id
        ORDER BY posts.post_id DESC
    """).fetchall()

    if not posts:
        st.info("No posts yet.")
    else:
        for post_id, username, content, like_count in posts:
            st.markdown(f"**{username}**: {content}")
            st.write(f"❤️ {like_count} likes")
            if st.button(f"Like ❤️", key=post_id):
                cur.execute("INSERT INTO likes (post_id) VALUES (?)", (post_id,))
                conn.commit()
                st.success("You liked this post!")
                st.rerun()

# Add Post Page
elif page == "Add Post":
    st.subheader("➕ Create a New Post")

    if not users:
        st.warning("⚠️ No users found. Please add users to the database manually.")
    else:
        with st.form("post_form"):
            user_options = {f"{u[1]} (ID: {u[0]})": u[0] for u in users}
            selected_user = st.selectbox("Select User", list(user_options.keys()))
            post_content = st.text_area("What's on your mind?")
            submitted = st.form_submit_button("Post")

            if submitted and post_content.strip():
                user_id = user_options[selected_user]
                cur.execute("INSERT INTO posts (user_id, content) VALUES (?, ?)", (user_id, post_content))
                conn.commit()
                st.success("✅ Post created successfully!")
                st.rerun()
