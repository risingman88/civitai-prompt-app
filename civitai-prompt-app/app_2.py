"""
Civitai Prompt Generator App
A Streamlit-based interactive prompt generator for AI image generation
"""

import streamlit as st
import json
import random
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

# Variation mappings - maps canonical terms to their variations
VARIATION_MAP = {
    'sitting': ['sitting', 'seated', 'sit', 'sits', 'sitting down', 'sits down'],
    'standing': ['standing', 'stand', 'stands', 'standing up', 'stands up'],
    'lying': ['lying', 'lay', 'lying down', 'lies', 'laid', 'lies down'],
    'realistic photograph': ['realistic photograph', 'photorealistic', 'realistic photo', 'photograph', 'photo of', 'realistic', 'real life photo'],
    'large breasts': ['large breasts', 'big breasts', 'huge breasts', 'massive breasts', 'big breast'],
    'smile': ['smile', 'smiling', 'smiles', 'smiled', 'smiling face'],
    'naked': ['naked', 'nude', 'bare', 'undressed', 'unclothed', 'without clothes'],
    'topless': ['topless', 'top less', 'top-less', 'breasts exposed'],
    'outdoor': ['outdoor', 'outside', 'outdoors', 'outside', 'exterior'],
    'beach': ['beach', 'seaside', 'shore', 'sand', 'tropical beach', 'beachside'],
    'sunset': ['sunset', 'sundown', 'golden hour', 'dusk', 'sunset time'],
    'bikini': ['bikini', 'swimsuit', 'swimwear', 'bikini bottom', 'bikini top'],
    'pinup': ['pinup pose', 'pin-up', 'pinup', 'pin-up style'],
    'athletic': ['athletic', 'fit', 'toned', 'fitness', 'sporty'],
    'curvy': ['curvy', 'curvaceous', 'hourglass figure', 'voluptuous', 'curvaceous figure'],
    'blonde': ['blonde', 'blond', 'yellow hair', 'golden hair', 'fair hair'],
    'brunette': ['brunette', 'brown hair', 'chestnut hair', 'dark brown hair'],
    'red hair': ['red hair', 'auburn hair', 'ginger hair', 'redhead'],
    'long hair': ['long hair', 'very long hair', 'waist length hair', 'flowing hair'],
    'short hair': ['short hair', 'short styled hair', 'bob cut', 'pixie cut'],
    'blue eyes': ['blue eyes', 'azure eyes', 'cerulean eyes', 'sapphire eyes'],
    'green eyes': ['green eyes', 'emerald eyes', 'jade eyes', 'forest green eyes'],
    'standing': ['standing', 'stands', 'upright', 'on feet'],
    'kneeling': ['kneeling', 'kneel', 'kneeling down', 'on knees'],
    'squatting': ['squatting', 'squat', 'crouching', 'in a squat'],
    'from behind': ['from behind', 'rear view', 'back view', 'seen from behind'],
    'from above': ['from above', 'bird view', 'aerial view', 'overhead'],
    'close-up': ['close-up', 'closeup', 'close up', 'tight shot'],
    'full body': ['full body', 'full shot', 'entire figure', 'whole body'],
    'portrait': ['portrait', 'portrait shot', 'face focus', 'head and shoulders'],
    'studio': ['studio', 'photo studio', 'indoor studio', 'controlled studio'],
    'indoor': ['indoor', 'inside', 'indoors', 'interior'],
    'forest': ['forest', 'woods', 'trees', 'woodland', 'forested'],
    'dynamic lighting': ['dynamic lighting', 'dramatic lighting', 'striking lighting', 'chiaroscuro'],
    'soft lighting': ['soft lighting', '柔和光线', 'gentle lighting', 'diffused light'],
    'natural lighting': ['natural lighting', 'daylight', 'sunlight', 'natural light'],
}

