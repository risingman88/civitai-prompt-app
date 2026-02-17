"""
Civitai Prompt Generator App
AI-powered prompt generator following Civitai's official methodology
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

# Default quality tags (placed at END of prompt per Civitai methodology)
QUALITY_TAGS = [
    'masterpiece', 'best quality', 'highres', 'absurdres', 'ultra realistic',
    'sharp focus', 'fine details', 'highly detailed', '8k', '4k', 'HDR',
    'realism', 'realistic', 'cinematic', 'professional', 'amazing quality'
]

# Standard negative prompt template
DEFAULT_NEGATIVE = "text, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry"

# ============ MINIMAX API ============
def call_minimax_api(prompt_text, api_key, num_variations=5):
    """Generate optimized prompts using MiniMax API following Civitai methodology"""
    
    if not api_key:
        return None
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Detailed prompt engineering instructions
    system_prompt = """You are an expert AI art prompt engineer following Civitai's official methodology.

STRUCTURE YOUR PROMPTS LIKE THIS:
1. MEDIUM (optional): photo, oil painting, digital art, 3d render, pencil sketch
2. SUBJECT: 1girl, woman, man + physical details (athletic, tall, curvy)
3. FACE/HAIR: blue eyes, brunette, wavy hair, detailed face
4. CLOTHING: wearing red dress, leather jacket, bikini
5. POSE/EXPRESSION: standing, smiling, looking at viewer, arms crossed
6. SETTING: luxury bedroom, park, beach, studio, forest
7. LIGHTING: dramatic lighting, golden hour, soft lighting, rim lighting
8. COMPOSITION: close-up, medium shot, full body, from above
9. TECHNICAL (END): 8k, high resolution, sharp focus, masterpiece

CRITICAL RULES:
- Use comma-separated TAGS, not natural language
- Put most important elements FIRST (higher attention)
- Quality tags go at the END, not start
- Remove redundant descriptors
- Don't mix conflicting styles (realistic + anime)
- No URLs, HTML, or special characters
- Weight key elements with (keyword:1.2) for emphasis

NEGATIVE PROMPT TEMPLATE:
text, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry

Generate creative variations that follow this structure."""

    user_prompt = f"""Create {num_variations} unique image prompts based on this seed: "{prompt_text}"

Requirements:
1. Follow the tag-based structure above
2. Group related concepts together
3. Place subject first, quality at end
4. Add 2-4 creative variations with different poses, settings, or moods
5. Include appropriate negative prompts

Return ONLY a JSON array:
[
  {{"prompt": "full optimized prompt here", "negative": "negative prompt"}},
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
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.8,
                "max_tokens": 4000
            },
            timeout=90
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result:
                content = result['choices'][0]['message']['content']
                content = content.strip()
                # Clean up JSON
                if content.startswith('```json'):
                    content = content[7:-3]
                elif content.startswith('```'):
                    content = content[3:-3]
                parsed = json.loads(content)
                if isinstance(parsed, list):
                    results = []
                    for item in parsed:
                        if isinstance(item, dict):
                            prompt = item.get('prompt', '')
                            negative = item.get('negative', DEFAULT_NEGATIVE)
                            results.append({'prompt': prompt, 'negative': negative})
                        else:
                            results.append({'prompt': str(item), 'negative': DEFAULT_NEGATIVE})
                    return results
    except Exception as e:
        st.error(f"API Error: {str(e)}")
    
    return None

