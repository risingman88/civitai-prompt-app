# 🎨 Civitai Prompt Generator

An interactive web app for analyzing and generating AI image prompts from your Civitai favorites/collections.

## Features

- **📊 Dataset Analysis**: Automatically categorizes prompts by subject, pose, environment, lighting, etc.
- **🎯 Interactive Builder**: Build prompts by selecting from your collected data
- **🎲 Random Generator**: Get inspired by random prompts from your dataset
- **📦 LORA Insights**: See which LORAs and combinations are most common
- **⚙️ Technical Stats**: Average steps, CFG scales, samplers used

## Tech Stack

- **Python 3.8+**
- **Streamlit** - Web framework (no HTML/CSS knowledge needed)
- **JSON** - Data storage
- **Deployable**: Vercel, Streamlit Cloud, any VPS

## 📁 Folder Structure

```
civitai-prompt-app/
├── app.py              # Main Streamlit application
├── analyze_data.py     # Script to parse and categorize metadata
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── .gitignore        # Git ignore rules
└── data/
    └── parsed_data.json   # Categorized data (auto-generated)
```

## 🚀 Quick Start

### Option 1: Run Locally

```bash
# 1. Navigate to the app folder
cd civitai-prompt-app

# 2. Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py

# 5. Open browser at http://localhost:8501
```

### Option 2: Run with Python directly

```bash
cd civitai-prompt-app
python -m streamlit run app.py
```

## 📦 Deployment Options

### Deploy to Streamlit Cloud (FREE)

1. Push this folder to a GitHub repository
2. Go to https://share.streamlit.io
3. Connect your GitHub and select this repository
4. Set:
   - Main file path: `app.py`
   - Python version: 3.9+
5. Click Deploy!

### Deploy to Vercel (FREE)

1. Create a `vercel.json` file:
```json
{
  "buildCommand": "pip install -r requirements.txt",
  "devCommand": "streamlit run app.py",
  "installCommand": "pip install -r requirements.txt"
}
```

2. Push to GitHub
3. Import to Vercel

### Deploy to VPS (Ubuntu/Debian)

```bash
# 1. Install Python
sudo apt update
sudo apt install python3 python3-pip python3-venv

# 2. Upload files (via SCP)
scp -r civitai-prompt-app user@your-server:/path/to/

# 3. SSH to server
ssh user@your-server

# 4. Setup
cd civitai-prompt-app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Run with systemd or screen
# Option A: Run in background with screen
screen -S streamlit
source venv/bin/activate
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
# Press Ctrl+A then D to detach

# Option B: Create systemd service (see below)
```

### Create Systemd Service (VPS)

Create `/etc/systemd/system/streamlit.service`:

```ini
[Unit]
Description=Civitai Prompt Generator
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/civitai-prompt-app
Environment="PATH=/path/to/civitai-prompt-app/venv/bin"
ExecStart=/path/to/civitai-prompt-app/venv/bin/streamlit run app.py --server.port 8501 --server.address 127.0.0.1

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable streamlit
sudo systemctl start streamlit
sudo systemctl status streamlit
```

## 🔧 Customization

### Adding Your Own Metadata

1. Place your `all-images-metadata.json` in the `data/` folder
2. Run the analyzer:
```bash
python analyze_data.py
```
3. The app will automatically use the new parsed data

### Modifying Categories

Edit `app.py` and modify the `CATEGORIES` dictionary:

```python
CATEGORIES = {
    'your_category': '🎯 Your Category Name',
    ...
}
```

## 📊 Data Format

The app expects `data/parsed_data.json` with this structure:

```json
{
  "metadata": {
    "total_images": 95,
    "with_prompts": 88
  },
  "categorized_images": [
    {
      "id": 12345,
      "prompt": "...",
      "categories": {
        "subject": ["1girl"],
        "pose": ["sitting"],
        "environment": ["beach"]
      },
      "loras": [{"name": "LORA Name", "weight": 0.8}],
      "settings": {"sampler": "Euler a", "steps": 30}
    }
  ],
  "lora_analysis": {
    "counts": {"LORA Name": 15},
    "top_combinations": [...]
  }
}
```

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'streamlit'"

```bash
pip install streamlit
```

### "Port already in use"

```bash
# Kill existing processes
lsof -i :8501
kill <PID>
```

### Data not loading

Check that `data/parsed_data.json` exists. If not, run:
```bash
python analyze_data.py
```

## 📝 License

MIT License - Feel free to use and modify!

## 🙏 Credits

Built with ❤️ using Streamlit
Data sourced from Civitai collections
