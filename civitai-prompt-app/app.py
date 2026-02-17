"""
Civitai Prompt Generator App
A Streamlit-based interactive prompt generator for AI image generation
"""

import streamlit as st
import json
import random
import re
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

# Category definitions with display names
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

# Variation mappings
VARIATION_MAP = {
    'sitting': ['sitting', 'seated', 'sit', 'sits', 'sitting down', 'sits down'],
    'standing': ['standing', 'stand', 'stands', 'standing up', 'stands up'],
    'lying': ['lying', 'lay', 'lying down', 'lies', 'laid'],
    'realistic photograph': ['realistic photograph', 'photorealistic', 'realistic photo', 'photograph'],
    'large breasts': ['large breasts', 'big breasts', 'huge breasts', 'massive breasts'],
    'smile': ['smile', 'smiling', 'smiles', 'smiled'],
    'naked': ['naked', 'nude', 'bare', 'undressed'],
    'topless': ['topless', 'top less', 'breasts exposed'],
    'outdoor': ['outdoor', 'outside', 'outdoors'],
    'beach': ['beach', 'seaside', 'shore', 'tropical beach'],
    'sunset': ['sunset', 'sundown', 'golden hour', 'dusk'],
    'bikini': ['bikini', 'swimsuit', 'swimwear'],
    'pinup': ['pinup pose', 'pin-up', 'pinup'],
    'athletic': ['athletic', 'fit', 'toned', 'fitness'],
    'curvy': ['curvy', 'curvaceous', 'hourglass', 'voluptuous'],
    'blonde': ['blonde', 'blond', 'golden hair'],
    'brunette': ['brunette', 'brown hair', 'chestnut'],
    'red hair': ['red hair', 'auburn', 'ginger', 'redhead'],
    'long hair': ['long hair', 'flowing hair', 'waist length'],
    'short hair': ['short hair', 'bob', 'pixie cut'],
    'blue eyes': ['blue eyes', 'azure', 'cerulean', 'sapphire'],
    'green eyes': ['green eyes', 'emerald', 'jade'],
    'kneeling': ['kneeling', 'kneel', 'on knees'],
    'squatting': ['squatting', 'squat', 'crouching'],
    'from behind': ['from behind', 'rear view', 'back view'],
    'from above': ['from above', 'bird view', 'aerial'],
    'close-up': ['close-up', 'closeup', 'tight shot'],
    'full body': ['full body', 'full shot', 'entire figure'],
    'portrait': ['portrait', 'face focus', 'headshot'],
    'studio': ['studio', 'photo studio', 'indoor studio'],
    'indoor': ['indoor', 'inside', 'interior'],
    'forest': ['forest', 'woods', 'trees', 'woodland'],
    'dynamic lighting': ['dynamic lighting', 'dramatic lighting', 'chiaroscuro'],
    'soft lighting': ['soft lighting', '柔和光线', 'diffused light'],
    'natural lighting': ['natural lighting', 'daylight', 'sunlight'],
}

# Creative expansion suggestions
POSE_SUGGESTIONS = [
    "reaching arms toward camera", "arms above head", "hands on hips", 
    "legs crossed", "one leg raised", "leaning forward", "leaning back",
    "twisting", "bending", "stretching", "dancing", "walking",
    "running hands through hair", "covering chest", "playing with hair",
    "looking over shoulder", "head tilted", "eyes closed", "mouth open"
]

LIGHTING_SUGGESTIONS = [
    "rim lighting", "backlit", "golden hour", "blue hour",
    "neon lights", "candlelight", "moonlight", "studio strobes",
    "practical lighting", "motivated lighting", "volumetric fog",
    "God rays", "softbox lighting", "ring light", "key light"
]

ENVIRONMENT_SUGGESTIONS = [
    "luxury bedroom", "master suite", "hotel room", "cozy cottage",
    "modern apartment", "loft space", "garden terrace", "balcony",
    "private courtyard", "secluded beach", "hotel balcony", "yacht deck",
    "helicopter", "private jet", "train compartment", "candlelit room"
]

EMOTION_SUGGESTIONS = [
    "seductive", "confident", "playful", "mysterious", "romantic",
    "sensual", "adorable", "alluring", "provocative", "dreamy",
    "intense", "soft", "gentle", "passionate", "wistful"
]

CLOTHING_SUGGESTIONS = [
    "silk robe", "lace underwear", "silk panties", "thong",
    "stockings", "garter belt", "sheer dress", "transparent top",
    "leather jacket", "crop top", "mini skirt", "bodycon dress",
    "bikini bottom only", "towel wrapped", "oversized shirt"
]

