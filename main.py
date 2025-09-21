from instagrapi import Client
import json
import random
import os
import warnings

from instagrapi.exceptions import TwoFactorRequired

warnings.filterwarnings("ignore", category=UserWarning)

with open("login_data.txt", "r") as file:
    USERNAME, PASSWORD = file.readline().strip().split()

print(USERNAME, PASSWORD)

SESSION_FILE = f"{USERNAME}_session"

# SHORTCODE = "DO0ZZDTjDst"
SHORTCODE = input("Enter shortcode for GIVEAWAY post: ")
#
# cl = Client()
#
# if os.path.exists(SESSION_FILE):
#     try:
#         cl.load_settings(SESSION_FILE)
#         cl.login(USERNAME, PASSWORD)  # will reuse session if possible
#         print("✅ Session loaded from file")
#     except Exception as e:
#         print("⚠ Session invalid or empty, logging in again:", e)
#         os.remove(SESSION_FILE)  # remove corrupted session
#
# # ---------- FRESH LOGIN ----------
# if not os.path.exists(SESSION_FILE):
#     try:
#         cl.login(USERNAME, PASSWORD)
#     except TwoFactorRequired:
#         code = input("Enter 2FA code from app/SMS: ")
#         cl.login(USERNAME, PASSWORD, verification_code=code)
#     cl.dump_settings(SESSION_FILE)
#     print("✅ New session saved")
#
# # ---------- FETCH POST INFO ----------
# url = f"https://www.instagram.com/p/{SHORTCODE}/"
# media_id = cl.media_id(cl.media_pk_from_url(url))
# media = cl.media_info(media_id)
#
# print(f"Likes: {media.like_count}")
# print(f"Comments count: {media.comment_count}")
# print("--- COMMENTS ---")
#
# # ---------- GET COMMENTS AND FOLLOWERS ----------
# comments = cl.media_comments(media_id)
#
# commenters = []
#
# # for c in comments:
# #     username = c.user.username
# #     text = c.text
# #
# #     try:
# #         user = cl.user_info_by_username(username)
# #         followers = user.follower_count
# #     except Exception as e:
# #         followers = "N/A"
# #
# #     print(f"{username} ({followers} followers): {text}")
# #     commenters.append(username)
# for comment in comments:
#     username = comment.user.username
#     try:
#         user_info = cl.user_info_by_username(username)
#         followers = user_info.follower_count
#     except Exception:
#         followers = "N/A"
#     print(f"{username} ({followers} followers): {comment.text}")
#
# # ---------- PICK RANDOM WINNER ----------
# winner = random.choice(commenters)
# print(f"\n🎉 Winner: {winner}")


cl = Client()

# ---------- LOAD SESSION ----------
if os.path.exists(SESSION_FILE):
    try:
        cl.load_settings(SESSION_FILE)
        cl.login(USERNAME, PASSWORD)  # reuse session
        print("✅ Session loaded from file")
    except Exception as e:
        print("⚠ Session invalid, logging in again:", e)
        os.remove(SESSION_FILE)

# ---------- FRESH LOGIN ----------
if not os.path.exists(SESSION_FILE):
    try:
        cl.login(USERNAME, PASSWORD)
    except TwoFactorRequired:
        code = input("Enter 2FA code from app/SMS: ")
        cl.login(USERNAME, PASSWORD, verification_code=code)
    cl.dump_settings(SESSION_FILE)
    print("✅ New session saved")

# ---------- FETCH POST ----------
url = f"https://www.instagram.com/p/{SHORTCODE}/"
media_id = cl.media_pk_from_url(url)
media = cl.media_info(media_id)

print(f"Likes: {media.like_count}")
print(f"Comments count: {media.comment_count}")
print("--- COMMENTS ---")

comments = cl.media_comments(media_id)

comments_data = []  # store results to print later

for comment in comments:
    username = comment.user.username
    try:
        user_info = cl.user_info_by_username(username)
        followers = user_info.follower_count
    except Exception:
        followers = "N/A"
    comments_data.append((username, followers, comment.text))

# ---------- PRINT RESULTS AT THE END ----------
print(f"\nLikes: {media.like_count}")
print(f"Comments count: {media.comment_count}")
print("--- COMMENTS ---")
for username, followers, text in comments_data:
    print(f"{username} ({followers} followers): {text}")

comments_json = []
for comment in comments_data:
    username = comment[0]
    followers = comment[1]
    text = comment[2]
    comments_json.append({
        "username": username,
        "followers": followers,
        "comment": text
    })

# Save to file
with open("comments_data.json", "w", encoding="utf-8") as f:
    json.dump(comments_json, f, ensure_ascii=False, indent=4)

print("✅ Comments data saved to comments_data.json")