# Default quality tags
QUALITY_TAGS = [
    'masterpiece', 'best quality', 'highres', 'absurdres', 'ultra realistic',
    'sharp focus', 'fine details', 'highly detailed', '8k', '4k', 'HDR',
    'realism', 'realistic', 'cinematic', 'professional', 'amazing quality',
    'incredible quality', 'stunning', 'beautiful', 'gorgeous', 'perfect'
]

# Default negative prompts
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

def get_all_loras(data):
    """Get all unique LORAs"""
    if data and 'lora_analysis' in data:
        return data['lora_analysis'].get('counts', {})
    return []

def get_random_variation(term):
    """Get a random variation of a term"""
    variations = VARIATION_MAP.get(term.lower(), [term])
    return random.choice(variations)

def generate_variations(selections, num_variations=5, include_quality=True, quality_tags=None):
    """Generate multiple prompt variations with synonyms"""
    variations = []
    
    for _ in range(num_variations):
        parts = []
        
        # Add quality tags (with variations)
        if include_quality:
            selected_quality = random.sample(
                quality_tags or QUALITY_TAGS[:10], 
                min(3, len(quality_tags or QUALITY_TAGS))
            )
            parts.extend(selected_quality)
        
        # Add selections with synonym variations
        for category, items in selections.items():
            for item in items:
                # Get a random variation of this term
                variation = get_random_variation(item)
                parts.append(variation)
        
        variations.append(', '.join(parts))
    
    return variations

def generate_negative_prompt(exclusions=None):
    """Generate negative prompt with some randomization"""
    parts = [DEFAULT_NEGATIVE]
    
    # Add some common exclusions randomly
    common_negatives = [
        "blurry", "blurred", "pixelated", "low resolution", "compression artifacts",
        "bad anatomy", "wrong anatomy", "disfigured", "mutated",
        "extra limbs", "missing limbs", "fused fingers", "too many fingers",
        "ugly", "duplicate", "morbid", "mutilated", "poorly drawn"
    ]
    
    # Add 2-4 random exclusions
    random_negatives = random.sample(common_negatives, random.randint(2, 4))
    parts.extend(random_negatives)
    
    return ', '.join(parts)

# Main app layout
st.title("🎨 Civitai Prompt Generator")
st.markdown("""
Build creative AI prompts with **multiple variations**! Select options from each category 
and generate unique prompts with synonym variations.
""")

# Sidebar - Quick Stats
with st.sidebar:
    st.header("📊 Dataset Stats")
    if data:
        st.metric("Total Images", data.get('metadata', {}).get('total_images', 0))
        st.metric("With Prompts", data.get('metadata', {}).get('with_prompts', 0))
        
        lora_count = len(data.get('lora_analysis', {}).get('counts', {}))
        st.metric("Unique LORAs", lora_count)
        
        st.subheader("🔥 Top Samplers")
        samplers = data.get('technical_settings', {}).get('samplers', {})
        for sampler, count in list(samplers.items())[:5]:
            st.text(f"  {sampler}: {count}")
        
        st.subheader("📦 Base Models")
        bases = {}
        for img in data.get('categorized_images', []):
            bm = img.get('baseModel', 'Unknown')
            bases[bm] = bases.get(bm, 0) + 1
        for base, count in sorted(bases.items(), key=lambda x: -x[1])[:5]:
            st.text(f"  {base}: {count}")
    else:
        st.warning("No data loaded! Make sure parsed_data.json exists in the data/ folder.")

# Main content - Tab interface
tab1, tab2, tab3, tab4 = st.tabs(["🎯 Build Prompt", "📚 Browse Data", "🔀 Random Generator", "📦 LORA Insights"])

