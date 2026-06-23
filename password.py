import streamlit as st
import secrets
import string

st.set_page_config(page_title="Password Generator", page_icon="🔐", layout="centered")

st.title("🔐 Password Generator")

st.write("Generate strong, random passwords with configurable options.")

st.sidebar.header("Password Settings")
length = st.sidebar.slider("Length", min_value=6, max_value=64, value=16, step=1)

use_lower = st.sidebar.checkbox("Lowercase (a-z)", value=True)
use_upper = st.sidebar.checkbox("Uppercase (A-Z)", value=True)
use_digits = st.sidebar.checkbox("Digits (0-9)", value=True)
use_symbols = st.sidebar.checkbox("Symbols (!@#$%^&*)", value=True)

include_spaces = st.sidebar.checkbox("Include spaces (not recommended)", value=False)

if include_spaces:
    symbol_chars = string.punctuation + " "
else:
    symbol_chars = string.punctuation

char_pools = []
if use_lower:
    char_pools.append(string.ascii_lowercase)
if use_upper:
    char_pools.append(string.ascii_uppercase)
if use_digits:
    char_pools.append(string.digits)
if use_symbols:
    char_pools.append(symbol_chars)

if not char_pools:
    st.warning("Select at least one character type.")
    st.stop()


def generate_password(n: int) -> str:
    # Ensure at least one from each selected pool
    password_chars = [secrets.choice(pool) for pool in char_pools]
    remaining = n - len(password_chars)

    if remaining > 0:
        password_chars.extend(secrets.choice("".join(char_pools)) for _ in range(remaining))

    secrets.SystemRandom().shuffle(password_chars)
    return "".join(password_chars)


if "password" not in st.session_state:
    st.session_state.password = ""

col1, col2 = st.columns(2)
with col1:
    generate = st.button("Generate", type="primary")
with col2:
    st.caption("Tip: increase length for stronger passwords")

if generate:
    if length < len(char_pools):
        st.error("Length is too small for the selected character types.")
        st.stop()

    st.session_state.password = generate_password(length)

st.subheader("Generated Password")
st.code(st.session_state.password if st.session_state.password else "Click Generate to see password", language="text")

if st.session_state.password:
    st.download_button(
        label="Download as .txt",
        data=st.session_state.password + "\n",
        file_name="generated_password.txt",
        mime="text/plain",
    )