def expand_with_ai(seed_prompt, api_key, num_expansions=5):
    """Expand a prompt with creative variations using AI"""
    
    if not api_key:
        return None
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    system_prompt = """You are an expert AI art prompt engineer.

Given a prompt, create creative expansions following Civitai's methodology:
- Add new poses, expressions, settings, or moods
- Keep subject consistent but vary the context
- Add 2-4 key creative elements
- Maintain the tag-based structure"""

    user_prompt = f"""Expand this prompt with creative variations:

"{seed_prompt}"

Create {num_expansions} variations that:
1. Change pose/expression
2. Change setting/environment  
3. Change lighting/atmosphere
4. Create a "creative mix" combining elements

Return ONLY JSON:
[
  {{"prompt": "expanded prompt", "description": "what changed"}},
  ...
]"""

    try:
        response = requests.post(
            "https://api.minimax.chat/v1/text/chatcompletion_v2",
            headers=headers,
            json={
                "model": "MiniMax-Text-01",
                "messages": [
                    {"role": "system", "content": system_prompt},
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
    """Fallback generation without API - follows Civitai structure"""
    variations = []
    
    for _ in range(num_variations):
        parts = []
        
        # Section 1: Subject (most important)
        subject_parts = []
        if 'subject' in seed_elements:
            subject_parts.extend(seed_elements['subject'][:2])
        if 'body_features' in seed_elements:
            subject_parts.extend(seed_elements['body_features'][:2])
        if 'hair' in seed_elements:
            subject_parts.extend(seed_elements['hair'][:2])
        if subject_parts:
            parts.append(", ".join(subject_parts))
        
        # Section 2: Clothing
        if 'clothing' in seed_elements:
            parts.append(", ".join(seed_elements['clothing'][:2]))
        
        # Section 3: Pose & Expression
        if 'pose' in seed_elements:
            parts.append(", ".join(seed_elements['pose'][:2]))
        if 'emotion' in seed_elements:
            parts.append(", ".join(seed_elements['emotion'][:2]))
        
        # Section 4: Environment
        if 'environment' in seed_elements:
            parts.append(", ".join(seed_elements['environment'][:2]))
        
        # Section 5: Lighting & Style
        if 'lighting' in seed_elements:
            parts.append(", ".join(seed_elements['lighting'][:2]))
        if 'art_style' in seed_elements:
            parts.append(", ".join(seed_elements['art_style'][:2]))
        
        # Section 6: Composition
        if 'composition' in seed_elements:
            parts.append(", ".join(seed_elements['composition'][:2]))
        if 'camera' in seed_elements:
            parts.append(", ".join(seed_elements['camera'][:2]))
        
        # Section 7: Quality (END)
        quality = random.sample(QUALITY_TAGS[:8], min(4, len(QUALITY_TAGS)))
        parts.append(", ".join(quality))
        
        variations.append({
            'prompt': ", ".join(parts),
            'negative': DEFAULT_NEGATIVE
        })
    
    return variations

def generate_fallback_expansion(seed_prompt, num_expansions=5):
    """Fallback expansion without API"""
    expansions = []
    
    # Pose variation
    expansions.append({
        'prompt': seed_prompt + ", dynamic pose, arms in motion",
        'description': 'New pose'
    })
    
    # Lighting variation
    expansions.append({
        'prompt': seed_prompt + ", dramatic lighting, rim light",
        'description': 'New lighting'
    })
    
    # Setting variation
    expansions.append({
        'prompt': seed_prompt + ", in luxury setting, ornate background",
        'description': 'New setting'
    })
    
    # Emotion variation
    expansions.append({
        'prompt': seed_prompt + ", intense gaze, powerful expression",
        'description': 'New mood'
    })
    
    # Full creative
    expansions.append({
        'prompt': seed_prompt + ", cinematic composition, golden hour lighting, (masterpiece:1.2)",
        'description': 'Creative mix'
    })
    
    return expansions[:num_expansions]

# ============ HELPER FUNCTIONS ============
def get_category_items(category, data):
    """Get unique items from dataset"""
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
**AI-powered prompt generator** following Civitai's official methodology.

Built with **tag-based structure** for optimal Stable Diffusion results.
""")

# Sidebar
with st.sidebar:
    st.header("⚙️ AI Settings")
    
    api_key = st.text_input(
        "MiniMax API Key",
        type="password",
        help="Enter MiniMax API key for AI generations"
    )
    
    use_ai = st.checkbox(
        "Use AI for generations", 
        value=bool(api_key),
        disabled=not api_key
    )
    
    st.info("💡 Without API key, uses structured fallback")
    
    st.markdown("---")
    
    st.header("📊 Dataset Stats")
    if data:
        st.metric("Total Images", data.get('metadata', {}).get('total_images', 0))
        st.metric("With Prompts", data.get('metadata', {}).get('with_prompts', 0))
    else:
        st.warning("No data loaded!")

# Main tabs
tab1, tab2, tab3 = st.tabs(["🎯 Build Prompt", "📚 Browse Data", "🔀 Random"])

with tab1:
    st.header("Build Optimized Prompts")
    
    # Settings
    st.subheader("⚙️ Settings")
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        num_variations = st.slider("Variations", 1, 10, 5)
    with col_s2:
        clear_prev = st.checkbox("Clear previous", value=True)
    with col_s3:
        mode = "🤖 AI" if use_ai else "🎲 Structured"
        st.text(f"Mode: {mode}")
    
    # Seed input
    st.divider()
    st.subheader("✏️ Seed Prompt")
    st.caption("Enter a description or select elements below")
    seed_input = st.text_area(
        "Describe what you want",
        value="",
        placeholder="e.g., beautiful woman in elegant dress at sunset"
    )
    
    # Category selections
    st.divider()
    st.subheader("📋 Select Elements")
    
    all_selections = {}
    col1, col2 = st.columns(2)
    
    for idx, (category, label) in enumerate(CATEGORIES.items()):
        with col1 if idx % 2 == 0 else col2:
            st.markdown(f"**{label}**")
            
            items = get_category_items(category, data)
            
            if items:
                selected = st.multiselect(
                    f"Select...",
                    options=items,
                    key=f"sel_{category}_{idx}"
                )
            else:
                manual = st.text_input(f"Add {label}...", key=f"man_{category}_{idx}")
                selected = [x.strip() for x in manual.split(',')] if manual else []
            
            if selected:
                all_selections[category] = selected
    
    # Generate
    st.divider()
    if st.button("🚀 Generate Prompts", type="primary", use_container_width=True):
        if clear_prev:
            st.session_state.generated = False
            st.session_state.positive_variations = []
            st.session_state.negative_variations = []
            st.session_state.expanded_prompts = {}
            st.session_state.show_expansion = {}
        
        with st.spinner("🤖 AI generating optimized prompts..." if use_ai else "🎲 Building structured prompts..."):
            # Build seed from input or selections
            seed_parts = []
            if seed_input:
                seed_parts.extend(split_into_terms(seed_input))
            for category, items in all_selections.items():
                if items:
                    seed_parts.extend(items)
            seed_for_ai = seed_input if seed_input else (", ".join(seed_parts) if seed_parts else "beautiful woman")
            
            # Generate variations
            if use_ai and api_key:
                results = call_minimax_api(seed_for_ai, api_key, num_variations)
                if not results:
                    results = generate_fallback_variations(all_selections, num_variations)
            else:
                results = generate_fallback_variations(all_selections, num_variations)
            
            if results:
                st.session_state.positive_variations = [r.get('prompt', '') for r in results]
                st.session_state.negative_variations = [r.get('negative', DEFAULT_NEGATIVE) for r in results]
                st.session_state.generated = True
                st.session_state.generation_count += 1
        
        st.success(f"Generated {num_variations} optimized prompts!")
    
    # Display results
    if st.session_state.generated and st.session_state.positive_variations:
        st.divider()
        st.subheader(f"✨ Generated Prompts (Gen #{st.session_state.generation_count})")
        
        for i, (pos, neg) in enumerate(zip(
            st.session_state.positive_variations,
            st.session_state.negative_variations
        )):
            var_key = f"var_{i}"
            
            with st.expander(f"Prompt {i+1}", expanded=(i==0)):
                st.text_area(
                    f"Positive #{i+1}",
                    value=pos,
                    height=140,
                    key=f"pos_{i}_{st.session_state.generation_count}"
                )
                
                col_cp, _ = st.columns([1, 6])
                with col_cp:
                    if st.button("📋 Copy", key=f"cp_{i}_{st.session_state.generation_count}"):
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
                    if st.button(f"✨ Expand This Prompt", key=f"exp_{i}_{st.session_state.generation_count}"):
                        with st.spinner("🤖 AI expanding..." if use_ai else "🎲 Expanding..."):
                            if use_ai and api_key:
                                expansions = expand_with_ai(pos, api_key, 5)
                                if not expansions:
                                    expansions = generate_fallback_expansion(pos, 5)
                            else:
                                expansions = generate_fallback_expansion(pos, 5)
                            
                            st.session_state.expanded_prompts[var_key] = expansions or []
                            st.session_state.show_expansion[var_key] = True
                            st.rerun()
                with col_cp2:
                    if st.button("📋 Neg", key=f"cpn_{i}_{st.session_state.generation_count}"):
                        st.toast("Copied!")
                
                # Show expansions
                if st.session_state.show_expansion.get(var_key) and var_key in st.session_state.expanded_prompts:
                    expansions = st.session_state.expanded_prompts[var_key]
                    
                    st.divider()
                    st.markdown("### ✨ Creative Expansions")
                    
                    for j, exp in enumerate(expansions):
                        prompt = exp.get('prompt', '') if isinstance(exp, dict) else exp
                        desc = exp.get('description', '') if isinstance(exp, dict) else ''
                        
                        with st.expander(f"Variation {j+1}" + (f" - {desc}" if desc else "")):
                            st.text_area(
                                f"Expanded #{j+1}",
                                value=prompt,
                                height=80,
                                key=f"exp_{var_key}_{j}"
                            )
                            col_c, _ = st.columns([1, 6])
                            with col_c:
                                if st.button("📋", key=f"cpe_{var_key}_{j}"):
                                    st.toast("Copied!")
                    
                    if st.button("▼ Hide", key=f"hide_{var_key}"):
                        st.session_state.show_expansion[var_key] = False
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
            "📥 Download All",
            json.dumps(all_prompts, indent=2),
            file_name="optimized_prompts.json",
            mime="application/json"
        )
        
        if st.button("🗑️ Clear"):
            st.session_state.generated = False
            st.session_state.positive_variations = []
            st.session_state.generation_count = 0
            st.rerun()

with tab2:
    st.header("📚 Browse Dataset")
    if data and 'categorized_images' in data:
        filter_base = st.selectbox(
            "Filter by Model",
            options=['All'] + sorted(set(img.get('baseModel', 'Unknown') for img in data['categorized_images']))
        )
        
        filtered = data['categorized_images']
        if filter_base != 'All':
            filtered = [img for img in filtered if img.get('baseModel') == filter_base]
        
        st.metric("Showing", f"{len(filtered)} images")
        
        for img in filtered[:15]:
            with st.expander(f"ID: {img.get('id')}"):
                st.code(img.get('prompt', 'N/A')[:600])
    else:
        st.warning("No data!")

with tab3:
    st.header("🔀 Random Generator")
    if data and 'categorized_images' in data:
        if st.button("🎲 Random Prompt", type="primary"):
            random_img = random.choice(data['categorized_images'])
            st.code(random_img.get('prompt', 'N/A'))
    else:
        st.warning("No data!")

st.divider()
st.caption("🎨 Civitai Prompt Generator | Powered by MiniMax AI")
