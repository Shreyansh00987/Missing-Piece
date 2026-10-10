# Kaggle Publication Workflow & Checklist

**Project:** MISSING PIECE  
**Target:** DEV × Kaggle Benchmarking Challenge  
**Notebook File:** `notebooks/missing_piece_benchmark.ipynb`  
**Dataset Artifact:** `data/dataset.jsonl`, `data/dataset.csv`  

---

## 1. Environment & Credential Verification

- [x] Python benchmark code verified and unit tested (32/32 tests passing).
- [x] Full dataset generated and validated (120 items: 60 intact, 60 defective).
- [x] Notebook constructed and verified self-contained (`notebooks/missing_piece_benchmark.ipynb`).
- [ ] **Kaggle Credentials Check:**
  - Kaggle CLI installed: `pip install kaggle` (Available on system)
  - Kaggle API token location: `~/.kaggle/kaggle.json` or environment variables `KAGGLE_USERNAME` and `KAGGLE_KEY`.
  - *Current Status:* No Kaggle API credentials detected in the environment.

---

## 2. Publication Options

### Option A: Automated Kaggle CLI Push (When API Token Configured)
If `kaggle.json` or environment variables are provided:

```bash
# 1. Create Kaggle kernel metadata
kaggle kernels init -p notebooks/

# 2. Edit notebooks/kernel-metadata.json:
# {
#   "id": "<your-username>/missing-piece-ai-benchmark",
#   "title": "Missing Piece: The Epistemic Caution AI Benchmark",
#   "code_file": "missing_piece_benchmark.ipynb",
#   "language": "python",
#   "kernel_type": "notebook",
#   "is_private": false,
#   "enable_gpu": false,
#   "enable_internet": true
# }

# 3. Push to Kaggle
kaggle kernels push -p notebooks/
```

### Option B: Web UI Publication (Direct Import)
1. Go to [kaggle.com/code](https://www.kaggle.com/code) and click **"New Notebook"**.
2. Select **File -> Import Notebook** and upload `notebooks/missing_piece_benchmark.ipynb` from this repository.
3. In the right panel under **Input**:
   - Upload `data/dataset.jsonl` and `outputs/scored_results.csv` as a new private/public Kaggle Dataset, OR run the notebook directly (it generates the dataset deterministically via code!).
4. Click **Run All** to verify all markdown cells and figures execute cleanly.
5. Click **Save Version -> Save & Run All (Commit)**.
6. Under notebook settings, toggle **Sharing: Public**.
7. Copy the public Kaggle notebook URL (format: `https://www.kaggle.com/<username>/missing-piece-ai-benchmark`).
8. Paste the real URL into `submission/dev_article.md` under the section **"My Benchmark"**.

---

## 3. Publication Verification Checklist

- [ ] Kernel executed successfully with zero runtime errors.
- [ ] All 6 figures render cleanly inside the Kaggle interface.
- [ ] Sharing visibility confirmed as **Public**.
- [ ] Verified URL is active and accessible via logged-out browser session.
- [ ] Verified URL updated in `submission/dev_article.md` and `README.md`.
