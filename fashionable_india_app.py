import streamlit as st
from groq import Groq
from PIL import Image
import io, re, time, datetime

st.set_page_config(
    page_title="Fashionable India ✨",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;800&family=DM+Sans:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; background-color: #fdfaf7; color: #1a1208; }
.main-header { font-family: 'Playfair Display', serif; font-size: 3.2rem; font-weight: 800; background: linear-gradient(135deg, #D4AF37, #FF6B6B, #C84B31); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; padding: 1rem 0 0.2rem; }
.tagline { text-align: center; color: #8a6040; font-size: 1rem; letter-spacing: 0.15em; text-transform: uppercase; margin-bottom: 2rem; }
.result-section { background: linear-gradient(135deg, #fff8f2, #fef5ec); border-left: 4px solid #D4AF37; border-radius: 0 12px 12px 0; padding: 1.2rem 1.5rem; margin: 0.8rem 0; }
.shop-btn { display: inline-block; background: linear-gradient(135deg, #D4AF37, #C84B31); color: white !important; padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.8rem; font-weight: 500; margin: 0.2rem; text-decoration: none !important; }
hr { border-color: #e8d5c0 !important; }
.stButton>button { background: linear-gradient(135deg, #D4AF37, #C84B31); color: white; border: none; border-radius: 25px; padding: 0.6rem 2rem; font-size: 1rem; font-weight: 600; width: 100%; }
.stTextArea textarea { background: #fff8f2 !important; color: #1a1208 !important; border-color: #e8d5c0 !important; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ─── AFFILIATE LINKS ───
AFFILIATE_LINKS = {
    "Myntra":   "https://www.myntra.com/search?rawQuery=",
    "Ajio":     "https://www.ajio.com/search/?text=",
    "Meesho":   "https://meesho.com/search?q=",
    "Nykaa":    "https://www.nykaa.com/search/result/?q=",
    "Flipkart": "https://www.flipkart.com/search?q=",
    "Amazon":   "https://www.amazon.in/s?k=",
}

def make_link(platform, query):
    base = AFFILIATE_LINKS.get(platform, "https://www.google.com/search?q=")
    return base + query.replace(" ", "+")

# ─── RATE LIMITING ───
def check_rate_limit():
    now = time.time()
    if "requests" not in st.session_state:
        st.session_state.requests = []
    st.session_state.requests = [t for t in st.session_state.requests if now - t < 60]
    if len(st.session_state.requests) >= 3:
        wait = int(60 - (now - st.session_state.requests[0]))
        st.error(f"⏳ Thoda wait karo! {wait} seconds mein dobara try karo.")
        return False
    st.session_state.requests.append(now)
    return True

# ─── SYSTEM PROMPT ───
SYSTEM_PROMPT = """
You are India's #1 AI Personal Stylist, Dermatologist & Grooming Expert for "Fashionable India".
Philosophy: "Anyone can become stylish — regardless of background, budget, or appearance."

━━━ CRITICAL RULES ━━━
0. NAME: Use ONLY the name from profile. Never invent names.
1. NO BODY SHAME: Use curvy/athletic/slender. Never fat/skinny.
2. LANGUAGE:
   - Hinglish 🇮🇳: Standard Hindi in English alphabet + English. ONLY use: aap/tum/yaar/bilkul/ekdum/bahut/achha. NEVER Punjabi(tuhade)/Telugu(nuvvu)/regional words.
   - English 🇬🇧: Pure professional warm English. Zero Hindi words.
3. GENDER — MOST CRITICAL:
   - Male: EXCLUSIVELY men's products. Zero women's items. Every single item must be for men.
   - Female: EXCLUSIVELY women's products. Zero men's items. Every single item must be for women.
   - Triple-check each product before suggesting.
4. UNIQUENESS: 100% personalized to THIS exact profile. Reference their specific details always.
5. SCIENCE: Back skincare with ingredients + explain WHY it works for their skin type.
6. SPECIFICITY: Exact fit, exact color for skin tone, exact Indian brand in budget.

━━━ USER PROFILE ━━━
{profile}

━━━ STYLING ENGINE ━━━
[MEN BODY TYPES]
Inverted Triangle: Slim-fit tops, tapered trousers, V-necks
Rectangle: Padded blazers, structured jackets, layering
Oval/Round: Dark verticals, straight-fit, long shirts, avoid tight
Triangle: Broad collars, padded shoulders, horizontal stripes top

[WOMEN BODY TYPES]
Pear: Boat necks, A-line kurtis, dark bottoms, statement tops
Apple: Empire waist, flowy georgette, V-necks, avoid bodycon
Rectangle: Peplum, belts, fit-and-flare, ruffles
Hourglass: Wrap dresses, belted, bodycon, fitted silhouettes
Inverted Triangle: Wide-leg pants, palazzos, A-line skirts

[FACE SHAPES & GLASSES]
Oval: Most frames work, rectangular/wayfarer best
Round: Angular/rectangular frames to add definition
Square: Round/oval frames to soften jawline
Heart: Bottom-heavy frames, aviators, round frames
Diamond: Oval/rimless frames, cat-eye for women

[SKIN TONE COLORS]
Fair: Jewel tones, Navy, Burgundy, Emerald
Wheatish: Mustard, Rust, Olive, Earthy Browns, Terracotta
Dusky: Coral, Mint, Peach, Gold, Maroon, Royal Blue
Very Dark: Hot Pink, Orange, White, Royal Blue, Lime Green

[HEIGHT]
Short(<5'4"): Monochromatic, vertical stripes, high-waist, avoid oversized
Average(5'4"-5'8"): Most styles work
Tall(>5'8"): Color blocking, horizontal stripes, wide-leg, large prints

[SKIN TYPES & INGREDIENTS]
Oily: Salicylic Acid(BHA), Niacinamide, Benzoyl Peroxide, lightweight gel moisturizer
Dry: Hyaluronic Acid, Ceramides, Shea Butter, Squalane, rich cream moisturizer
Combination: Niacinamide, lightweight Hyaluronic Acid, gel-cream moisturizer
Sensitive: Centella Asiatica, Aloe Vera, Ceramides, fragrance-free products, gentle cleanser

[HAIR TYPES]
Straight: Volumizing shampoo, light serum, avoid heavy oils
Wavy: Sulfate-free shampoo, curl-enhancing cream, argan oil
Curly: Moisture-rich shampoo, deep conditioner, leave-in cream, castor oil
Coily: Co-wash, heavy moisturizer, shea butter, protective styles

[INDIAN BRANDS BY BUDGET]
Under ₹500: Meesho, Bewakoof, Campus Sutra
₹500-1500: H&M, Roadster, Mast&Harbour, HRX, Highlander
₹1500-3000: Jack&Jones, Only, Vero Moda, W for Women, Aurelia
₹3000-6000: Tommy Hilfiger, U.S.Polo, Van Heusen, AND
₹6000+: Zara, Marks&Spencer, Global Desi

[SKINCARE BRANDS INDIA]
Budget: Minimalist, Plum, Dot&Key, Mamaearth, Wow, Re'equil
Mid: The Derma Co, Pilgrim, MCaffeine, Foxtale, Prolixr
Premium: Clinique, Neutrogena, La Roche-Posay, Cetaphil, The Ordinary

━━━ RESPOND IN EXACTLY THIS 9-PART STRUCTURE ━━━

1. 🌟 Style Breakdown:
[Address by name. Analyze body type + skin tone + face shape + height + region warmly. 3-4 lines. Celebrity stylist tone.]

2. 👗 Perfect Outfit Formula:
[3 complete outfits — Casual + Formal + Ethnic/Occasion.
Format: Top + Bottom + Shoes + Accessory + Color rationale.
GENDER-CORRECT items ONLY. Budget-appropriate brands.]

3. 🌍 Regional Style Hack:
[Climate + region specific fabric + outfit tip. 2-3 lines.]

4. ✨ Pro Style Secret:
[One ultra-specific trick for their body type + height. 2-3 lines.]

5. 💆 Complete Skincare Routine:
Based on their EXACT skin type, provide:
DAY ROUTINE:
- Cleanser: [product type + key ingredient + why for their skin]
- Toner: [product type + key ingredient + why]
- Serum: [product type + key ingredient + why]
- Moisturizer: [product type + key ingredient + why]
- Sunscreen: [SPF recommendation + why]
- Lip Balm: [type + why]
NIGHT ROUTINE:
- Cleanser: [double cleanse or single + why]
- Toner: [type + ingredient]
- Serum/Treatment: [active ingredient for their concern + why it works at night]
- Moisturizer: [richer option for night + why]
- Lip treatment: [overnight lip mask/balm]

6. 💇 Hair Care Routine:
Based on their hair type:
- Shampoo: [type + ingredient + frequency]
- Conditioner: [type + application method]
- Hair Oil: [which oil + how to use]
- Hair Serum: [for what purpose + when to apply]
For MEN: Beard style for their face shape + beard care routine
For WOMEN: Best haircut for face shape + styling tip

7. 🎨 Style Aesthetic + Fragrance:
- Best aesthetic match for their profile + why
- Day fragrance: [type + occasion]
- Night/Date fragrance: [type + occasion]

8. 😎 Glasses Recommendation:
Based on face shape, suggest exact frame style that suits them + why.

9. 🛍️ Complete Shopping List (15-16 items):

⚠️ GENDER LOCK RULE — READ BEFORE WRITING EACH ITEM:
- If Male: Search queries MUST contain "men" or "men's". Example: "HRX Navy Blue Slim Fit T-Shirt Men"
- If Female: Search queries MUST contain "women" or "women's". Example: "Only Women Navy Blue Slim Fit Top"
- NEVER write a search query without the gender word at the end.
- SELF-CHECK: Before writing each item, ask — "Is this 100% for [their gender]?" If any doubt, rewrite.

Format: [Category] [Platform] -> Search: "[Exact search query with gender word]"

Clothing (STRICT Gender-specific):
- Upper 1: [Myntra/Ajio] -> Search: "[brand] [color] [fit] [clothing type] [men/women]"
- Upper 2: [Myntra/Ajio] -> Search: "[brand] [color] [fit] [clothing type] [men/women]"
- Lower 1: [Myntra/Ajio] -> Search: "[brand] [color] [fit] [trouser/jeans/skirt/etc] [men/women]"
- Lower 2: [Meesho/Ajio] -> Search: "[brand] [color] [fit] [trouser/jeans/skirt/etc] [men/women]"
- Ethnic: [Myntra/Meesho] -> Search: "[brand] [kurta/kurti/sherwani/salwar] [men/women]"
- Footwear 1: [Myntra/Flipkart] -> Search: "[brand] [sneakers/heels/loafers] [color] [men/women]"
- Footwear 2: [Amazon/Myntra] -> Search: "[brand] [formal/casual shoes] [color] [men/women]"
- Sunglasses: [Amazon/Flipkart] -> Search: "[frame shape] sunglasses [men/women]"

Skincare (skin type + gender specific):
- Face Wash: [Nykaa] -> Search: "[brand] [ingredient] face wash [skin type] [men/women]"
- Toner: [Nykaa] -> Search: "[brand] [ingredient] toner [skin type]"
- Serum: [Nykaa] -> Search: "[brand] [Vitamin C/Niacinamide/etc] serum [skin type]"
- Moisturizer: [Nykaa/Flipkart] -> Search: "[brand] [gel/cream] moisturizer [skin type]"
- Sunscreen: [Nykaa] -> Search: "[brand] SPF [50/30] sunscreen [skin type] [men/women]"
- Lip Balm: [Nykaa/Amazon] -> Search: "[brand] lip balm [moisturizing/SPF]"

Haircare (hair type specific):
- Shampoo: [Nykaa/Amazon] -> Search: "[brand] [sulfate-free/volumizing] shampoo [hair type]"
- Hair Serum: [Nykaa] -> Search: "[brand] hair serum [frizz control/shine/etc]"

Fragrance (gender + occasion specific):
- Day Perfume: [Nykaa/Amazon] -> Search: "[brand] [fresh/citrus/light floral] perfume [men/women] EDT"
- Night/Date Perfume: [Nykaa/Amazon] -> Search: "[brand] [woody/oriental/musky] perfume [men/women] EDP"

TONE: Personal, warm, expert. Never generic. Every word feels made ONLY for this person.
"""

# ─── AI CALL ───
def get_styling_advice(profile: dict, api_key: str) -> str:
    client = Groq(api_key=api_key)
    profile_text = "\n".join([f"- {k}: {v}" for k, v in profile.items()])
    prompt = SYSTEM_PROMPT.replace("{profile}", profile_text)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=3000,
        temperature=0.7,
    )
    return response.choices[0].message.content

# ─── PARSE SHOPPING ITEMS ───
def parse_shopping_items(text: str):
    items = []
    platforms = "Myntra|Ajio|Meesho|Nykaa|Flipkart|Amazon"
    pattern = rf'(?:Upper|Lower|Ethnic|Footwear|Face Wash|Toner|Serum|Moisturizer|Sunscreen|Lip Balm|Shampoo|Hair Serum|Sunglasses|Clothing)?[^\n]*?\b({platforms})\b[^\n]*?Search:\s*"([^"]+)"'
    matches = re.findall(pattern, text, re.IGNORECASE)
    seen = set()
    for platform, query in matches:
        key = query.strip().lower()
        if key not in seen:
            seen.add(key)
            items.append({
                "platform": platform.strip(),
                "query": query.strip(),
                "url": make_link(platform.strip(), query.strip())
            })
    return items[:18]

# ─── MAIN APP ───
def main():
    st.markdown('<div class="main-header">✨ Fashionable India</div>', unsafe_allow_html=True)
    st.markdown('<div class="tagline">Anyone Can Be A Stylist In Their Own Way</div>', unsafe_allow_html=True)
    st.markdown("---")

    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        api_key = st.secrets.get("GROQ_API_KEY", "") or st.text_input("🔑 Groq API Key", type="password")
        st.markdown("---")
        st.markdown("### 🌐 Language / Bhasha")
        language = st.radio("", ["Hinglish 🇮🇳", "English 🇬🇧"], horizontal=True)
        st.markdown("---")
        st.markdown("### 📸 Upload Photo (Optional)")
        uploaded_img = st.file_uploader("Photo upload karo", type=["jpg", "jpeg", "png"])
        st.markdown("---")
        st.caption("Fashionable India — AI-powered personal styling for every Indian.")

    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.markdown("### 👤 Apne Baare Mein Batao")
        user_name = st.text_input("👤 Naam / Name", placeholder="e.g. Adarsh, Priya...")
        gender = st.radio("Gender", ["Male", "Female", "Other"], horizontal=True)

        c1, c2 = st.columns(2)
        with c1:
            skin_tone = st.selectbox("🎨 Skin Tone", ["Fair (Gora)", "Wheatish (Gehuniya)", "Dusky (Saanwla)", "Very Dark"])
            height = st.select_slider("📏 Height", options=["Very Short (<5'2\")", "Short (5'2\"–5'5\")", "Medium (5'5\"–5'8\")", "Tall (5'8\"–5'11\")", "Very Tall (>5'11\")"], value="Medium (5'5\"–5'8\")")
            face_shape = st.selectbox("😊 Face Shape", ["Oval", "Round", "Square", "Heart", "Diamond"])
        with c2:
            skin_type = st.selectbox("🧴 Skin Type", ["Oily", "Dry", "Combination", "Sensitive"])
            hair_type = st.selectbox("💇 Hair Type", ["Straight", "Wavy", "Curly", "Coily"])
            body_type_options = {
                "Male": ["Inverted Triangle (Broad Shoulders)", "Rectangle (Athletic)", "Oval/Round (Curvy Mid)", "Triangle (Narrow Shoulders)"],
                "Female": ["Pear (Heavy Bottom)", "Apple (Heavy Mid)", "Rectangle (Straight)", "Hourglass", "Inverted Triangle (Broad Shoulders)"],
                "Other": ["Slender", "Athletic", "Curvy", "Plus Size"]
            }
            body_type = st.selectbox("👤 Body Type", body_type_options.get(gender, body_type_options["Other"]))

        occasion = st.multiselect("🎯 Occasion", ["Daily Office", "Casual Outings", "College", "Wedding/Shaadi", "Festive/Pooja", "Date Night", "Sports/Gym"], default=["Casual Outings"])
        budget = st.select_slider("💰 Budget", options=["Under ₹500", "₹500–1,500", "₹1,500–3,000", "₹3,000–6,000", "₹6,000+"], value="₹500–1,500")
        city_type = st.selectbox("🌍 Region", ["North India (Hot & Cold)", "South India (Hot & Humid)", "East India (Humid & Festive)", "West India (Dry & Coastal)", "Hill Station (Cold)"])
        extra_notes = st.text_area("📝 Extra Notes (Optional)", placeholder="Koi special preference? e.g. No ethnic wear, Office formal only...")

    with col2:
        st.markdown("### 🎯 Style Preview")
        if uploaded_img:
            img = Image.open(uploaded_img)
            st.image(img, caption="Tumhari photo 📸", use_container_width=True)
            st.success("✅ Photo upload ho gayi!")
        else:
            st.markdown("""<div style="background:linear-gradient(145deg,#fff8f2,#fef3e8);border:1px solid #e8d5c0;border-radius:16px;padding:3rem 1rem;text-align:center;">
                <div style="font-size:4rem">👗</div>
                <p style="color:#8a6040;margin-top:1rem">Form bhar ke apna<br>AI Style Report pao!</p></div>""", unsafe_allow_html=True)

        st.markdown("### 💡 Style Tip")
        import random
        tips = ["🌈 Monochromatic outfits instantly make you look taller!", "👟 White sneakers work with almost every outfit.", "🎽 Tucked-in shirt always looks more polished.", "🧣 One statement accessory changes the whole look!", "🕶️ Right sunglasses can transform your entire look!"]
        st.info(random.choice(tips))

        st.markdown("### 📊 Your Profile Summary")
        if user_name:
            st.markdown(f"""<div style="background:#fff8f2;border:1px solid #e8d5c0;border-radius:12px;padding:1rem;">
            <b>👤 {user_name}</b> | {gender}<br>
            🎨 {skin_tone} | 📏 {height}<br>
            😊 {face_shape} face | 🧴 {skin_type} skin<br>
            💇 {hair_type} hair | 💰 {budget}
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        generate = st.button("✨ Mera Complete Style Report Banao!")

    if generate:
        if not api_key:
            st.error("⚠️ Groq API Key daalo sidebar mein!")
            return
        if not check_rate_limit():
            return

        profile = {
            "Name": user_name if user_name else "Friend",
            "Gender": gender,
            "Skin Tone": skin_tone,
            "Skin Type": skin_type,
            "Face Shape": face_shape,
            "Hair Type": hair_type,
            "Height": height,
            "Body Type": body_type,
            "Occasion": ", ".join(occasion) if occasion else "Casual",
            "Budget": budget,
            "City/Region": city_type,
            "Language": language,
            "Extra Notes": extra_notes or "None",
        }

        with st.spinner("🪡 Aapka complete style report teyaar ho raha hai... (30-40 seconds)"):
            try:
                result = get_styling_advice(profile, api_key)

                st.markdown("---")
                st.markdown("## 🎨 Aapka Complete Personal Style Report")

                sections = re.split(r'(?=\d+\.\s[🌟👗🌍✨💆💇🎨😎🛍️])', result)
                for section in sections:
                    if section.strip():
                        st.markdown(f'<div class="result-section">{section.strip().replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)

                # Shopping Links
                items = parse_shopping_items(result)
                if items:
                    st.markdown("---")
                    st.markdown("### 🛒 Direct Shopping Links")
                    
                    # Categorize items
                    categories = {
                        "👗 Clothing & Footwear": [],
                        "🧴 Skincare": [],
                        "💇 Haircare": [],
                        "🌸 Fragrance": [],
                        "😎 Accessories": []
                    }
                    
                    skincare_keywords = ["face wash", "toner", "serum", "moisturizer", "sunscreen", "lip"]
                    hair_keywords = ["shampoo", "hair"]
                    sunglass_keywords = ["sunglass", "eyewear", "frame"]
                    fragrance_keywords = ["perfume", "fragrance", "edt", "edp", "cologne", "deodorant"]
                    
                    for item in items:
                        q = item['query'].lower()
                        if any(k in q for k in skincare_keywords):
                            categories["🧴 Skincare"].append(item)
                        elif any(k in q for k in hair_keywords):
                            categories["💇 Haircare"].append(item)
                        elif any(k in q for k in fragrance_keywords):
                            categories["🌸 Fragrance"].append(item)
                        elif any(k in q for k in sunglass_keywords):
                            categories["😎 Accessories"].append(item)
                        else:
                            categories["👗 Clothing & Footwear"].append(item)

                    for cat_name, cat_items in categories.items():
                        if cat_items:
                            st.markdown(f"**{cat_name}**")
                            cols = st.columns(min(len(cat_items), 4))
                            for i, item in enumerate(cat_items):
                                with cols[i % 4]:
                                    st.markdown(f'<a href="{item["url"]}" target="_blank" class="shop-btn">🛍️ {item["platform"]}<br><small>{item["query"][:25]}...</small></a>', unsafe_allow_html=True)
                            st.markdown("")

                # Download
                st.markdown("---")
                st.download_button("📥 Style Report Download Karo", data=result, file_name=f"style_report_{user_name or 'me'}.txt", mime="text/plain")

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    # ─── FEEDBACK FORM ───
    st.markdown("---")
    st.markdown("### 📝 Feedback — Help Us Improve!")
    st.markdown("""
    <div style="background:linear-gradient(135deg,#fff8f2,#fef5ec);border:1px solid #e8d5c0;border-radius:16px;padding:1.5rem;text-align:center;">
        <div style="font-size:2rem">💬</div>
        <h4 style="color:#C84B31;font-family:'Playfair Display',serif;">Aapka Feedback Chahiye!</h4>
        <p style="color:#8a6040;">2 minute mein batao — kya achha laga, kya improve ho sakta hai?<br>Har feedback personally padha jaata hai!</p>
        <a href="https://forms.gle/HV25NY6bzF23Un659" target="_blank" 
           style="display:inline-block;background:linear-gradient(135deg,#D4AF37,#C84B31);color:white;padding:0.8rem 2rem;border-radius:25px;font-weight:600;text-decoration:none;margin-top:0.5rem;">
            📝 Feedback Do — 2 Min!
        </a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<div style='text-align:center;color:#8a6040;font-size:0.8rem;padding:1rem'>Made with ❤️ for India | Fashionable India © 2025<br><a href='https://www.myntra.com' target='_blank' style='color:#8a6040'>Myntra</a> &nbsp;|&nbsp; <a href='https://www.ajio.com' target='_blank' style='color:#8a6040'>Ajio</a> &nbsp;|&nbsp; <a href='https://www.meesho.com' target='_blank' style='color:#8a6040'>Meesho</a> &nbsp;|&nbsp; <a href='https://www.nykaa.com' target='_blank' style='color:#8a6040'>Nykaa</a></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
