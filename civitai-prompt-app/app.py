"""
Civitai Prompt Generator App
A Streamlit-based interactive prompt generator with AI-powered generations
"""

import streamlit as st
import json
import random
import re
import requests
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Civitai Prompt Generator",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load parsed data
@st.cache_data
def load_data():
    data_path = Path(__file__).parent / "data" / "parsed_data.json"
    if data_path.exists():
        with open(data_path, 'r') as f:
            return json.load(f)
    return None

data = load_data()

# Category definitions
CATEGORIES = {
    'subject': '👤 Subject',
    'pose': '🧘 Pose/Position',
    'environment': '🌍 Environment/Setting',
    'body_features': '💪 Body Features',
    'hair': '💇 Hair Style/Color',
    'clothing': '👗 Clothing/Accessories',
    'lighting': '💡 Lighting',
    'art_style': '🎨 Art Style',
    'quality': '✨ Quality Tags',
    'camera': '📷 Camera/Technical',
    'composition': '📐 Composition',
    'emotion': '😊 Emotion/Expression',
    'skin_features': '🧴 Skin Features',
    'special_effects': '✨ Special Effects',
}

# Default quality tags
QUALITY_TAGS = [
    'masterpiece', 'best quality', 'highres', 'absurdres', 'ultra realistic',
    'sharp focus', 'fine details', 'highly detailed', '8k', '4k', 'HDR',
    'realism', 'realistic', 'cinematic', 'professional', 'amazing quality'
]

DEFAULT_NEGATIVE = "score_6, score_5, score_4, worst quality, low quality, bad anatomy, bad hands, deformed, ugly, disfigured, poorly drawn face, mutation, extra fingers, fewer fingers"

# Fallback suggestions for when AI is not available
POSE_SUGGESTIONS = [
    "arms above head", "hands on hips", "legs crossed", "one leg raised",
    "leaning forward", "leaning back", "twisting", "bending",
    "looking over shoulder", "head tilted", "eyes closed"
]

LIGHTING_SUGGESTIONS = [
    "rim lighting", "backlit", "golden hour", "blue hour",
    "neon lights", "candlelight", "moonlight", "studio strobes"
]

ENVIRONMENT_SUGGESTIONS = [
    "luxury bedroom", "hotel room", "modern apartment", "garden terrace",
    "balcony", "secluded beach", "yacht deck", "candlelit room"
]

EMOTION_SUGGESTIONS = [
    "seductive", "confident", "playful", "mysterious", "romantic",
    "sensual", "adorable", "alluring", "provocative", "dreamy"
]