STORY_SUGGESTIONS = [
    "morning after", "getting ready for a date", "relaxing after work",
    "vacation mode", "self-care Sunday", "romantic getaway",
    "surprise for partner", "birthday morning", "return from trip",
    "late night reflection", "preparing for evening out", "winding down"
]

ACCESSORY_SUGGESTIONS = [
    "diamond necklace", "pearl earrings", "silk blindfold",
    "rose petals", "champagne glass", "wine glass",
    "candles", "fresh flowers", "fur throw", "velvet cushion",
    "mirror reflection", "glass surface", "silk sheets"
]

# Default quality tags
QUALITY_TAGS = [
    'masterpiece', 'best quality', 'highres', 'absurdres', 'ultra realistic',
    'sharp focus', 'fine details', 'highly detailed', '8k', '4k', 'HDR',
    'realism', 'realistic', 'cinematic', 'professional', 'amazing quality'
]

DEFAULT_NEGATIVE = "score_6, score_5, score_4, worst quality, low quality, bad anatomy, bad hands, deformed, ugly, disfigured, poorly drawn face, mutation, extra fingers, fewer fingers"

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

def get_random_variation(term):
    """Get a random variation of a term"""
    variations = VARIATION_MAP.get(term.lower(), [term])
    return random.choice(variations)

def split_into_terms(text):
    """Split custom input text into individual terms"""
    terms = re.split(r'[,;\n]+', text)
    terms = [t.strip() for t in terms if t.strip()]
    return terms

def generate_variations(selections, custom_text, num_variations=5, include_quality=True, quality_tags=None):
    """Generate multiple prompt variations with synonyms"""
    variations = []
    
    for _ in range(num_variations):
        parts = []
        
        if include_quality:
            selected_quality = random.sample(
                quality_tags or QUALITY_TAGS[:10], 
                min(3, len(quality_tags or QUALITY_TAGS))
            )
            parts.extend(selected_quality)
        
        if custom_text:
            custom_terms = split_into_terms(custom_text)
            for term in custom_terms:
                variation = get_random_variation(term)
                parts.append(variation)
        
        for category, items in selections.items():
            for item in items:
                variation = get_random_variation(item)
                parts.append(variation)
        
        variations.append(', '.join(parts))
    
    return variations

def expand_prompt(seed_prompt):
    """Generate creative expansions based on a seed prompt"""
    suggestions = {
        'poses': random.sample(POSE_SUGGESTIONS, min(3, len(POSE_SUGGESTIONS))),
        'lighting': random.sample(LIGHTING_SUGGESTIONS, min(3, len(LIGHTING_SUGGESTIONS))),
        'environments': random.sample(ENVIRONMENT_SUGGESTIONS, min(3, len(ENVIRONMENT_SUGGESTIONS))),
        'emotions': random.sample(EMOTION_SUGGESTIONS, min(3, len(EMOTION_SUGGESTIONS))),
        'clothing': random.sample(CLOTHING_SUGGESTIONS, min(3, len(CLOTHING_SUGGESTIONS))),
        'stories': random.sample(STORY_SUGGESTIONS, min(3, len(STORY_SUGGESTIONS))),
        'accessories': random.sample(ACCESSORY_SUGGESTIONS, min(3, len(ACCESSORY_SUGGESTIONS))),
    }
    
    # Generate expanded prompts based on suggestions
    expanded_prompts = []
    
    # Pose variation
    expanded = seed_prompt + ", " + random.choice(suggestions['poses'])
    expanded_prompts.append(expanded)
    
    # Lighting variation
    expanded = seed_prompt + ", " + random.choice(suggestions['lighting'])
    expanded_prompts.append(expanded)
    
    # Environment variation
    expanded = seed_prompt + ", in " + random.choice(suggestions['environments'])
    expanded_prompts.append(expanded)
    
    # Full creative variation
    creative_parts = [seed_prompt]
    creative_parts.append(random.choice(suggestions['poses']))
    creative_parts.append(random.choice(suggestions['emotions']))
    creative_parts.append(random.choice(suggestions['lighting']))
    creative_parts.append("in " + random.choice(suggestions['environments']))
    expanded_prompts.append(", ".join(creative_parts))
    
    # Story variation
    story_parts = [seed_prompt]
    story_parts.append(random.choice(suggestions['stories']))
    story_parts.append(random.choice(suggestions['emotions']))
    story_parts.append(random.choice(suggestions['accessories']))
    expanded_prompts.append(", ".join(story_parts))
    
    return {
        'suggestions': suggestions,
        'expanded_prompts': expanded_prompts
    }

