import html
import os
import streamlit as st
import pickle
import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from PIL import Image as PILImage
except ImportError:
    PILImage = None

st.set_page_config(
    page_title="Movie Recommendation",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Load 7.jpeg for full-page blurred background
import base64
_script_dir = os.path.dirname(os.path.abspath(__file__))
_bg_paths = [
    os.path.join(_script_dir, "assests", "7.jpeg"),
    os.path.join(_script_dir, "assests", "7.jpg.jpeg"),
]
_bg_b64 = ""
for _p in _bg_paths:
    if os.path.isfile(_p):
        with open(_p, "rb") as _f:
            _bg_b64 = "data:image/jpeg;base64," + base64.b64encode(_f.read()).decode()
        break
_bg_url = _bg_b64 or "none"

# Full-page blurred 7.jpeg (fixed div + gradient overlay)
st.markdown(
    '<style>#bg7{position:fixed;top:0;left:0;right:0;bottom:0;background-image:url("' + _bg_url + '");background-size:cover;background-position:center;filter:blur(12px);z-index:-2;}#bg7over{position:fixed;top:0;left:0;right:0;bottom:0;background:linear-gradient(135deg,rgba(26,10,46,0.55),rgba(45,27,78,0.55),rgba(193,168,242,0.55),rgba(226,113,157,0.55));z-index:-1;}</style>'
    '<div id="bg7"></div><div id="bg7over"></div>',
    unsafe_allow_html=True,
)

# CSS: single-page compact layout, creative boxes
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap');
    
    .stApp {
        background: transparent !important;
        font-family: 'Outfit', system-ui, sans-serif;
    }
    /* Hide Streamlit's top black bar (Deploy / header / toolbar) */
    header { display: none !important; }
    [data-testid="stHeader"] { display: none !important; }
    .stDeployButton { display: none !important; }
    #MainMenu { visibility: hidden !important; }
    #stDecoration { display: none !important; }
    footer { visibility: hidden !important; }
    .block-container, [data-testid="stVerticalBlock"] { position: relative; z-index: 1; }
    
    .main-header {
        text-align: center;
        padding: 0.8rem 0 0.4rem;
        margin-bottom: 0.3rem;
    }
    .main-header h1 {
        font-size: 3rem;
        font-weight: 800;
        color: #fff;
        margin: 0;
        letter-spacing: -0.02em;
        text-shadow: 0 0 20px rgba(255,255,255,0.3), 0 4px 8px rgba(0,0,0,0.3);
        transform: perspective(400px) rotateX(2deg);
        transition: transform 0.5s ease, text-shadow 0.5s ease;
        animation: titleFloat 5s ease-in-out infinite;
    }
    .main-header h1:hover {
        animation: none;
        transform: perspective(400px) rotateX(0deg) translateY(-3px);
        text-shadow: 0 0 28px rgba(255,255,255,0.4), 0 6px 12px rgba(0,0,0,0.25);
    }
    @keyframes titleFloat {
        0%, 100% { transform: perspective(400px) rotateX(2deg) translateY(0); }
        50% { transform: perspective(400px) rotateX(2deg) translateY(-6px); }
    }
    .main-header p {
        color: rgba(255,255,255,0.85);
        font-size: 0.95rem;
        margin: 0.5rem 0 0;
    }

    /* Movie-themed graphics (reused across the whole page) */
    .movie-hero-graphics, .movie-graphics {
        position: relative;
        min-height: 72px;
        margin-bottom: 0.6rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .movie-graphics--compact {
        min-height: 52px;
        margin-bottom: 0.5rem;
    }
    .movie-graphics--footer {
        min-height: 40px;
        margin-bottom: 0.4rem;
    }
    .movie-hero-graphics .film-strip, .movie-graphics .film-strip {
        position: absolute;
        left: 50%;
        transform: translateX(-50%);
        width: 90%;
        max-width: 420px;
        height: 24px;
        background: repeating-linear-gradient(
            90deg,
            rgba(0,0,0,0.5) 0px,
            rgba(0,0,0,0.5) 12px,
            transparent 12px,
            transparent 28px
        );
        border-radius: 4px;
        border: 2px solid rgba(255,255,255,0.25);
        animation: filmStripShine 3s ease-in-out infinite;
    }
    .movie-graphics--compact .film-strip, .movie-graphics--footer .film-strip {
        height: 16px;
        max-width: 320px;
    }
    .movie-graphics--footer .film-strip { height: 12px; max-width: 280px; }
    @keyframes filmStripShine {
        0%, 100% { opacity: 0.7; box-shadow: 0 0 12px rgba(255,255,255,0.1); }
        50% { opacity: 1; box-shadow: 0 0 20px rgba(255,255,255,0.2); }
    }
    .movie-hero-graphics .reel, .movie-graphics .reel {
        position: absolute;
        width: 44px;
        height: 44px;
        border: 4px solid rgba(255,255,255,0.5);
        border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, rgba(255,255,255,0.2), rgba(0,0,0,0.4));
        box-shadow: inset 0 0 12px rgba(0,0,0,0.4);
    }
    .movie-graphics--compact .reel, .movie-graphics--footer .reel {
        width: 32px;
        height: 32px;
        border-width: 3px;
    }
    .movie-graphics--footer .reel { display: none; }
    .movie-hero-graphics .reel::before, .movie-graphics .reel::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 14px;
        height: 14px;
        background: rgba(255,255,255,0.4);
        border-radius: 50%;
        border: 2px solid rgba(255,255,255,0.3);
    }
    .movie-graphics--compact .reel::before, .movie-graphics--footer .reel::before {
        width: 10px;
        height: 10px;
    }
    .movie-hero-graphics .reel-left, .movie-graphics .reel-left { left: 12%; top: 50%; transform: translateY(-50%); animation: reelSpin 4s linear infinite; }
    .movie-hero-graphics .reel-right, .movie-graphics .reel-right { right: 12%; left: auto; top: 50%; transform: translateY(-50%); animation: reelSpin 4s linear infinite reverse; }
    @keyframes reelSpin {
        from { transform: translateY(-50%) rotate(0deg); }
        to { transform: translateY(-50%) rotate(360deg); }
    }
    .movie-hero-graphics .star, .movie-graphics .star {
        position: absolute;
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        text-shadow: 0 0 8px rgba(255,193,7,0.6);
        animation: twinkle 2s ease-in-out infinite;
    }
    .movie-graphics--compact .star, .movie-graphics--footer .star { font-size: 0.9rem; }
    .movie-hero-graphics .star.s1, .movie-graphics .star.s1 { top: 8px; left: 22%; animation-delay: 0s; }
    .movie-hero-graphics .star.s2, .movie-graphics .star.s2 { top: 4px; left: 50%; animation-delay: 0.4s; }
    .movie-hero-graphics .star.s3, .movie-graphics .star.s3 { top: 12px; right: 22%; animation-delay: 0.8s; }
    .movie-hero-graphics .star.s4, .movie-graphics .star.s4 { top: 18px; left: 38%; animation-delay: 0.2s; }
    .movie-hero-graphics .star.s5, .movie-graphics .star.s5 { top: 6px; right: 35%; animation-delay: 0.6s; }
    .movie-graphics--compact .star.s1 { top: 4px; }
    .movie-graphics--compact .star.s4 { top: 12px; }
    .movie-graphics--footer .star.s2 { top: 2px; }
    .movie-graphics--footer .star.s4, .movie-graphics--footer .star.s5 { display: none; }
    @keyframes twinkle {
        0%, 100% { opacity: 0.5; transform: scale(0.9); }
        50% { opacity: 1; transform: scale(1.15); }
    }
    .movie-hero-graphics .clap, .movie-graphics .clap {
        position: absolute;
        font-size: 1.4rem;
        opacity: 0.6;
        animation: clapFloat 3s ease-in-out infinite;
    }
    .movie-graphics--compact .clap, .movie-graphics--footer .clap { font-size: 1.1rem; }
    .movie-graphics--footer .clap { display: none; }
    .movie-hero-graphics .clap.c1, .movie-graphics .clap.c1 { top: 20px; left: 18%; animation-delay: 0s; }
    .movie-hero-graphics .clap.c2, .movie-graphics .clap.c2 { top: 12px; right: 18%; animation-delay: 1.2s; }
    @keyframes clapFloat {
        0%, 100% { transform: translateY(0) rotate(-5deg); opacity: 0.5; }
        50% { transform: translateY(-6px) rotate(5deg); opacity: 0.75; }
    }
    /* Picker section: different animation – bouncing dots + sliding strip */
    .section-anim-picker { position: relative; min-height: 40px; margin-bottom: 0.5rem; display: flex; align-items: center; justify-content: center; }
    .section-anim-picker .strip-slide {
        position: absolute; left: 50%; transform: translateX(-50%);
        width: 80%; height: 10px;
        background: repeating-linear-gradient(90deg, rgba(0,0,0,0.35) 0px, rgba(0,0,0,0.35) 6px, transparent 6px, transparent 18px);
        border-radius: 3px;
        animation: stripSlide 4s linear infinite;
    }
    @keyframes stripSlide {
        0% { transform: translateX(calc(-50% + 0px)); }
        100% { transform: translateX(calc(-50% + 24px)); }
    }
    .section-anim-picker .dot { position: absolute; width: 8px; height: 8px; background: rgba(255,193,7,0.9); border-radius: 50%; animation: bounceDot 1.2s ease-in-out infinite; }
    .section-anim-picker .dot.d1 { left: 20%; top: 50%; margin-top: -4px; animation-delay: 0s; }
    .section-anim-picker .dot.d2 { left: 50%; top: 50%; margin-top: -4px; animation-delay: 0.2s; }
    .section-anim-picker .dot.d3 { right: 20%; left: auto; top: 50%; margin-top: -4px; animation-delay: 0.4s; }
    @keyframes bounceDot {
        0%, 100% { transform: translateY(0); opacity: 0.8; }
        50% { transform: translateY(-8px); opacity: 1; }
    }
    /* Hero posters section: reels + spotlight glow */
    .section-anim-hero .reel { animation: reelSpin 4s linear infinite; }
    .section-anim-hero .star { animation: starPulse 2.5s ease-in-out infinite; }
    .section-anim-hero .film-strip { animation: filmStripShine 3s ease-in-out infinite; }
    .section-anim-hero .glow-line {
        position: absolute; left: 0; top: 50%; width: 40%; height: 2px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
        animation: spotlightMove 3s ease-in-out infinite;
    }
    @keyframes starPulse {
        0%, 100% { opacity: 0.6; transform: scale(0.95); filter: brightness(0.9); }
        50% { opacity: 1; transform: scale(1.2); filter: brightness(1.2); }
    }
    @keyframes spotlightMove {
        0% { left: 0; opacity: 0.3; }
        50% { left: 60%; opacity: 0.8; }
        100% { left: 0; opacity: 0.3; }
    }
    /* Recs section: wave of stars + film edge */
    .section-anim-recs { position: relative; min-height: 44px; margin-bottom: 0.5rem; }
    .section-anim-recs .film-edge {
        position: absolute; left: 50%; transform: translateX(-50%); top: 0;
        width: 95%; height: 8px;
        background: repeating-linear-gradient(90deg, transparent 0px, transparent 10px, rgba(0,0,0,0.4) 10px, rgba(0,0,0,0.4) 14px);
        border-radius: 2px;
        animation: edgeShine 2s ease-in-out infinite;
    }
    @keyframes edgeShine {
        0%, 100% { opacity: 0.6; }
        50% { opacity: 1; }
    }
    .section-anim-recs .star { animation: starWave 1.8s ease-in-out infinite; }
    .section-anim-recs .star.s1 { animation-delay: 0s; }
    .section-anim-recs .star.s2 { animation-delay: 0.25s; }
    .section-anim-recs .star.s3 { animation-delay: 0.5s; }
    @keyframes starWave {
        0%, 100% { transform: scale(0.85); opacity: 0.5; }
        50% { transform: scale(1.25); opacity: 1; }
    }
    .hero-box {
        background: linear-gradient(145deg, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0.05) 100%);
        border: 2px solid rgba(255,255,255,0.6);
        border-radius: 20px;
        padding: 0.8rem 1rem;
        margin: 0.5rem 0 0.8rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.2);
    }
    
    .picker-box {
        background: linear-gradient(145deg, rgba(255,107,107,0.2) 0%, rgba(255,193,7,0.15) 50%, rgba(0,229,255,0.15) 100%);
        border: 2px solid rgba(255,255,255,0.5);
        border-radius: 16px;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0 0.8rem;
        box-shadow: 0 8px 24px rgba(0,0,0,0.25), 0 12px 32px rgba(0,0,0,0.15);
        transform: perspective(600px) translateZ(0);
        transition: transform 0.4s ease, box-shadow 0.4s ease;
    }
    .picker-box:hover {
        transform: perspective(600px) translateZ(8px);
        box-shadow: 0 12px 32px rgba(0,0,0,0.3), 0 20px 48px rgba(0,0,0,0.2);
    }
    
    .picker-row label {
        color: rgba(255,255,255,0.95) !important;
        font-weight: 600 !important;
    }
    div[data-testid="stSelectbox"] > div {
        background: rgba(255,255,255,0.1) !important;
        border-radius: 12px !important;
        border: 2px solid rgba(255,255,255,0.3) !important;
    }
    div[data-testid="stSelectbox"] input {
        color: #fff !important;
    }
    
    .stButton > button {
        width: 100%;
        padding: 0.7rem 1rem !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        background: linear-gradient(135deg, #27eae7 0%, #646dc4 100%) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 12px !important;
        cursor: pointer;
        transition: transform 0.25s ease, box-shadow 0.25s ease !important;
        transform: perspective(300px) translateZ(0);
    }
    .stButton > button:hover {
        transform: perspective(300px) rotateX(-8deg) translateY(-4px) translateZ(8px) !important;
        box-shadow: 0 12px 36px rgba(39,234,231,0.5), 0 6px 16px rgba(0,0,0,0.2) !important;
    }
    .stButton > button:active {
        transform: perspective(300px) rotateX(0deg) translateY(0) scale(0.98) !important;
    }
    
    .recs-box {
        background: linear-gradient(145deg, rgba(0,229,255,0.15) 0%, rgba(255,107,107,0.1) 100%);
        border: 2px solid rgba(255,255,255,0.4);
        border-radius: 16px;
        padding: 1rem;
        margin: 0.5rem 0 0;
        box-shadow: 0 8px 24px rgba(0,0,0,0.2), 0 16px 40px rgba(0,0,0,0.12);
        transform: perspective(800px) translateZ(0);
        transition: transform 0.4s ease, box-shadow 0.4s ease;
    }
    .recs-box:hover {
        transform: perspective(800px) translateZ(6px);
        box-shadow: 0 12px 32px rgba(0,0,0,0.25), 0 24px 56px rgba(0,0,0,0.15);
    }
    .recs-header {
        color: #fff;
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 0.8rem;
        text-shadow: 0 0 12px rgba(255,255,255,0.4);
    }
    .movie-card {
        background: linear-gradient(145deg, rgba(255,255,255,0.12) 0%, rgba(255,255,255,0.04) 100%);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.25);
        border-radius: 14px;
        padding: 0.6rem;
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transform: perspective(700px) rotateX(0deg) rotateY(0deg) scale(1) translateZ(0);
    }
    .movie-card:hover {
        transform: perspective(700px) rotateX(-8deg) rotateY(3deg) scale(1.04) translateY(-8px) translateZ(12px);
        border-color: rgba(255,255,255,0.4);
        box-shadow: 0 20px 40px rgba(0,0,0,0.35), 0 12px 30px rgba(0,229,255,0.25);
    }
    .movie-card img {
        border-radius: 10px;
        width: 100%;
        display: block;
    }
    .movie-card .title {
        color: #fff;
        font-weight: 600;
        font-size: 0.85rem;
        margin-top: 0.5rem;
        line-height: 1.3;
    }
    .movie-card .rating {
        color: rgba(255,193,7,0.95);
        font-size: 0.8rem;
        margin-top: 0.35rem;
        font-weight: 500;
    }
    
    [data-testid="stVerticalBlock"] > div { padding: 0.2rem 0 !important; }
    .block-container { padding-top: 5rem !important; padding-bottom: 1rem !important; max-width: 100% !important; }
    
    .nav-header {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 999;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.6rem 1.5rem;
        background: linear-gradient(90deg, #d34397 0%, #e21433 100%);
        border-bottom: 2px solid rgba(255,255,255,0.25);
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    .nav-header a {
        color: #fff;
        text-decoration: none;
        font-weight: 600;
        padding: 0.4rem 0.8rem;
        border-radius: 8px;
        transition: all 0.2s;
    }
    .nav-header a:hover {
        background: rgba(255,255,255,0.2);
        transform: translateY(-1px);
    }
    .nav-links { display: flex; gap: 0.5rem; align-items: center; }
    .nav-logo { font-size: 1.2rem; font-weight: 700; display: inline-flex; align-items: center; gap: 0.5rem; }
    .nav-logo-img { height: 36px; width: auto; vertical-align: middle; object-fit: contain; }
    
    .app-footer {
        margin-top: 2.8rem;
        padding: 1rem 1.5rem;
        background: linear-gradient(90deg, #d34397 0%, #e21433 100%);
        border-top: 2px solid rgba(255,255,255,0.25);
        border-radius: 16px 16px 0 0;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        box-shadow: 0 -4px 20px rgba(0,0,0,0.2);
    }
    .footer-links { display: flex; gap: 1rem; flex-wrap: wrap; }
    .footer-links a {
        color: rgba(255,255,255,0.95);
        text-decoration: none;
        font-size: 0.9rem;
        transition: color 0.2s;
    }
    .footer-links a:hover { color: #fff; }
    .footer-copy { color: rgba(255,255,255,0.85); font-size: 0.85rem; }
    .back-top {
        padding: 0.5rem 1rem;
        background: rgba(255,255,255,0.25);
        color: #fff !important;
        border: 1px solid rgba(255,255,255,0.5);
        border-radius: 10px;
        font-weight: 600;
        cursor: pointer;
        transition: transform 0.2s, box-shadow 0.2s, background 0.2s;
    }
    .back-top:hover {
        transform: translateY(-2px);
        background: rgba(255,255,255,0.35);
        box-shadow: 0 4px 16px rgba(0,0,0,0.2);
    }

    /* Hero posters: alternating big/small + effects (this section only) */
    .hero-box .hero-posters {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        flex-wrap: wrap;
        padding: 0.4rem 0;
    }
    .hero-box .hero-poster {
        border-radius: 14px;
        overflow: hidden;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.2);
        box-shadow: 0 8px 24px rgba(0,0,0,0.35);
        transition: transform 0.3s ease, box-shadow 0.3s ease, filter 0.3s ease;
        flex-shrink: 0;
        transform: perspective(800px) rotateY(0deg) rotateX(0deg) translateZ(0);
    }
    .hero-box .hero-poster.hero-poster-big {
        width: 200px;
        max-width: 28vw;
    }
    .hero-box .hero-poster.hero-poster-small {
        width: 130px;
        max-width: 18vw;
    }
    .hero-box .hero-poster img {
        display: block;
        width: 100%;
        height: auto;
        vertical-align: middle;
    }
    .hero-box .hero-poster:hover {
        transform: perspective(800px) rotateY(-8deg) rotateX(5deg) translateZ(20px) scale(1.05);
        box-shadow: 0 20px 48px rgba(0,0,0,0.45), 0 0 28px rgba(39,234,231,0.3);
        filter: brightness(1.08);
    }
    .hero-box .hero-poster.hero-poster-big:hover {
        box-shadow: 0 24px 52px rgba(0,0,0,0.4), 0 0 32px rgba(226,113,157,0.25);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Load logo for navbar (your custom image)
_logo_path = os.path.join(_script_dir, "assests", "ChatGPT Image Mar 10, 2026, 11_46_40 PM.png")
_nav_logo_html = ""
if os.path.isfile(_logo_path):
    try:
        with open(_logo_path, "rb") as _f:
            _logo_b64 = base64.b64encode(_f.read()).decode()
        _nav_logo_html = f'<img src="data:image/png;base64,{_logo_b64}" alt="Logo" class="nav-logo-img" />'
    except Exception:
        _nav_logo_html = "🎬"
else:
    _nav_logo_html = "🎬"

# Interactive header (sticky nav)
st.markdown(
    f"""
    <div class="nav-header" id="top">
        <a href="#top" class="nav-logo">{_nav_logo_html}</a>
        <div class="nav-links">
            <a href="#top">Home</a>
            <a href="#picker-section">Pick Movie</a>
            <a href="#recs-section">Recommendations</a>
        </div>
    </div>
    <div class="main-header">
        <div class="movie-hero-graphics">
            <div class="film-strip"></div>
            <div class="reel reel-left"></div>
            <div class="reel reel-right"></div>
            <span class="star s1">★</span>
            <span class="star s2">★</span>
            <span class="star s3">★</span>
            <span class="star s4">★</span>
            <span class="star s5">★</span>
            <span class="clap c1">🎬</span>
            <span class="clap c2">🎬</span>
        </div>
        <h1>{_nav_logo_html} Movie Recommendation</h1>
        <p>Pick a movie you liked and discover similar ones</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Section-specific animation HTML (each section has a different look)
PICKER_ANIM_HTML = """
<div class="section-anim-picker">
    <div class="strip-slide"></div>
    <div class="dot d1"></div><div class="dot d2"></div><div class="dot d3"></div>
</div>
"""
HERO_BOX_ANIM_HTML = """
<div class="movie-graphics movie-graphics--compact section-anim-hero">
    <div class="glow-line"></div>
    <div class="film-strip"></div>
    <div class="reel reel-left"></div>
    <div class="reel reel-right"></div>
    <span class="star s1">★</span><span class="star s2">★</span><span class="star s3">★</span>
    <span class="star s4">★</span><span class="star s5">★</span>
    <span class="clap c1">🎬</span><span class="clap c2">🎬</span>
</div>
"""
RECS_ANIM_HTML = """
<div class="section-anim-recs movie-graphics movie-graphics--compact">
    <div class="film-edge"></div>
    <span class="star s1">★</span><span class="star s2">★</span><span class="star s3">★</span>
</div>
"""

movies_dict = pickle.load(open("Movie_dict.pkl", "rb"))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open("Similarity.pkl", "rb"))
movie_list = movies["title"].values

# Picker section FIRST (visible on page load, no scrolling needed)
st.markdown(
    '<div class="picker-box" id="picker-section">' + PICKER_ANIM_HTML + '<div class="picker-row">',
    unsafe_allow_html=True,
)
col_sel, col_opts, col_btn = st.columns([2, 1, 1])
with col_sel:
    selected_movie = st.selectbox(
        "Type or select a movie",
        movie_list,
        key="movie_select",
    )
with col_opts:
    num_recs = st.selectbox(
        "How many?",
        [5, 10],
        index=0,
        key="num_recs",
    )
with col_btn:
    st.write("")
    show_clicked = st.button("Show Recommendations", key="rec_btn")
st.markdown("</div></div>", unsafe_allow_html=True)

# Hero images below picker: 3 big, 3 small (alternating) with effects
_script_dir = os.path.dirname(os.path.abspath(__file__))
assets_dir = os.path.join(_script_dir, "assests")
hero_images = []
if os.path.isdir(assets_dir):
    for name in os.listdir(assets_dir):
        lower = name.lower()
        if lower.endswith((".jpg", ".jpeg", ".png")):
            hero_images.append(os.path.join(assets_dir, name))
    hero_images = sorted(hero_images)[:6]

def _hero_img_mime(path):
    lower = path.lower()
    if lower.endswith(".png"):
        return "image/png"
    return "image/jpeg"

if hero_images:
    parts = ['<div class="hero-box">' + HERO_BOX_ANIM_HTML + '<div class="hero-posters">']
    for i, path in enumerate(hero_images):
        size_class = "hero-poster-big" if (i % 2 == 0) else "hero-poster-small"
        try:
            with open(path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            mime = _hero_img_mime(path)
            src = f"data:{mime};base64,{b64}"
            safe_src = html.escape(src)
            parts.append(f'<div class="hero-poster {size_class}"><img src="{safe_src}" alt="Poster {i+1}"></div>')
        except Exception:
            parts.append(f'<div class="hero-poster {size_class}"><img src="https://via.placeholder.com/200x300/2d1b4e/eee?text=Poster" alt="Poster"></div>')
    parts.append("</div></div>")
    st.markdown("".join(parts), unsafe_allow_html=True)


@st.cache_data(ttl=86400)
def fetch_poster_and_rating(movie_id):
    """Fetch poster URL and rating from TMDB; cached for 24h. Returns (poster_url, rating)."""
    default_poster = "https://via.placeholder.com/200x300/1a1a2e/eee?text=No+Poster"
    try:
        url = "https://api.themoviedb.org/3/movie/{}?api_key=dbe0e7a31304c13546ad62b24da61f45&language=en-US".format(
            movie_id
        )
        data = requests.get(url, timeout=5).json()
        poster_path = data.get("poster_path")
        poster_url = ("https://image.tmdb.org/t/p/w500/" + poster_path) if poster_path else default_poster
        rating = data.get("vote_average")  # 0–10 scale from TMDB
        rating_str = f"{rating:.1f}" if rating is not None else "—"
        return (poster_url, rating_str)
    except Exception:
        pass
    return (default_poster, "—")


def recommend(movie, count=5):
    index = movies[movies["title"] == movie].index[0]
    distances = sorted(
        list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1]
    )
    names, poster_ids = [], []
    n = min(count, len(distances) - 1)
    for i in distances[1 : 1 + n]:
        poster_ids.append(movies.iloc[i[0]].movie_id)
        names.append(movies.iloc[i[0]].title)
    # Fetch poster + rating for each movie in parallel (same API call)
    with ThreadPoolExecutor(max_workers=min(10, n)) as executor:
        results = list(executor.map(fetch_poster_and_rating, poster_ids))
    posters = [r[0] for r in results]
    ratings = [r[1] for r in results]
    return names, posters, ratings


if show_clicked:
    names, posters, ratings = recommend(selected_movie, count=num_recs)
    st.session_state["rec_names"] = names
    st.session_state["rec_posters"] = posters
    st.session_state["rec_ratings"] = ratings
    st.session_state["scroll_to_recs"] = True

if "rec_names" in st.session_state and "rec_posters" in st.session_state:
    names = st.session_state["rec_names"]
    posters = st.session_state["rec_posters"]
    ratings = st.session_state.get("rec_ratings", ["—"] * len(names))
    n = len(names)

    st.markdown(
        '<div class="recs-box" id="recs-section">'
        + RECS_ANIM_HTML
        + '<p class="recs-header">Recommended for you</p>',
        unsafe_allow_html=True,
    )
    cols_per_row = 5
    for start in range(0, n, cols_per_row):
        row_cols = st.columns(cols_per_row)
        for j, col in enumerate(row_cols):
            i = start + j
            if i >= n:
                break
            with col:
                safe_name = html.escape(names[i])
                safe_url = html.escape(posters[i])
                rating = ratings[i] if i < len(ratings) else "—"
                safe_rating = html.escape(str(rating))
                rating_text = f"★ {safe_rating}/10" if rating != "—" else "★ —"
                st.markdown(
                    f'<div class="movie-card">'
                    f'<img src="{safe_url}" alt="{safe_name}" style="width:100%;border-radius:10px;">'
                    f'<p class="title">{safe_name}</p>'
                    f'<p class="rating">{rating_text}</p></div>',
                    unsafe_allow_html=True,
                )
    st.markdown("</div>", unsafe_allow_html=True)

    # Auto-scroll to "Recommended for you" after section is rendered
    if st.session_state.get("scroll_to_recs"):
        st.session_state["scroll_to_recs"] = False
        st.components.v1.html(
            """
            <script>
            (function() {
                function scroll() {
                    try {
                        var doc = window.parent.document;
                        var el = doc.getElementById('recs-section');
                        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    } catch (e) {}
                }
                setTimeout(scroll, 100);
            })();
            </script>
            """,
            height=0,
        )

# Interactive footer (simple structure, no extra divs)
st.markdown(
    """
    <div class="app-footer">
        <div class="footer-links">
            <a href="#top">Back to top</a>
            <a href="#picker-section">Pick a movie</a>
            <a href="#recs-section">See recommendations</a>
        </div>
        <span class="footer-copy">© Movie Recommendation · Discover similar films</span>
        <a href="#top" class="back-top">↑ Back to top</a>
    </div>
    """,
    unsafe_allow_html=True,
)
