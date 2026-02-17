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

# Variation mappings
VARIATION_MAP = {
    'sitting': ['sitting', 'seated', 'sit', 'sits', 'sitting down'],
    'standing': ['standing', 'stand', 'stands', 'standing up'],
    'lying': ['lying', 'lay', 'lying down', 'lies', 'laid'],
    'realistic photograph': ['realistic photograph', 'photorealistic', 'realistic photo', 'photograph', 'photo of', 'realistic'],
    'large breasts': ['large breasts', 'big breasts', 'huge breasts', 'massive breasts'],
    'smile': ['smile', 'smiling', 'smiles', 'smiled'],
    'naked': ['naked', 'nude', 'bare', 'undressed', 'unclothed'],
    'topless': ['topless', 'topless', 'top less'],
    'outdoor': ['outdoor', 'outside', 'outdoors'],
    'beach': ['beach', 'seaside', 'shore', 'sand', 'tropical beach'],
    'sunset': ['sunset', 'sundown', 'golden hour', 'dusk'],
    'bikini': ['bikini', 'swimsuit', 'swimwear'],
    'pinup': ['pinup pose', 'pin-up', 'pinup'],
    'athletic': ['athletic', 'fit', 'toned', 'fitness'],
    'curvy': ['curvy', 'curvaceous', 'hourglass figure', 'voluptuous'],
    'blonde': ['blonde', 'blond', 'yellow hair', 'golden hair'],
    'brunette': ['brunette', 'brown hair', 'chestnut hair'],
    'long hair': ['long hair', 'very long hair', 'waist length hair'],
    'short hair': ['short hair', 'short styled hair'],
    'blue eyes': ['blue eyes', 'azure eyes', 'cerulean eyes'],
    'green eyes': ['green eyes', 'emerald eyes', 'jade eyes'],
}

# Default quality tags
QUALITY_TAGS = [
    'masterpiece', 'best quality', 'highres', 'absurdres', 'ultra realistic',
    'sharp focus', 'fine details', 'highly detailed', '8k', '4k', 'HDR',
    'realism', 'realistic', 'cinematic', 'professional'
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
    return {}

def generate_prompt(selections, include_quality=True, quality_tags=None):
    """Generate a prompt from selections"""
    parts = []
    
    # Add quality tags first (typical for Civitai prompts)
    if include_quality:
        parts.extend(quality_tags or random.sample(QUALITY_TAGS, min(3, len(QUALITY_TAGS))))
    
    # Add selections by category order
    for category in CATEGORIES.keys():
        if category in selections and selections[category]:
            for item in selections[category]:
                parts.append(item)
    
    return ', '.join(parts)

def generate_negative_prompt(exclusions):
    """Generate negative prompt from exclusions"""
    parts = [DEFAULT_NEGATIVE]
    for category, items in exclusions.items():
        if items:
            parts.extend(items)
    return ', '.join(parts)

# Main app layout
st.title("🎨 Civitai Prompt Generator")
st.markdown("""
This app analyzes your collected Civitai image metadata to help you generate 
creative AI prompts. Select options from each category to build your perfect prompt!
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
    
    # Initialize session state for selections
    if 'selections' not in st.session_state:
        st.session_state.selections = {}
    
    # Create columns for categories
    col1, col2 = st.columns(2)
    
    all_selections = {}
    
    for idx, (category, label) in enumerate(CATEGORIES.items()):
        # Alternate between columns
        with col1 if idx % 2 == 0 else col2:
            st.subheader(label)
            
            # Get available items for this category
            items = get_category_items(category, data)
            
            if items:
                # Multi-select for items
                selected = st.multiselect(
                    f"Select {category}...",
                    options=items,
                    key=f"select_{category}",
                    help=f"Found {len(items)} unique {category} terms in your dataset"
                )
            else:
                # Allow manual input
                manual_input = st.text_area(
                    f"Add custom {category}...",
                    key=f"manual_{category}",
                    help="No matches found in dataset - add your own!"
                )
                selected = [x.strip() for x in manual_input.split(',') if x.strip()] if manual_input else []
            
            if selected:
                all_selections[category] = selected
    
    # Quality settings
    st.divider()
    st.subheader("⚙️ Quality Settings")
    
    col_q1, col_q2 = st.columns(2)
    with col_q1:
        include_quality = st.checkbox("Include Quality Tags", value=True)
    with col_q2:
        quality_tags_input = st.text_area(
            "Custom Quality Tags (comma-separated)",
            value=', '.join(QUALITY_TAGS[:5]),
            help="Common quality tags for AI image generation"
        )
    
    quality_tags = [x.strip() for x in quality_tags_input.split(',') if x.strip()]
    
    # Generate button
    if st.button("🚀 Generate Prompt", type="primary", use_container_width=True):
        positive = generate_prompt(all_selections, include_quality, quality_tags)
        negative = generate_negative_prompt({})
        
        st.session_state.generated_positive = positive
        st.session_state.generated_negative = negative
        
        st.success("Prompt generated!")
    
    # Display generated prompts
    if 'generated_positive' in st.session_state:
        st.divider()
        st.subheader("✨ Generated Prompt")
        
        st.text_area(
            "Positive Prompt",
            value=st.session_state.generated_positive,
            height=150,
            key="positive_output"
        )
        
        if st.button("📋 Copy Positive", key="copy_pos"):
            st.toast("Copied to clipboard!")
        
        st.subheader("❌ Negative Prompt")
        
        st.text_area(
            "Negative Prompt",
            value=st.session_state.generated_negative,
            height=100,
            key="negative_output"
        )
        
        if st.button("📋 Copy Negative", key="copy_neg"):
            st.toast("Copied to clipboard!")

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
            
            # Copy buttons
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
