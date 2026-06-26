import streamlit as st
import secrets
import string
import math
import os
import time
import requests
import json
from streamlit_lottie import st_lottie


# --- Helper Functions ---
def load_css(file_name):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, file_name)
    try:
        with open(file_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass # Silently pass if CSS is missing so the app doesn't crash

def load_lottieurl(url: str):
    """Fetches a Lottie animation from a web URL."""
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None

def load_lottie_file(filepath: str):
    """Safely loads a local Lottie JSON file."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, filepath)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        # Catches the error if the file exists but is empty or invalid
        return None

def calculate_entropy(length: int, pool_size: int) -> float:
    """Calculates password strength in bits of entropy."""
    if pool_size == 0:
        return 0
    return length * math.log2(pool_size)

# --- App Configuration ---
st.set_page_config(page_title="Vault | Secure Generator", page_icon="🔐", layout="centered")
load_css("style.css")

# --- Load Animations (With Fallback Logic) ---
# 1. Try to load local files first
lottie_lock = load_lottie_file("lock.json")
lottie_success = load_lottie_file("success.json")

# 2. If local files are missing or empty (JSONDecodeError), fallback to URL
if not lottie_lock:
    lottie_lock = load_lottieurl("https://lottie.host/5a092c45-24e5-4224-b52e-ec5f97f75355/1oY7x44P9T.json")
if not lottie_success:
    lottie_success = load_lottieurl("https://lottie.host/808df04e-e47e-4dcb-947b-1d70a1cf6d18/sYwF2yLh6D.json")

# --- UI Header ---
col1, col2 = st.columns([1, 4])
with col1:
    if lottie_lock:
        st_lottie(lottie_lock, height=80, key="header_anim")
    else:
        st.markdown("<h1 style='text-align: center;'>🔐</h1>", unsafe_allow_html=True)
with col2:
    st.title("Vault Generator")
st.write("Generate cryptographically secure passwords with entropy analysis.")

# --- State Management ---
if "password" not in st.session_state:
    st.session_state.password = ""
if "entropy" not in st.session_state:
    st.session_state.entropy = 0

# --- Sidebar Configuration Form ---
st.sidebar.header("Security Parameters")
with st.sidebar.form("settings_form"):
    length = st.slider("Password Length", min_value=4, max_value=64, value=16, step=1)
    
    use_lower = st.checkbox("Lowercase (a-z)", value=True)
    use_upper = st.checkbox("Uppercase (A-Z)", value=True)
    use_digits = st.checkbox("Digits (0-9)", value=True)
    use_symbols = st.checkbox("Symbols (!@#$%^&*)", value=True)
    include_spaces = st.checkbox("Include spaces", value=False)
    
    submitted = st.form_submit_button("Generate Password", type="primary", use_container_width=True)

# --- Generation Logic ---
if submitted:
    symbol_chars = string.punctuation + " " if include_spaces else string.punctuation
    
    char_pools = []
    pool_size = 0
    
    if use_lower:
        char_pools.append(string.ascii_lowercase)
        pool_size += 26
    if use_upper:
        char_pools.append(string.ascii_uppercase)
        pool_size += 26
    if use_digits:
        char_pools.append(string.digits)
        pool_size += 10
    if use_symbols:
        char_pools.append(symbol_chars)
        pool_size += len(symbol_chars)

    if not char_pools:
        st.error("⚠️ You must select at least one character type.")
    elif length < len(char_pools):
        st.error("⚠️ Length is too small to include all selected character types.")
    else:
        # 1. Show processing animation
        with st.spinner("Cryptographically securing..."):
            time.sleep(0.5) # Micro-interaction pause for effect
            
            # 2. Build the password
            password_chars = [secrets.choice(pool) for pool in char_pools]
            remaining = length - len(password_chars)
            
            if remaining > 0:
                all_allowed_chars = "".join(char_pools)
                password_chars.extend(secrets.choice(all_allowed_chars) for _ in range(remaining))
            
            secrets.SystemRandom().shuffle(password_chars)
            final_password = "".join(password_chars)
            
            # 3. Save to state
            st.session_state.password = final_password
            st.session_state.entropy = calculate_entropy(length, pool_size)
            
            # 4. Trigger Success Toast
            st.toast("Secure token generated!", icon="✅")

# --- Main Display Area ---
st.write("---")

if st.session_state.password:
    st.subheader("Your Secure Token")
    
    # Display the password in the custom CSS code box
    st.code(st.session_state.password, language="text")
    
    # --- Entropy (Strength) Meter ---
    st.write("### Strength Analysis")
    entropy = st.session_state.entropy
    
    # Determine strength text and color
    if entropy < 50:
        strength, color = "Weak", "red"
        progress = 0.3
    elif entropy < 70:
        strength, color = "Moderate", "orange"
        progress = 0.6
    else:
        strength, color = "Strong", "green"
        progress = 1.0
        
    # Display the meter
    st.progress(progress)
    st.markdown(f"**Bits of Entropy:** `{round(entropy, 1)}` | **Status:** <span style='color:{color}; font-weight:bold;'>{strength}</span>", unsafe_allow_html=True)
    
    # Download Button
    st.write("")
    st.download_button(
        label="Download as .txt",
        data=st.session_state.password + "\n",
        file_name="secure_password.txt",
        mime="text/plain",
        use_container_width=True
    )
else:
    st.info("Configure your parameters in the sidebar and click **Generate Password** to begin.")