with tab1:
    st.header("Build Your Prompt")
    
    # Number of variations slider
    st.subheader("⚙️ Settings")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        num_variations = st.slider(
            "Number of variations to generate",
            min_value=1,
            max_value=10,
            value=5,
            help="How many unique prompts to generate"
        )
    with col_s2:
        include_quality = st.checkbox("Include Quality Tags", value=True, help="Add quality tags like 'masterpiece', '8k', etc.")
    
    # Quality tags input
    if include_quality:
        with st.expander("🎚️ Quality Tags", expanded=True):
            quality_tags_input = st.text_area(
                "Custom Quality Tags (comma-separated)",
                value=', '.join(QUALITY_TAGS[:8]),
                help="Edit these quality tags that will be randomly included"
            )
            quality_tags = [x.strip() for x in quality_tags_input.split(',') if x.strip()]
    else:
        quality_tags = []
    
    # Category selections
    st.divider()
    st.subheader("📋 Select Prompt Elements")
    
    # Initialize session state for selections
    if 'selections' not in st.session_state:
        st.session_state.selections = {}
    
    all_selections = {}
    
    # Create columns for categories
    col1, col2 = st.columns(2)
    
    for idx, (category, label) in enumerate(CATEGORIES.items()):
        # Alternate between columns
        with col1 if idx % 2 == 0 else col2:
            st.markdown(f"**{label}**")
            
            # Get available items for this category
            items = get_category_items(category, data)
            
            if items:
                # Multi-select for items
                selected = st.multiselect(
                    f"Select {category}...",
                    options=items,
                    key=f"select_{category}",
                    help=f"Found {len(items)} unique {category} terms"
                )
            else:
                # Allow manual input
                manual_input = st.text_input(
                    f"Add custom {category}...",
                    key=f"manual_{category}",
                    placeholder="e.g., dancing, running, etc."
                )
                selected = [x.strip() for x in manual_input.split(',')] if manual_input else []
            
            if selected:
                all_selections[category] = selected
    
    # Generate button
    st.divider()
    if st.button("🚀 Generate Variations", type="primary", use_container_width=True):
        with st.spinner("Generating prompt variations..."):
            # Generate variations
            positive_variations = generate_variations(
                all_selections, 
                num_variations=num_variations,
                include_quality=include_quality,
                quality_tags=quality_tags
            )
            negative_variations = [generate_negative_prompt() for _ in range(num_variations)]
            
            # Store in session state
            st.session_state.positive_variations = positive_variations
            st.session_state.negative_variations = negative_variations
            st.session_state.generated = True
        
        st.success(f"Generated {num_variations} unique variations!")
    
    # Display generated variations
    if 'generated' in st.session_state and st.session_state.get('generated'):
        st.divider()
        st.subheader("✨ Generated Variations")
        
        for i, (pos, neg) in enumerate(zip(
            st.session_state.positive_variations, 
            st.session_state.negative_variations
        )):
            with st.expander(f"Variation {i+1}", expanded=(i==0)):
                st.text_area(
                    f"Positive Prompt #{i+1}",
                    value=pos,
                    height=120,
                    key=f"pos_{i}"
                )
                
                col_copy1, col_copy2 = st.columns([1, 6])
                with col_copy1:
                    if st.button("📋 Copy", key=f"copy_pos_{i}"):
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
                    key=f"neg_{i}"
                )
                
                col_copy3, col_copy4 = st.columns([1, 6])
                with col_copy3:
                    if st.button("📋 Copy Neg", key=f"copy_neg_{i}"):
                        st.session_state.copied_neg = neg
                        st.toast("Negative copied!")
                with col_copy4:
                    if st.session_state.get('copied_neg') == neg:
                        st.text("✓ Copied!")
        
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