# ============ MINIMAX API ============
def call_minimax_api(prompt_text, api_key, num_variations=5):
    """Generate prompts using MiniMax API"""
    
    if not api_key:
        return None
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    user_prompt = f"""You are an expert AI art prompt engineer.

Given this seed prompt: "{prompt_text}"

Generate {num_variations} creative AI image prompts based on it.

Rules:
1. Keep the core subject/style elements
2. Add variations in: poses, emotions, lighting, settings, clothing
3. Make each variation unique and visually interesting
4. Use quality tags (masterpiece, highres, etc.)

Return ONLY a JSON array:
[
  {{"prompt": "full detailed prompt here"}},
  ...
]

No other text. Only the JSON array."""

    try:
        response = requests.post(
            "https://api.minimax.chat/v1/text/chatcompletion_v2",
            headers=headers,
            json={
                "model": "MiniMax-Text-01",
                "messages": [
                    {"role": "system", "content": "You are a creative AI art prompt expert."},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.9,
                "max_tokens": 3000
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result:
                content = result['choices'][0]['message']['content']
                # Clean up and parse JSON
                content = content.strip()
                if content.startswith('```json'):
                    content = content[7:-3]
                elif content.startswith('```'):
                    content = content[3:-3]
                parsed = json.loads(content)
                if isinstance(parsed, list):
                    return [p.get('prompt', p) if isinstance(p, dict) else p for p in parsed]
    except Exception as e:
        st.error(f"API Error: {str(e)}")
    
    return None

def generate_ai_variations(seed_elements, api_key, num_variations=5):
    """Generate variations using AI based on selected elements"""
    
    if not api_key:
        return None
    
    # Build a seed prompt from selections
    seed_parts = []
    for category, items in seed_elements.items():
        if items:
            seed_parts.extend(items)
    seed_prompt = ", ".join(seed_parts)
    
    if not seed_prompt.strip():
        # Generate completely random creative prompts
        seed_prompt = "beautiful woman"
    
    return call_minimax_api(seed_prompt, api_key, num_variations)

def generate_ai_expansion(seed_prompt, api_key, num_variations=5):
    """Generate creative expansions for an existing prompt"""
    
    if not api_key:
        return None
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    user_prompt = f"""You are an expert AI art prompt engineer.

Take this prompt and create {num_variations} creative variations:

Original: "{seed_prompt}"

Create variations that:
1. Add new poses, emotions, lighting, settings
2. Keep the core subject but add creative twists
3. Suggest story/context for the scene
4. Include quality tags

Return ONLY a JSON array:
[
  {{"prompt": "expanded prompt here", "description": "what changed"}},
  ...
]

No other text. Only JSON."""

    try:
        response = requests.post(
            "https://api.minimax.chat/v1/text/chatcompletion_v2",
            headers=headers,
            json={
                "model": "MiniMax-Text-01",
                "messages": [
                    {"role": "system", "content": "You are a creative AI art prompt expert."},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.9,
                "max_tokens": 3000
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result:
                content = result['choices'][0]['message']['content']
                content = content.strip()
                if content.startswith('```json'):
                    content = content[7:-3]
                elif content.startswith('```'):
                    content = content[3:-3]
                return json.loads(content)
    except Exception as e:
        st.error(f"API Error: {str(e)}")
    
    return None

# ============ FALLBACK FUNCTIONS ============
def generate_fallback_variations(seed_elements, num_variations=5):
    """Fallback when no API key - uses random suggestions"""
    variations = []
    
    for _ in range(num_variations):
        parts = []
        
        # Add quality tags
        parts.extend(random.sample(QUALITY_TAGS[:8], min(4, len(QUALITY_TAGS))))
        
        # Add seed elements
        for category, items in seed_elements.items():
            if items:
                parts.extend(items)
        
        # Add random creative elements
        parts.append(random.choice(POSE_SUGGESTIONS))
        parts.append(random.choice(LIGHTING_SUGGESTIONS))
        parts.append(random.choice(ENVIRONMENT_SUGGESTIONS))
        
        variations.append(", ".join(parts))
    
    return variations

def generate_fallback_expansion(seed_prompt, num_variations=5):
    """Fallback expansion without AI"""
    expansions = []
    
    # Pose variation
    expansions.append({
        "prompt": seed_prompt + ", " + random.choice(POSE_SUGGESTIONS),
        "description": "New pose added"
    })
    
    # Lighting variation
    expansions.append({
        "prompt": seed_prompt + ", " + random.choice(LIGHTING_SUGGESTIONS),
        "description": "New lighting"
    })
    
    # Environment variation
    expansions.append({
        "prompt": seed_prompt + ", in " + random.choice(ENVIRONMENT_SUGGESTIONS),
        "description": "New setting"
    })
    
    # Emotion variation
    expansions.append({
        "prompt": seed_prompt + ", " + random.choice(EMOTION_SUGGESTIONS),
        "description": "New mood"
    })
    
    # Full creative
    creative = [
        seed_prompt,
        random.choice(POSE_SUGGESTIONS),
        random.choice(EMOTION_SUGGESTIONS),
        random.choice(LIGHTING_SUGGESTIONS),
        "in " + random.choice(ENVIRONMENT_SUGGESTIONS)
    ]
    expansions.append({
        "prompt": ", ".join(creative),
        "description": "Creative mix"
    })
    
    return expansions[:num_variations]

# ============ HELPER FUNCTIONS ============
def get_category_items(category, data):
    """Get all unique items from a category"""
    if data and 'categorized_images' in data:
        items = set()
        for img in data['categorized_images']:
            cats = img.get('categories', {})
            if category in cats:
                items.update(cats[category])
        return sorted(list(items))
    return []

def split_into_terms(text):
    terms = re.split(r'[,;\n]+', text)
    return [t.strip() for t in terms if t.strip()]

def generate_negative_prompt():
    parts = [DEFAULT_NEGATIVE]
    common_negatives = [
        "blurry", "pixelated", "low resolution", "bad anatomy",
        "mutated", "extra limbs", "disfigured", "fused fingers"
    ]
    parts.extend(random.sample(common_negatives, random.randint(2, 4)))
    return ', '.join(parts)

# ============ SESSION STATE ============
if 'generated' not in st.session_state:
    st.session_state.generated = False
if 'positive_variations' not in st.session_state:
    st.session_state.positive_variations = []
if 'negative_variations' not in st.session_state:
    st.session_state.negative_variations = []
if 'generation_count' not in st.session_state:
    st.session_state.generation_count = 0
if 'expanded_prompts' not in st.session_state:
    st.session_state.expanded_prompts = {}
if 'show_expansion' not in st.session_state:
    st.session_state.show_expansion = {}

# ============ MAIN APP ============
st.title("🎨 Civitai Prompt Generator")
st.markdown("""
Build creative AI prompts with **AI-powered variations**! Select elements 
or enter a seed, and generate unique prompts with MiniMax AI.
""")

# Sidebar - API Settings & Stats
with st.sidebar:
    st.header("⚙️ AI Settings")
    
    # API Key
    api_key = st.text_input(
        "MiniMax API Key",
        type="password",
        help="Enter MiniMax API key for AI-powered generations"
    )
    
    # AI Mode toggle
    use_ai = st.checkbox(
        "Use AI for generations", 
        value=bool(api_key),
        disabled=not api_key,
        help="When enabled, all prompt generations use MiniMax AI"
    )
    
    st.info("💡 Without API key, uses random fallback suggestions")
    
    st.markdown("---")
    
    st.header("📊 Dataset Stats")
    if data:
        st.metric("Total Images", data.get('metadata', {}).get('total_images', 0))
        st.metric("With Prompts", data.get('metadata', {}).get('with_prompts', 0))
        lora_count = len(data.get('lora_analysis', {}).get('counts', {}))
        st.metric("Unique LORAs", lora_count)
    else:
        st.warning("No data loaded!")

# Main content
tab1, tab2, tab3, tab4 = st.tabs(["🎯 Build Prompt", "📚 Browse Data", "🔀 Random Generator", "📦 LORA Insights"])

with tab1:
    st.header("Build Your Prompt")
    
    # Settings
    st.subheader("⚙️ Settings")
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        num_variations = st.slider("Number of variations", 1, 10, 5)
    with col_s2:
        clear_prev = st.checkbox("Clear previous results", value=True)
    with col_s3:
        st.text(f"Mode: {'🤖 AI' if use_ai else '🎲 Random'}")
    
    # Quick seed input
    st.divider()
    st.subheader("✏️ Quick Seed")
    seed_input = st.text_area(
        "Enter a seed prompt or description",
        value="",
        placeholder="e.g., beautiful woman in elegant dress, futuristic cityscape",
        help="This will be used as the base for AI generations"
    )
    
    # Category selections
    st.divider()
    st.subheader("📋 Or Select Elements")
    st.caption("Select from your dataset OR enter a seed above (seed takes priority)")
    
    all_selections = {}
    col1, col2 = st.columns(2)
    
    for idx, (category, label) in enumerate(CATEGORIES.items()):
        with col1 if idx % 2 == 0 else col2:
            st.markdown(f"**{label}**")
            
            items = get_category_items(category, data)
            
            if items:
                selected = st.multiselect(
                    f"Select {category}...",
                    options=items,
                    key=f"select_{category}_{idx}"
                )
            else:
                manual = st.text_input(f"Add {category}...", key=f"manual_{category}_{idx}")
                selected = [x.strip() for x in manual.split(',')] if manual else []
            
            if selected:
                all_selections[category] = selected
    
    # Generate button
    st.divider()
    if st.button("🚀 Generate Variations", type="primary", use_container_width=True):
        if clear_prev:
            st.session_state.generated = False
            st.session_state.positive_variations = []
            st.session_state.negative_variations = []
            st.session_state.expanded_prompts = {}
            st.session_state.show_expansion = {}
        
        with st.spinner("🤖 AI is generating creative variations..." if use_ai else "🎲 Generating variations..."):
            # Build seed for AI
            seed_parts = []
            if seed_input:
                seed_parts.extend(split_into_terms(seed_input))
            for category, items in all_selections.items():
                if items:
                    seed_parts.extend(items)
            
            seed_for_ai = seed_input if seed_input else (", ".join(seed_parts) if seed_parts else "beautiful woman")
            
            # Generate variations
            if use_ai and api_key:
                variations = generate_ai_variations(all_selections, api_key, num_variations)
                if not variations:
                    variations = generate_fallback_variations(all_selections, num_variations)
            else:
                variations = generate_fallback_variations(all_selections, num_variations)
            
            negative_variations = [generate_negative_prompt() for _ in range(num_variations)]
            
            st.session_state.positive_variations = variations
            st.session_state.negative_variations = negative_variations
            st.session_state.generated = True
            st.session_state.generation_count += 1
        
        mode = "🤖 AI" if use_ai else "🎲 Random"
        st.success(f"{mode} Generated {num_variations} unique variations!")
    
    # Display results
    if st.session_state.generated and st.session_state.positive_variations:
        st.divider()
        st.subheader(f"✨ Generated Variations (Gen #{st.session_state.generation_count}) [{'AI' if use_ai else 'Random'}]")
        
        for i, (pos, neg) in enumerate(zip(
            st.session_state.positive_variations, 
            st.session_state.negative_variations
        )):
            variation_key = f"var_{i}"
            
            with st.expander(f"Variation {i+1}", expanded=(i==0)):
                st.text_area(
                    f"Positive #{i+1}",
                    value=pos,
                    height=120,
                    key=f"pos_{i}_{st.session_state.generation_count}"
                )
                
                col_cp, _ = st.columns([1, 6])
                with col_cp:
                    if st.button("📋 Copy", key=f"copy_{i}_{st.session_state.generation_count}"):
                        st.session_state.copied = pos
                        st.toast("Copied!")
                
                st.markdown("---")
                st.text_area(
                    f"Negative #{i+1}",
                    value=neg,
                    height=80,
                    key=f"neg_{i}_{st.session_state.generation_count}"
                )
                
                # Expand button
                st.divider()
                col_exp, col_cp2 = st.columns([2, 1])
                with col_exp:
                    if st.button(f"✨ Expand This Prompt", key=f"expand_{i}_{st.session_state.generation_count}"):
                        with st.spinner("🤖 AI expanding..." if use_ai else "🎲 Generating..."):
                            if use_ai and api_key:
                                expansions = generate_ai_expansion(pos, api_key)
                                if not expansions:
                                    expansions = generate_fallback_expansion(pos, 5)
                            else:
                                expansions = generate_fallback_expansion(pos, 5)
                            
                            st.session_state.expanded_prompts[variation_key] = expansions or []
                            st.session_state.show_expansion[variation_key] = True
                            st.rerun()
                with col_cp2:
                    if st.button("📋 Neg", key=f"copy_neg_{i}_{st.session_state.generation_count}"):
                        st.toast("Negative copied!")
                
                # Show expansions
                if st.session_state.show_expansion.get(variation_key) and variation_key in st.session_state.expanded_prompts:
                    expansions = st.session_state.expanded_prompts[variation_key]
                    
                    st.divider()
                    st.markdown("### ✨ Creative Expansions")
                    
                    if expansions:
                        for j, exp in enumerate(expansions):
                            prompt = exp.get('prompt', '') if isinstance(exp, dict) else exp
                            desc = exp.get('description', '') if isinstance(exp, dict) else ''
                            
                            with st.expander(f"Expansion {j+1}" + (f" - {desc}" if desc else "")):
                                st.text_area(
                                    f"Expanded #{j+1}",
                                    value=prompt,
                                    height=80,
                                    key=f"exp_{variation_key}_{j}"
                                )
                                col_c, _ = st.columns([1, 5])
                                with col_c:
                                    if st.button("📋", key=f"copy_exp_{variation_key}_{j}"):
                                        st.toast("Copied!")
                    
                    if st.button("▼ Hide", key=f"hide_{variation_key}"):
                        st.session_state.show_expansion[variation_key] = False
                        st.rerun()
        
        # Download
        st.divider()
        all_prompts = {
            "variations": [
                {"positive": pos, "negative": neg}
                for pos, neg in zip(
                    st.session_state.positive_variations,
                    st.session_state.negative_variations
                )
            ]
        }
        
        st.download_button(
            "📥 Download All as JSON",
            json.dumps(all_prompts, indent=2),
            file_name="prompt_variations.json",
            mime="application/json"
        )
        
        if st.button("🗑️ Clear Results"):
            st.session_state.generated = False
            st.session_state.positive_variations = []
            st.session_state.negative_variations = []
            st.session_state.generation_count = 0
            st.session_state.expanded_prompts = {}
            st.session_state.show_expansion = {}
            st.rerun()

with tab2:
    st.header("📚 Browse Your Dataset")
    if data and 'categorized_images' in data:
        filter_base = st.selectbox(
            "Filter by Base Model",
            options=['All'] + sorted(set(img.get('baseModel', 'Unknown') for img in data['categorized_images']))
        )
        search_term = st.text_input("Search Prompts", placeholder="Search...")
        
        filtered = data['categorized_images']
        if filter_base != 'All':
            filtered = [img for img in filtered if img.get('baseModel') == filter_base]
        if search_term:
            search = search_term.lower()
            filtered = [img for img in filtered if search in img.get('prompt', '').lower()]
        
        st.metric("Showing", f"{len(filtered)} images")
        
        for img in filtered[:15]:
            with st.expander(f"ID: {img.get('id')} - {img.get('baseModel', 'Unknown')}"):
                st.code(img.get('prompt', 'N/A')[:600])
    else:
        st.warning("No data available!")

with tab3:
    st.header("🎲 Random Generator")
    if data and 'categorized_images' in data:
        if st.button("🎲 Generate Random Prompt", type="primary"):
            random_img = random.choice(data['categorized_images'])
            st.code(random_img.get('prompt', 'N/A'))
            st.text(f"Base: {random_img.get('baseModel', 'Unknown')}")
    else:
        st.warning("No data available!")

with tab4:
    st.header("📦 LORA Insights")
    if data and 'lora_analysis' in data:
        lora_data = data['lora_analysis']
        loras = lora_data.get('counts', {})
        lora_df = [{'LORA': name, 'Count': count} for name, count in list(loras.items())[:20]]
        if lora_df:
            st.dataframe(lora_df, use_container_width=True)
    else:
        st.warning("No LORA data available!")

st.divider()
st.caption("🎨 Civitai Prompt Generator | Powered by MiniMax AI")