def generate_negative_prompt(exclusions=None):
    """Generate negative prompt with some randomization"""
    parts = [DEFAULT_NEGATIVE]
    common_negatives = [
        "blurry", "blurred", "pixelated", "low resolution", "compression artifacts",
        "bad anatomy", "wrong anatomy", "disfigured", "mutated",
        "extra limbs", "missing limbs", "fused fingers", "too many fingers",
        "ugly", "duplicate", "morbid", "mutilated", "poorly drawn"
    ]
    random_negatives = random.sample(common_negatives, random.randint(2, 4))
    parts.extend(random_negatives)
    return ', '.join(parts)

# Initialize session state
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

# Main app layout
st.title("🎨 Civitai Prompt Generator")
st.markdown("""
Build creative AI prompts with **multiple variations**! Select options from each category,
add custom content, and generate unique prompts with synonym variations.
""")

# Sidebar - Quick Stats
with st.sidebar:
    st.header("📊 Dataset Stats")
    if data:
        st.metric("Total Images", data.get('metadata', {}).get('total_images', 0))
        st.metric("With Prompts", data.get('metadata', {}).get('with_prompts', 0))
        lora_count = len(data.get('lora_analysis', {}).get('counts', {}))
        st.metric("Unique LORAs", lora_count)
    else:
        st.warning("No data loaded!")

# Main content - Tab interface
tab1, tab2, tab3, tab4 = st.tabs(["🎯 Build Prompt", "📚 Browse Data", "🔀 Random Generator", "📦 LORA Insights"])