with tab2:
    st.header("📚 Browse Your Dataset")
    
    if data and 'categorized_images' in data:
        # Filter options
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filter_base = st.selectbox(
                "Filter by Base Model",
                options=['All'] + sorted(set(img.get('baseModel', 'Unknown') for img in data['categorized_images']))
            )
        with col_f2:
            search_term = st.text_input("Search Prompts", placeholder="Search for keywords...")
        
        # Filter images
        filtered = data['categorized_images']
        if filter_base != 'All':
            filtered = [img for img in filtered if img.get('baseModel') == filter_base]
        if search_term:
            search = search_term.lower()
            filtered = [img for img in filtered if search in img.get('prompt', '').lower()]
        
        st.metric("Showing", f"{len(filtered)} images")
        
        # Display images
        for img in filtered[:20]:  # Show first 20
            with st.expander(f"ID: {img.get('id')} - {img.get('baseModel', 'Unknown')}"):
                st.text("Prompt:")
                st.code(img.get('prompt', 'N/A')[:500])
                
                if img.get('negative'):
                    st.text("Negative:")
                    st.code(img.get('negative', 'N/A')[:300])
                
                if img.get('loras'):
                    st.text("LORAs:")
                    for lora in img.get('loras', [])[:3]:
                        st.text(f"  - {lora.get('name', 'Unknown')}: {lora.get('weight', 1.0)}")
                
                st.text(f"Settings: {img.get('settings', {}).get('sampler', 'N/A')} | Steps: {img.get('settings', {}).get('steps', 'N/A')} | CFG: {img.get('settings', {}).get('cfgScale', 'N/A')}")
    else:
        st.warning("No data available!")

with tab3:
    st.header("🎲 Random Generator")
    st.markdown("Generate a random prompt from your dataset as inspiration!")
    
    if data and 'categorized_images' in data:
        if st.button("🎲 Generate Random Prompt", type="primary"):
            random_img = random.choice(data['categorized_images'])
            
            st.subheader("✨ Random Inspiration")
            st.code(random_img.get('prompt', 'N/A')[:800])
            
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                st.text("Negative:")
                st.code(random_img.get('negative', 'N/A')[:300])
            with col_r2:
                st.text("Settings:")
                settings = random_img.get('settings', {})
                st.json(settings)
            
            st.text(f"Source: {random_img.get('username', 'Unknown')} | Base: {random_img.get('baseModel', 'Unknown')}")
            
            # Copy button
            if st.button("📋 Copy This Prompt"):
                st.session_state.copied_prompt = random_img.get('prompt', '')
                st.toast("Copied!")
            
            if 'copied_prompt' in st.session_state:
                st.text_area("Copied Prompt", value=st.session_state.copied_prompt, height=100)
    else:
        st.warning("No data available!")

with tab4:
    st.header("📦 LORA Insights")
    
    if data and 'lora_analysis' in data:
        lora_data = data['lora_analysis']
        
        # Top LORAs
        st.subheader("🔥 Top 20 Most Used LORAs")
        loras = lora_data.get('counts', {})
        lora_df = [{'LORA': name, 'Count': count, 'Avg Weight': round(lora_data.get('avg_weights', {}).get(name, 0), 2)}
                   for name, count in list(loras.items())[:20]]
        
        if lora_df:
            st.dataframe(lora_df, use_container_width=True)
        
        # LORA combinations
        st.subheader("🔀 Top LORA Combinations")
        combos = lora_data.get('top_combinations', [])
        for i, (combo, count) in enumerate(combos[:10]):
            st.text(f"{i+1}. {' + '.join(combo[:3])}... ({count} images)")
        
        # Technical settings
        st.subheader("⚙️ Technical Settings")
        tech = data.get('technical_settings', {})
        
        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            st.metric("Avg Steps", f"{tech.get('steps_avg', 0):.1f}")
            st.text(f"Range: {tech.get('steps_range', (0,0))[0]}-{tech.get('steps_range', (0,0))[1]}")
        with col_t2:
            st.metric("Avg CFG Scale", f"{tech.get('cfg_avg', 0):.1f}")
            st.text(f"Range: {tech.get('cfg_range', (0,0))[0]}-{tech.get('cfg_range', (0,0))[1]}")
        with col_t3:
            st.metric("Unique Samplers", len(tech.get('samplers', {})))
    else:
        st.warning("No LORA data available!")

# Footer
st.divider()
st.caption("""
🎨 Civitai Prompt Generator | Built with Streamlit
Data sourced from your collected Civitai favorites and collections
""")
