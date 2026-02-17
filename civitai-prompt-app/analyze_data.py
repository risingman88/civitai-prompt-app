#!/usr/bin/env python3
"""
Civitai Prompt Analyzer
Analyzes metadata and creates categorized data for the prompt generator app
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

# Load metadata
with open('/home/helper/prompt-builder/all-images-metadata.json', 'r') as f:
    images = json.load(f)

# Category patterns for prompt analysis
CATEGORY_PATTERNS = {
    'subject': [
        r'\b(1girl|1boy|2girls|2boys|female|futana?ri|woman|man|girl|boy)\b',
        r'\b(1femboy|solo|femboy)\b',
    ],
    'pose': [
        r'\b(sitting|seated|sit|stands?ing|stand|lying|lay|pinup pose|kneeling|kneel|'
        r'squatting|squat|legs apart|legs spread|on back|on stomach|bent over|'
        r'from behind|from above|from front|profile|side view|front view)\b',
    ],
    'environment': [
        r'\b(beach|tropical|outdoor|indoor|studio|room|forest|desert|mountain|'
        r'city|night|day|sunset|sunrise|dawn|dusk|sky|clouds|grass|palm|'
        r'resort|ocean|sea|lake|pool|bed|chair|couch|wall|floor|background)\b',
    ],
    'body_features': [
        r'\b(large breasts|big breasts|huge breasts|massive breasts|small breasts|flat chest|'
        r'athletic|thin|curvy|curvaceous|wide hips|tiny waist|petite|slim|fit|fitness|'
        r'muscular|toned|plump|chubby|hourglass|big ass|flat ass|small breasts)\b',
    ],
    'hair': [
        r'\b(long hair|short hair|medium hair|blonde|brunette|red hair|black hair|'
        r'blue hair|pink hair|green hair|white hair|grey hair|curly hair|wavy hair|'
        r'straight hair|bald|shaved|ponytail|braids|pixie cut|long wavy|short pixie)\b',
    ],
    'clothing': [
        r'\b(bikini|swimsuit|naked|nude|topless|clothed|jeans|shirt|dress|'
        r'skirt|blouse|pants|shorts|underwear|bra|thong|lingerie|bodysuit|'
        r'costume|uniform|suit|tie|hat|glasses|jewelry|necklace|earrings|'
        r'bracelet|ring|tiara|crown|wings|halo|aura)\b',
    ],
    'lighting': [
        r'\b(sunset|sunrise|dramatic lighting|studio lighting|soft lighting|'
        r'natural lighting|neon|backlit|rim light|godrays|shadow|'
        r'high contrast|low key|high key|golden hour|blue hour|night|'
        r'dark|bright|dim|spotlight)\b',
    ],
    'art_style': [
        r'\b(realistic photograph|photorealistic|realistic photo|photograph|photo of|'
        r'anime|manga|illustration|digital painting|oil painting|watercolor|'
        r'3d render|cg|cartoon|comic|sketch|draft)\b',
    ],
    'quality': [
        r'\b(8k|4k|high resolution|highres|absurdres|masterpiece|best quality|'
        r'amazing quality|ultra realistic|sharp focus|fine details|detailed|'
        r'HDR|realism|realistic|sharp|clear|crisp|ultra detailed)\b',
    ],
    'camera': [
        r'\b(75mm|85mm|50mm|35mm|wide angle|telephoto|macro|depth of field|'
        r'DOF|bokeh|sharp focus|soft focus|blurry|close-up|wide shot|'
        r'full body|portrait|cowboy shot|headshot|medium shot|long shot|'
        r'Technicolor|Panavision|Cinemascope|Kodak|Film)\b',
    ],
    'composition': [
        r'\b(close-up|closeup|medium shot|wide shot|full body|headshot|cowboy shot|'
        r'portrait|bust|waist up|thigh up|full shot|aerial|worm|'
        r'(ass|breast|face|body) focus|solo focus)\b',
    ],
    'emotion': [
        r'\b(smiling|smile|laughing|laughing|crying|sad|angry|happy|sexy|'
        r'seductive|confident|shy|nervous|relaxed|calm|angry|mad|pleased|'
        r'blushing|blush|embarrassed|fear|surprised|worried|confused)\b',
    ],
    'skin_features': [
        r'\b(sweaty|wet|shiny|oily|dry|pale|fair|dark|tan|bronzed|glowing|'
        r'radiant|matte|smooth|rough|soft|velvety|clear|flawless|perfect skin|'
        r'skin texture)\b',
    ],
    'physical_details': [
        r'\b(abs|muscles|muscular|veins|tattoos|tattoo|piercings|piercing|'
        r'scars|marks|freckles|moles|birthmark|dimples|sweat|sweaty|'
        r'breathing|veiny|hairy|hairless|smooth skin)\b',
    ],
    'special_effects': [
        r'\b(godrays|particles|sparkles|glitter|smoke|fog|mist|fire|flames|'
        r'water|rain|snow|wind|leaves|petals|magic|sparkle|glow|shimmer)\b',
    ],
}

# Common negative prompt patterns
NEGATIVE_CATEGORIES = {
    'quality': [
        r'\b(worst quality|low quality|poor quality|bad quality|lowres|blur|blurry|'
        r'blurred|pixelated|upscaled|compression artifacts|jpeg artifacts)\b',
    ],
    'anatomy': [
        r'\b(bad anatomy|wrong anatomy|disfigured|deformed|mutated|ugly|'
        r'missing (limbs|fingers|toes|arms|legs)|extra (limbs|fingers|toes)|'
        r'fused (fingers|limbs)|too many fingers|fewer fingers|'
        r'bad hands|bad feet|bad face|ugly face|weird face)\b',
    ],
    'style': [
        r'\b(3d|cartoon|anime|manga|comic|sketch|drawing|painting|'
        r'illustrated|clipart|vector|watermark|signature|text|logo)\b',
    ],
    'unwanted_features': [
        r'\b(fat|chubby|overweight|thin|skinny|malnourished|skeletal|'
        r'child|kid|teen|underage|adult|mature)\b',
    ],
    'censoring': [
        r'\b(censor|censored|bar censor|mosaic|blur|covered|hidden)\b',
    ],
}


def categorize_prompt(prompt):
    """Extract categories from a prompt"""
    if not prompt:
        return {}
    
    prompt_lower = prompt.lower()
    categories = {}
    
    for category, patterns in CATEGORY_PATTERNS.items():
        matches = []
        for pattern in patterns:
            found = re.findall(pattern, prompt_lower, re.IGNORECASE)
            for match in found:
                # Handle both tuple and string matches
                if isinstance(match, tuple):
                    matches.extend([m.strip() for m in match if m.strip()])
                else:
                    matches.append(match.strip())
        if matches:
            # Remove duplicates and clean up
            matches = list(set([m.strip() for m in matches if m.strip() and isinstance(m, str)]))
            if matches:
                categories[category] = matches
    
    return categories


def analyze_negative_prompt(negative):
    """Categorize negative prompt exclusions"""
    if not negative:
        return {}
    
    neg_lower = negative.lower()
    exclusions = {}
    
    for category, patterns in NEGATIVE_CATEGORIES.items():
        matches = []
        for pattern in patterns:
            found = re.findall(pattern, neg_lower, re.IGNORECASE)
            for match in found:
                if isinstance(match, tuple):
                    matches.extend([m.strip() for m in match if m.strip()])
                else:
                    matches.append(match.strip())
        if matches:
            matches = list(set([m.strip() for m in matches if m.strip() and isinstance(m, str)]))
            if matches:
                exclusions[category] = matches
    
    return exclusions


def extract_variations(all_prompts):
    """Extract all variations/synonyms for each term"""
    variations = defaultdict(set)
    
    for prompt in all_prompts:
        if not prompt:
            continue
        
        # Extract n-grams and individual words
        words = re.findall(r'\b\w+\b', prompt.lower())
        
        # Common variations mapping
        variation_map = {
            'sitting': ['seated', 'sit', 'sits', 'sitting down'],
            'standing': ['stand', 'stands', 'standing up'],
            'lying': ['lay', 'lying down', 'lies', 'laid'],
            'realistic': ['realistic', 'photorealistic', 'photograph', 'photo', 'real life'],
            'large breasts': ['large breasts', 'big breasts', 'big breast', 'huge breasts'],
            'smile': ['smiling', 'smile', 'smiles', 'smiled'],
            'naked': ['naked', 'nude', 'bare', 'undressed', 'unclothed'],
            'topless': ['topless', 'top less', 'no top'],
            'outdoor': ['outdoor', 'outside', 'outdoors', 'outside'],
            'indoor': ['indoor', 'inside', 'indoors', 'inside'],
            'beach': ['beach', 'seaside', 'shore', 'sand'],
            'sunset': ['sunset', 'sundown', 'golden hour', 'dusk'],
        }
        
        for canonical, variants in variation_map.items():
            for variant in variants:
                if variant in prompt.lower():
                    variations[canonical].add(variant)
                    for v in variants:
                        variations[canonical].add(v)
    
    return {k: list(v) for k, v in variations.items()}


def analyze_loras(images):
    """Analyze LORA combinations and statistics"""
    lora_counts = Counter()
    lora_by_base = defaultdict(Counter)
    lora_weights = defaultdict(list)
    combinations = Counter()
    
    for img in images:
        base = img.get('baseModel', 'Unknown')
        loras = img.get('loras', [])
        
        lora_names = []
        for lora in loras:
            name = lora.get('name', 'Unknown')
            weight = lora.get('weight', 1.0)
            if name and name != 'Unknown':
                lora_counts[name] += 1
                lora_by_base[base][name] += 1
                lora_weights[name].append(weight)
                lora_names.append(name)
        
        if len(lora_names) > 1:
            combo_key = tuple(sorted(lora_names))
            combinations[combo_key] += 1
    
    # Calculate average weights
    avg_weights = {name: sum(weights)/len(weights) for name, weights in lora_weights.items()}
    
    return {
        'counts': dict(lora_counts.most_common(50)),
        'by_base': {k: dict(v) for k, v in lora_by_base.items()},
        'avg_weights': avg_weights,
        'top_combinations': combinations.most_common(20),
    }


def analyze_technical_settings(images):
    """Analyze sampler, steps, cfgScale distributions"""
    samplers = Counter()
    steps = []
    cfg_scales = []
    
    for img in images:
        if img.get('sampler'):
            samplers[img['sampler']] += 1
        if img.get('steps'):
            steps.append(img['steps'])
        if img.get('cfgScale'):
            cfg_scales.append(img['cfgScale'])
    
    return {
        'samplers': dict(samplers.most_common(20)),
        'steps_avg': sum(steps)/len(steps) if steps else 0,
        'steps_range': (min(steps) if steps else 0, max(steps) if steps else 0),
        'cfg_avg': sum(cfg_scales)/len(cfg_scales) if cfg_scales else 0,
        'cfg_range': (min(cfg_scales) if cfg_scales else 0, max(cfg_scales) if cfg_scales else 0),
    }


def main():
    print("Analyzing Civitai metadata...")
    
    # Analyze all images
    analyzed = []
    all_prompts = []
    
    for img in images:
        prompt = img.get('positivePrompt', '')
        negative = img.get('negativePrompt', '')
        
        categories = categorize_prompt(prompt)
        exclusions = analyze_negative_prompt(negative)
        
        analyzed.append({
            'id': img.get('id'),
            'username': img.get('username'),
            'baseModel': img.get('baseModel'),
            'prompt': prompt,
            'negative': negative,
            'categories': categories,
            'exclusions': exclusions,
            'loras': img.get('loras', []),
            'checkpoint': img.get('checkpoint'),
            'settings': {
                'sampler': img.get('sampler'),
                'steps': img.get('steps'),
                'cfgScale': img.get('cfgScale'),
                'seed': img.get('seed'),
                'width': img.get('width'),
                'height': img.get('height'),
            }
        })
        
        if prompt:
            all_prompts.append(prompt)
    
    # Extract variations
    print("Extracting variations...")
    variations = extract_variations(all_prompts)
    
    # Analyze LORAs
    print("Analyzing LORA combinations...")
    lora_analysis = analyze_loras(images)
    
    # Analyze technical settings
    print("Analyzing technical settings...")
    technical = analyze_technical_settings(images)
    
    # Compile final data
    result = {
        'metadata': {
            'total_images': len(images),
            'with_prompts': len(all_prompts),
            'generated_at': str(Path(__file__).stat().st_mtime) if Path(__file__).exists() else 'N/A',
        },
        'categorized_images': analyzed,
        'variations': variations,
        'lora_analysis': lora_analysis,
        'technical_settings': technical,
        'category_patterns': CATEGORY_PATTERNS,
        'negative_categories': NEGATIVE_CATEGORIES,
    }
    
    # Save parsed data
    output_path = Path('/home/helper/prompt-builder/civitai-prompt-app/data/parsed_data.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"Saved to {output_path}")
    print(f"\nSummary:")
    print(f"  Total images: {len(images)}")
    print(f"  With prompts: {len(all_prompts)}")
    print(f"  Unique LORAs: {len(lora_analysis['counts'])}")
    print(f"  Samplers: {len(technical['samplers'])}")
    print(f"  Variations found: {len(variations)}")
    
    return result


if __name__ == '__main__':
    main()
