import streamlit as st
from groq import Groq
from PIL import Image
import io
import base64

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Fashionable India ✨",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  CUSTOM CSS — Luxury Indian Fashion Aesthetic
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;800&family=DM+Sans:wght@300;400;500&display=swap');

/* Global */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #fdfaf7;
    color: #1a1208;
}

/* Header */
.main-header {
    font-family: 'Playfair Display', serif;
    font-size: 3.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #D4AF37, #FF6B6B, #C84B31);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    padding: 1rem 0 0.2rem;
}

.tagline {
    text-align: center;
    color: #8a6040;
    font-size: 1rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 2rem;
}

/* Cards */
.style-card {
    background: linear-gradient(145deg, #fff8f2, #fef3e8);
    border: 1px solid #e8d5c0;
    border-radius: 16px;
    padding: 1.5rem;
    margin: 1rem 0;
}

/* Result sections */
.result-section {
    background: linear-gradient(135deg, #fff8f2, #fef5ec);
    border-left: 4px solid #D4AF37;
    border-radius: 0 12px 12px 0;
    padding: 1.2rem 1.5rem;
    margin: 0.8rem 0;
}

.result-section h4 {
    color: #D4AF37;
    font-family: 'Playfair Display', serif;
    margin-bottom: 0.5rem;
}

/* Shop button */
.shop-btn {
    display: inline-block;
    background: linear-gradient(135deg, #D4AF37, #C84B31);
    color: white !important;
    padding: 0.5rem 1.2rem;
    border-radius: 25px;
    font-size: 0.85rem;
    font-weight: 500;
    margin: 0.3rem 0.3rem 0.3rem 0;
    text-decoration: none !important;
    cursor: pointer;
}

/* Sidebar */
.css-1d391kg { background: #fdf5ec !important; }

/* Divider */
hr { border-color: #e8d5c0 !important; }

/* Streamlit overrides */
.stButton>button {
    background: linear-gradient(135deg, #D4AF37, #C84B31);
    color: white;
    border: none;
    border-radius: 25px;
    padding: 0.6rem 2rem;
    font-size: 1rem;
    font-weight: 600;
    width: 100%;
    transition: opacity 0.2s;
}
.stButton>button:hover { opacity: 0.85; }

.stSelectbox label, .stRadio label, .stSlider label {
    color: #c8a882 !important;
}

.stTextArea textarea {
    background: #fff8f2 !important;
    color: #1a1208 !important;
    border-color: #e8d5c0 !important;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  AFFILIATE LINKS DATABASE
# ─────────────────────────────────────────────
AFFILIATE_LINKS = {
    "Myntra": "https://www.myntra.com/search?rawQuery=",
    "Ajio":   "https://www.ajio.com/search/?text=",
    "Meesho": "https://meesho.com/search?q=",
    "Nykaa":  "https://www.nykaa.com/search/result/?q=",
    "Flipkart":"https://www.flipkart.com/search?q=",
}

def make_search_link(platform: str, query: str) -> str:
    """Generate affiliate-style search URL."""
    base = AFFILIATE_LINKS.get(platform, "https://www.google.com/search?q=")
    return base + query.replace(" ", "+")


# ─────────────────────────────────────────────
#  GEMINI AI CALL
# ─────────────────────────────────────────────
SYSTEM_PROMPT = """
You are India's most premium AI Personal Stylist for "Fashionable India".
Motto: "Everyone can be a stylist in their own way."

CRITICAL RULES — MUST FOLLOW:
1. Never body-shame. Use: curvy/athletic/slender instead of fat/skinny.
2. LANGUAGE RULE — EXTREMELY IMPORTANT:
   - If Language = "Hinglish 🇮🇳": Reply in pure Hinglish (Hindi in English alphabet + English words mixed naturally). Sound like a desi best friend. Example: "Yaar, ye navy blue blazer tumpe ekdum suit karega!"
   - If Language = "English 🇬🇧": Reply in clean, professional yet warm English ONLY. No Hindi words at all. Sound like a luxury fashion consultant. Example: "This navy blue blazer will complement your frame beautifully!"
3. Account for Indian weather & middle-class budgets.
4. GENDER RULE — EXTREMELY IMPORTANT:
   - If Gender = Male: ONLY suggest men's products. Never suggest women's clothing.
   - If Gender = Female: ONLY suggest women's products. Never suggest men's clothing.
   - If Gender = Other: Ask preference or suggest unisex styles.
5. UNIQUENESS RULE: Every recommendation must be 100% unique to THIS person's exact profile.
   Never give generic suggestions. Always mention the person's specific body type, skin tone in suggestions.
6. PRODUCT SPECIFICITY RULE: 
   - Always include EXACT size fit (slim-fit, regular-fit, oversized)
   - Always include EXACT color that suits their skin tone
   - Always include SPECIFIC Indian brand names
   - Budget-appropriate brands only

USER PROFILE:
{profile}

STYLING ENGINE:
[FOR MALE]
- Inverted Triangle: Slim-fit tops, tapered trousers, V-neck tees
- Rectangle: Padded blazers, layered looks, structured jackets  
- Oval/Round (Curvy): Dark verticals, straight-fit, avoid tight tees
- Triangle (Narrow shoulders): Broad collars, padded shoulders, horizontal stripes on top

[FOR FEMALE]
- Pear (Heavy bottom): Boat necks, A-line kurtis, dark bottoms, statement necklaces
- Apple (Heavy mid): Empire waist, flowy georgette/chiffon, V-necks
- Rectangle: Peplum tops, belts, fit-and-flare
- Inverted Triangle: Wide-leg pants, palazzos, A-line skirts

[SKIN TONE COLORS]
- Fair: Jewel tones, Navy, Burgundy, Emerald
- Wheatish: Mustard, Rust, Olive Green, Earthy Browns
- Dusky: Peach, Mint, Maroon, Bright colors, Gold
- Very Dark: Bright Orange, Hot Pink, Royal Blue, White

[INDIAN BRANDS BY BUDGET]
- Under ₹500: Meesho brands, Bewakoof, Campus Sutra
- ₹500-1500: H&M, Roadster (Myntra), Mast & Harbour, HRX
- ₹1500-3000: Jack & Jones, Only, Vero Moda, W for Women
- ₹3000-6000: Tommy Hilfiger, U.S. Polo, Van Heusen
- ₹6000+: Zara, Marks & Spencer, AND, Global Desi

RESPOND IN EXACTLY THIS 5-PART STRUCTURE:

1. 🌟 Style Breakdown:
[Address them personally. Mention their SPECIFIC body type + skin tone. Be warm like a celebrity stylist who knows them personally. 3-4 lines.]

2. 👕 Perfect Fit:
[Give SPECIFIC silhouettes for tops + bottoms + ethnic wear. Mention exact colors that suit THEIR skin tone. 4-5 lines.]

3. ✨ Pro Style Hack:
[ONE ultra-specific clever trick for THEIR body type. Make it feel like insider celebrity stylist knowledge. 2-3 lines.]

4. ✂️ Grooming Touch:
[For Male: specific hairstyle + beard style for their face shape.
For Female: specific makeup tone + one skincare tip for Indian skin.
2-3 lines.]

5. 🛍️ Shopping List:
[CRITICAL: Match EXACT gender. Use their EXACT budget. Make search terms VERY specific.]
Item 1 (Clothing): [Myntra/Ajio/Meesho] -> Search: "[Gender-correct Brand] [Exact Color] [Exact Fit] [Clothing Type]"
Item 2 (Clothing): [Myntra/Ajio/Meesho] -> Search: "[Gender-correct Brand] [Pattern/Style] [Clothing Type]"  
Item 3 (Grooming): [Nykaa/Flipkart] -> Search: "[Brand] [Exact Product Name for their skin concern]"

TONE: Sound like a mix of a best friend + luxury celebrity stylist. Personal, warm, professional. Never robotic or generic.
"""

def get_styling_advice(profile: dict, api_key: str, image=None) -> str:
    client = Groq(api_key=api_key)

    profile_text = "\n".join([f"- {k}: {v}" for k, v in profile.items()])
    prompt = SYSTEM_PROMPT.replace("{profile}", profile_text)

    messages = [{"role": "user", "content": prompt}]

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=1500,
    )

    return response.choices[0].message.content


# ─────────────────────────────────────────────
#  PARSE SHOPPING LIST — extract platform+query
# ─────────────────────────────────────────────
import re

def parse_shopping_items(text: str):
    """Extract shopping items from AI response."""
    items = []
    pattern = r'Item \d+.*?:\s*\[?(Myntra|Ajio|Meesho|Nykaa|Flipkart)\]?.*?Search[:\s]+"?([^"\n]+)"?'
    matches = re.findall(pattern, text, re.IGNORECASE)
    for platform, query in matches:
        items.append({
            "platform": platform.strip(),
            "query": query.strip(),
            "url": make_search_link(platform.strip(), query.strip())
        })
    return items


# ─────────────────────────────────────────────
#  MAIN APP UI
# ─────────────────────────────────────────────
def main():

    # ── Header ──
    st.markdown('<div class="main-header">✨ Fashionable India</div>', unsafe_allow_html=True)
    st.markdown('<div class="tagline">Everyone Can Be A Stylist In Their Own Way</div>', unsafe_allow_html=True)
    st.markdown("---")

    # ── Sidebar — API Key ──
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        api_key = st.secrets.get("GROQ_API_KEY", "") or st.text_input("🔑 Groq API Key", type="password",
                                help="Get free key at aistudio.google.com")
        st.markdown("---")
        st.markdown("### 📸 Upload Photo (Optional)")
        uploaded_img = st.file_uploader("Apni photo upload karo", type=["jpg", "jpeg", "png"])
        st.markdown("---")
        st.markdown("### 🌐 Language / Bhasha")
        language = st.radio("Choose your language:", 
            ["Hinglish 🇮🇳", "English 🇬🇧"], 
            horizontal=True)
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.caption("Fashionable India uses AI to give personalized fashion advice for every Indian body type, skin tone & budget.")

    # ── Main Form ──
    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.markdown("### 👤 Apne Baare Mein Batao")

        gender = st.radio("Gender", ["Male", "Female", "Other"], horizontal=True)

        skin_tone = st.selectbox("Skin Tone",
            ["Fair (Gora)", "Wheatish (Gehuniya)", "Dusky (Saanwla)", "Very Dark"])

        height = st.select_slider("Height",
            options=["Very Short (<5'2\")", "Short (5'2\"–5'5\")",
                     "Medium (5'5\"–5'8\")", "Tall (5'8\"–5'11\")", "Very Tall (>5'11\")"],
            value="Medium (5'5\"–5'8\")")

        body_type_options = {
            "Male":   ["Inverted Triangle (Broad Shoulders)", "Rectangle (Athletic)", 
                       "Oval/Round (Curvy Mid)", "Triangle (Narrow Shoulders)"],
            "Female": ["Pear (Heavy Bottom)", "Apple (Heavy Mid)", 
                       "Rectangle (Straight)", "Inverted Triangle (Broad Shoulders)"],
            "Other":  ["Slender", "Athletic", "Curvy", "Plus Size"]
        }
        body_type = st.selectbox("Body Type / Shape", body_type_options.get(gender, body_type_options["Other"]))

        occasion = st.multiselect("Occasion (Multiple select kar sakte ho)",
            ["Daily Office", "Casual Outings", "College", "Wedding/Shaadi",
             "Festive/Pooja", "Date Night", "Sports/Gym"],
            default=["Daily Office"])

        budget = st.select_slider("Budget Range",
            options=["Under ₹500", "₹500–1,500", "₹1,500–3,000", "₹3,000–6,000", "₹6,000+"],
            value="₹500–1,500")

        city_type = st.radio("City Type (Weather ke liye)", 
            ["North India (Hot & Cold)", "South India (Hot & Humid)",
             "Coastal (Humid)", "Hill Station (Cold)"],
            horizontal=False)

        extra_notes = st.text_area("Kuch aur batana hai? (Optional)",
            placeholder="e.g., Mujhe traditional wear pasand nahi, ya mera office formal dress code hai...")

    with col2:
        st.markdown("### 🎯 Style Preview")
        if uploaded_img:
            img = Image.open(uploaded_img)
            st.image(img, caption="Tumhari photo 📸", use_column_width=True)
            st.success("✅ Photo upload ho gayi! AI isko bhi analyze karega.")
        else:
            st.markdown("""
            <div class="style-card" style="text-align:center; padding:3rem 1rem;">
                <div style="font-size:4rem">👗</div>
                <p style="color:#8a6040; margin-top:1rem">
                    Photo upload karo ya sirf form bhar ke<br>personalized style advice pao!
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("### 💡 Aaj Ka Style Tip")
        tips = [
            "🌈 Monochromatic outfits instantly make you look taller & slimmer!",
            "👟 White sneakers almost every outfit ke saath kaam karte hain.",
            "🎽 Tucked-in shirt always more polished lagta hai untucked se.",
            "🧣 Ek statement accessory — poora look change kar deta hai!"
        ]
        import random
        st.info(random.choice(tips))

    # ── Generate Button ──
    st.markdown("---")
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        generate = st.button("✨ Mera Style Banao!")

    # ── Results ──
    if generate:
        if not api_key:
            st.error("⚠️ Pehle sidebar mein Groq API Key daalo!")
            return
        # Clear previous results for fresh recommendation
        if 'last_profile' in st.session_state:
            del st.session_state['last_profile']

        profile = {
            "Gender": gender,
            "Skin Tone": skin_tone,
            "Height": height,
            "Body Type": body_type,
            "Occasion": ", ".join(occasion) if occasion else "Casual",
            "Budget": budget,
            "City/Weather": city_type,
            "Extra Notes": extra_notes or "None",
            "Language": language,
        }

        with st.spinner("🪡 Aapka personalized style teyaar ho raha hai..."):
            try:
                image = Image.open(uploaded_img) if uploaded_img else None
                result = get_styling_advice(profile, api_key, image)

                # ── Display Results ──
                st.markdown("---")
                st.markdown("## 🎨 Aapka Personal Style Report")

                # Split sections by emoji headers
                sections = re.split(r'(?=\d+\.\s[🌟👕✨✂️🛍️])', result)

                for section in sections:
                    if not section.strip():
                        continue
                    st.markdown(f"""
                    <div class="result-section">
                        {section.strip().replace(chr(10), '<br>')}
                    </div>
                    """, unsafe_allow_html=True)

                # ── Clickable Shopping Buttons ──
                items = parse_shopping_items(result)
                if items:
                    st.markdown("---")
                    st.markdown("### 🛒 Direct Shopping Links")
                    cols = st.columns(len(items))
                    for i, item in enumerate(items):
                        with cols[i]:
                            st.markdown(f"""
                            <a href="{item['url']}" target="_blank">
                                <div class="shop-btn">
                                    🛍️ {item['platform']}<br>
                                    <small>{item['query'][:30]}...</small>
                                </div>
                            </a>
                            """, unsafe_allow_html=True)

                # ── Share / Save ──
                st.markdown("---")
                st.download_button(
                    label="📥 Style Report Download Karo",
                    data=result,
                    file_name="my_fashionable_india_style.txt",
                    mime="text/plain"
                )

            except Exception as e:
                st.error(f"❌ Kuch error aa gaya: {str(e)}\n\nAPI key check karo aur dobara try karo!")

    # ── Footer ──
    st.markdown("---")
    st.markdown("""
    <div style='text-align:center; color:#8a6040; font-size:0.8rem; padding:1rem'>
        Made with ❤️ for India | Fashionable India © 2025<br>
        <a href='https://www.myntra.com' target='_blank' style='color:#8a6a4a'>Myntra</a> &nbsp;|&nbsp;
        <a href='https://www.ajio.com' target='_blank' style='color:#8a6a4a'>Ajio</a> &nbsp;|&nbsp;
        <a href='https://www.meesho.com' target='_blank' style='color:#8a6a4a'>Meesho</a> &nbsp;|&nbsp;
        <a href='https://www.nykaa.com' target='_blank' style='color:#8a6a4a'>Nykaa</a>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
