# SmartInsight AI — Behavioral Intelligence Advisor

A modern, dark-themed Streamlit application that predicts stress, addiction, and productivity risk from unified smartphone, sleep, and lifestyle data across India, USA, and Global cohorts.

**🚀 Live Demo:** [SmartInsight AI on Streamlit Cloud](https://smartinsight-ai.streamlit.app)

## ✨ Features

- **AI-Powered Risk Prediction** — RandomForest models for stress, addiction risk, and productivity scoring
- **Multi-Region Analytics** — India vs USA vs Global comparative behavioral insights
- **Behavioral Archetypes** — KMeans clustering identifies 5 distinct user personas
- **Explainable AI Lab** — Feature importance charts + sensitivity analysis for every prediction
- **Interactive Scenario Simulation** — "What-if" simulator for lifestyle interventions
- **Smart Insight Engine** — Personalized, model-aware recommendations ranked by impact
- **16,000 Records Dataset** — Unified behavioral intelligence from 24+ lifestyle dimensions
- **Dark Theme UI** — Glassmorphic design with smooth animations

## 📊 Tabs & Pages

| Page | Purpose |
|------|---------|
| **Home** | Build your profile, view stress/addiction/productivity scores |
| **Region-Aware Analytics** | Compare your metrics across geographic cohorts |
| **Students vs Professionals** | Behavioral split-screen analysis |
| **AI Risk Prediction** | Model outputs, real-time gauges, percentile rankings |
| **Behavioral Archetypes** | Which behavioral cluster matches you best? |
| **Explainable AI** | Drill into feature importance and model sensitivity |
| **Scenario Simulation** | Test lifestyle changes before committing |
| **Smart Insight Engine** | Get 3–5 high-impact personalized recommendations |

## 🛠️ Tech Stack

- **Framework:** Streamlit 1.55+
- **ML Models:** scikit-learn (RandomForest, KMeans)
- **Visualization:** Plotly (interactive charts)
- **Data:** Pandas, NumPy
- **Deployment:** Streamlit Cloud (free, auto-scaling, zero-downtime)

## 📦 Installation

### Local Setup

```bash
git clone https://github.com/yourusername/smartinsight-ai.git
cd smartinsight-ai
python -m pip install -r requirements.txt
streamlit run Home.py
```

Then open [http://localhost:8501](http://localhost:8501)

### First Run

On first launch, the app will automatically:
1. Load the raw behavioral dataset
2. Train the three ML models (stress, addiction, productivity)
3. Run KMeans clustering for archetypes
4. Cache all artifacts for fast subsequent loads

This takes ~2–3 minutes on first load, then runs instantly.

## 🌐 Deploy to Streamlit Cloud (Free)

### Option 1: Deploy Directly from GitHub

1. Push this repository to GitHub (if not already done)
2. Visit [streamlit.io/cloud](https://share.streamlit.io)
3. Click "New App" → Connect your GitHub repo
4. Select `Home.py` as the main file
5. Click "Deploy" — your app goes live in 2 minutes!

Your live URL will be: `https://yourusername-smartinsight-ai.streamlit.app`

### Option 2: Manual GitHub Setup & Deploy

```bash
# Initialize git (if not done)
git init
git add .
git commit -m "Initial commit: SmartInsight AI deployment"
git branch -M main
git remote add origin https://github.com/yourusername/smartinsight-ai.git
git push -u origin main

# Then deploy via streamlit.io/cloud
```

## 📋 Project Structure

```
smartinsight-ai/
├── Home.py                              # Landing page + profile builder
├── requirements.txt                     # Python dependencies
├── unified_behavioral_intelligence.csv  # Raw dataset (16,000 records)
├── .streamlit/
│   └── config.toml                     # Streamlit config (dark theme)
├── pages/
│   ├── 1_Region_Aware_Analytics.py
│   ├── 2_Students_vs_Professionals.py
│   ├── 3_AI_Risk_Prediction.py
│   ├── 4_Behavioral_Archetypes.py
│   ├── 5_Explainable_AI.py
│   ├── 6_Scenario_Simulation.py
│   └── 7_Smart_Insight_Engine.py
├── src/
│   ├── bootstrap.py          # Path initialization
│   ├── charts.py             # Plotly visualizations
│   ├── config.py             # App configuration & constants
│   ├── data.py               # Data loading & cleaning
│   ├── inference.py          # Model prediction pipeline
│   ├── insights.py           # Smart recommendation engine
│   ├── session.py            # Streamlit session management
│   ├── styles.py             # Dark theme CSS & components
│   ├── training.py           # ML model training & artifacts
│   └── analytics.py          # Cohort analysis utilities
├── data/
│   └── processed_behavioral_data.csv    # Cached processed dataset
├── models/
│   ├── stress_model.pkl           # Generated on first run
│   ├── addiction_model.pkl        # Generated on first run
│   ├── productivity_model.pkl     # Generated on first run
│   ├── preprocessor.pkl          # Feature transformer
│   ├── cluster_bundle.pkl        # KMeans clustering
│   └── model_metadata.json       # Model metadata
└── scripts/
    └── train_models.py             # Manual model retraining script
```

## 🧠 How It Works

### The Three AI Models

1. **Stress Level Predictor** (Regression)
   - Output: 0.00–1.00 (0 = calm, 1.00 = extreme stress)
   - Inputs: screen time, sleep, caffeine, notifications, activity level
   - Algorithm: RandomForestRegressor (100 estimators)

2. **Addiction Risk Classifier** (Classification)
   - Output: Low / Moderate / High
   - Inputs: gaming hours, social media, screen time, notifications
   - Algorithm: RandomForestClassifier

3. **Productivity Predictor** (Classification)
   - Output: 0–100 (stability score)
   - Inputs: sleep quality, stress, physical activity, work intensity
   - Algorithm: RandomForestClassifier

### Behavioral Archetypes (KMeans, k=5)

- **Burnout Users** — High screen, low sleep, elevated stress
- **Balanced Users** — Healthy across all dimensions
- **Hyper-Connected Users** — High notifications, social media intensity
- **Sleep-Deprived Achievers** — High productivity but chronic sleep deficit
- **Low-Risk Users** — Minimal digital stress, optimal lifestyle

## 🔧 Local Development

### Retrain Models

```bash
python scripts/train_models.py
```

This regenerates all `.pkl` artifacts from the raw CSV.

### Run Tests

```bash
python -m unittest discover -s tests -v
```

### Environment Variables (Optional)

No API keys or secrets required! The app works entirely offline.

## ⚡ Performance Notes

- **First load:** ~2–3 minutes (model training + caching)
- **Subsequent loads:** <1 second (from cache)
- **Streamlit Cloud:** Auto-redeployment with zero downtime
- **Max concurrent users:** Unlimited on Streamlit Cloud free tier
- **Data size:** 16,000 records × 24 features ≈ 2.5 MB

## 📝 Notes

- **Predictions are estimates** from a unified behavioral dataset
- **Not a diagnostic tool** — intended for research and self-insight
- **Privacy:** All data is processed locally; nothing is sent to external servers
- **Open source:** Modify, fork, and redistribute under MIT License

## 🐛 Troubleshooting

### "Module not found" errors
Ensure you ran `pip install -r requirements.txt`

### Models not loading
First run takes 2–3 minutes to train. Be patient; refresh the page.

### Dark theme not working locally
Ensure `.streamlit/config.toml` has `base = "dark"`

### Chart not showing on Streamlit Cloud
Rare plotly issue—refresh the page. If persistent, open an issue.

## 📞 Support

Found a bug or have a feature request? Open an issue on GitHub!

---

**Built with ❤️ using Streamlit**  
Disclaimer: Outputs are predictive estimates intended for behavioral research and exploration.