with tab1:
    st.header("Build Your Prompt")
    
    # Settings
    st.subheader("⚙️ Settings")
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        num_variations = st.slider("Number of variations", 1, 10, 5)
    with col_s2:
        include_quality = st.checkbox("Include Quality Tags", value=True)
    with col_s3:
        clear_prev = st.checkbox("Clear previous results", value=True)
    
    if include_quality:
        with st.expander("🎚️ Quality Tags", expanded=True):
            quality_tags_input = st.text_area(
                "Custom Quality Tags (comma-separated)",
                value=', '.join(QUALITY_TAGS[:8])
            )
            quality_tags = [x.strip() for x in quality_tags_input.split(',') if x.strip()]
    else:
        quality_tags = []
    
    # Custom input field
    st.divider()
    st.subheader("✏️ Custom Content")
    st.markdown("Add any custom terms or phrases (comma or newline separated).")
    custom_input = st.text_area(
        "Custom prompt elements",
        value="",
        placeholder="e.g., dancing, purple eyes, futuristic city"
    )
    
    # Category selections
    st.divider()
    st.subheader("📋 Select Prompt Elements")
    
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
                manual_input = st.text_input(f"Add custom {category}...", key=f"manual_{category}_{idx}")
                selected = [x.strip() for x in manual_input.split(',')] if manual_input else []
            
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
        
        with st.spinner("Generating prompt variations..."):
            positive_variations = generate_variations(
                all_selections, 
                custom_input,
                num_variations=num_variations,
                include_quality=include_quality,
                quality_tags=quality_tags
            )
            negative_variations = [generate_negative_prompt() for _ in range(num_variations)]
            
            st.session_state.positive_variations = positive_variations
            st.session_state.negative_variations = negative_variations
            st.session_state.generated = True
            st.session_state.generation_count += 1
        
        st.success(f"Generated {num_variations} unique variations!")
    
    # Display generated variations
    if st.session_state.generated and st.session_state.positive_variations:
        st.divider()
        st.subheader(f"✨ Generated Variations (Gen #{st.session_state.generation_count})")
        
        for i, (pos, neg) in enumerate(zip(
            st.session_state.positive_variations, 
            st.session_state.negative_variations
        )):
            variation_key = f"var_{i}"
            
            with st.expander(f"Variation {i+1}", expanded=(i==0)):
                st.text_area(
                    f"Positive Prompt #{i+1}",
                    value=pos,
                    height=120,
                    key=f"pos_{i}_{st.session_state.generation_count}"
                )
                
                col_copy1, col_copy2 = st.columns([1, 6])
                with col_copy1:
                    if st.button("📋 Copy", key=f"copy_pos_{i}_{st.session_state.generation_count}"):
                        st.session_state.copied_text = pos
                        st.toast("Copied!")
                with col_copy2:
                    if st.session_state.get('copied_text') == pos:
                        st.text("✓ Copied!")
                
                st.markdown("---")
                st.text_area(
                    f"Negative Prompt #{i+1}",
                    value=neg,
                    height=80,
                    key=f"neg_{i}_{st.session_state.generation_count}"
                )
                
                # ✨ EXPAND THIS PROMPT BUTTON
                st.divider()
                col_expand, col_copy_neg = st.columns([2, 1])
                with col_expand:
                    if st.button(f"✨ Expand This Prompt", key=f"expand_{i}_{st.session_state.generation_count}"):
                        # Generate expansions
                        expansion = expand_prompt(pos)
                        st.session_state.expanded_prompts[variation_key] = expansion
                        st.session_state.show_expansion[variation_key] = True
                        st.rerun()
                with col_copy_neg:
                    if st.button("📋 Copy Neg", key=f"copy_neg_{i}_{st.session_state.generation_count}"):
                        st.session_state.copied_neg = neg
                        st.toast("Negative copied!")
                
                # Show expansions if requested
                if st.session_state.show_expansion.get(variation_key) and variation_key in st.session_state.expanded_prompts:
                    expansion = st.session_state.expanded_prompts[variation_key]
                    suggestions = expansion['suggestions']
                    expanded = expansion['expanded_prompts']
                    
                    st.divider()
                    st.markdown("### ✨ Creative Expansions")
                    st.markdown(f"Based on: *\"{pos[:80]}...\"*")
                    
                    # Suggestions
                    st.markdown("**💡 Suggestions:**")
                    sug_cols = st.columns(3)
                    with sug_cols[0]:
                        st.markdown("**Poses**")
                        for p in suggestions['poses']:
                            st.text(f"• {p}")
                    with sug_cols[1]:
                        st.markdown("**Lighting**")
                        for p in suggestions['lighting']:
                            st.text(f"• {p}")
                    with sug_cols[2]:
                        st.markdown("**Settings**")
                        for p in suggestions['environments']:
                            st.text(f"• {p}")
                    
                    st.markdown("")
                    sug_cols2 = st.columns(3)
                    with sug_cols2[0]:
                        st.markdown("**Emotions**")
                        for p in suggestions['emotions']:
                            st.text(f"• {p}")
                    with sug_cols2[1]:
                        st.markdown("**Clothing**")
                        for p in suggestions['clothing']:
                            st.text(f"• {p}")
                    with sug_cols2[2]:
                        st.markdown("**Stories**")
                        for p in suggestions['stories']:
                            st.text(f"• {p}")
                    
                    # Expanded prompts
                    st.markdown("---")
                    st.markdown("**🎨 Expanded Prompts:**")
                    
                    for j, exp_prompt in enumerate(expanded):
                        with st.expander(f"Expanded Variation {j+1}"):
                            st.text_area(
                                f"Expanded #{j+1}",
                                value=exp_prompt,
                                height=100,
                                key=f"expanded_{variation_key}_{j}"
                            )
                            col_cp, _ = st.columns([1, 5])
                            with col_cp:
                                if st.button("📋 Copy", key=f"copy_exp_{variation_key}_{j}"):
                                    st.session_state.copied_expanded = exp_prompt
                                    st.toast("Copied!")
                            if st.session_state.get('copied_expanded') == exp_prompt:
                                st.text("✓ Copied!")
                    
                    # Close button
                    if st.button("▼ Hide Expansions", key=f"hide_{variation_key}"):
                        st.session_state.show_expansion[variation_key] = False
                        st.rerun()
        
        # Download all as JSON
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
        
        if st.button("🗑️ Clear Results", type="secondary"):
            st.session_state.generated = False
            st.session_state.positive_variations = []
            st.session_state.negative_variations = []
            st.session_state.generation_count = 0
            st.session_state.expanded_prompts = {}
            st.session_state.show_expansion = {}
            st.rerun()

with tab2:
    st.header("📚 Browse Your Dataset")
    # ... (rest of browse tab unchanged)

with tab3:
    st.header("🎲 Random Generator")
    # ... (rest of random tab unchanged)

with tab4:
    st.header("📦 LORA Insights")
    # ... (rest of LORA tab unchanged)

# Footer
st.divider()
st.caption("🎨 Civitai Prompt Generator | Built with Streamlit")
