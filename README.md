# Late Delivery Risk – Streamlit app

DataCo supply chain capstone. Scores an order's late-delivery risk at checkout with the project's Gradient Boosting model,
and lets you explore all 65,752 scored orders.

## Files
| File | What it is |
| --- | --- |
| `app.py` | The Streamlit app (3 tabs: Risk calculator with a Predict button, Scored orders, Model) |
| `risk_model.py` | Pure-Python scorer for the exported model (no scikit-learn needed) |
| `model.json` | The trained Gradient Boosting model (100 trees, depth 3) |
| `late_risk_scored_orders.csv` | All orders with `late_risk`, `risk_band`, `predicted_late` |
| `logo.png` | Project logo |
| `requirements.txt` | Python packages |

## Run on your computer
```
pip install -r requirements.txt
streamlit run app.py
```

## Publish on Streamlit Community Cloud (free)
1. Create a new **public** GitHub repository and upload every file in this folder (keep them together at the top level).
2. Go to https://share.streamlit.io and sign in with GitHub.
3. Click **Create app** → **Deploy a public app from GitHub**.
4. Pick your repository, branch `main`, and main file `app.py`. Click **Deploy**.
5. After a minute or two you get a link like `https://<your-app-name>.streamlit.app` to share with your trainer.

## Model summary
- Hold-out ROC-AUC 0.770 · precision 86% · recall 58% · accuracy 72% (50% cut-off)
- Bands: Low < 45% · Medium 45–70% · High ≥ 70% (36% / 65% / 89% actually late, out-of-fold)
