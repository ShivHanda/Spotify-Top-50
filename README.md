# 🎵 Automated Spotify Global Top 50 Pipeline & Analytics

![GitHub Actions](https://img.shields.io/badge/Status-Automated_Daily-success?style=for-the-badge&logo=githubactions)
![Python](https://img.shields.io/badge/Python-3.9-3776AB?style=for-the-badge&logo=python)
![Power BI](https://img.shields.io/badge/Power_BI-Visualized-F2C811?style=for-the-badge&logo=powerbi)
![Data](https://img.shields.io/badge/Data_Since-Dec_2025-blueviolet?style=for-the-badge)

> **"Capturing the pulse of global music trends, one day at a time."**

## 🚀 Project Overview
This repository hosts a robust **ETL (Extract, Transform, Load) Pipeline** that automatically archives the **Spotify Global Top 50** charts every single day. 

Unlike standard scripts that stop working due to API restrictions, this project uses a **hybrid architecture** to build a permanent historical dataset of music trends, which is then visualized using **Microsoft Power BI**.

### 📊 The Power BI Dashboard
*Dynamic visualization of the collected data.*

![Dashboard Preview]
<p align="center">
  <img src="https://raw.githubusercontent.com/ShivHanda/Spotify-Top-50/main/SpotifyGlobal50.gif" width="70%" alt="Dashboard Preview">
</p>

**Key Insights Tracked:**
* 📈 **Virality Trends:** Identifying songs that skyrocket to #1.
* ⏳ **Longevity Analysis:** Which tracks survive the longest in the Top 50?
* 🌍 **Artist Dominance:** Who owns the charts right now?

---

## ⚙️ Engineering Architecture (How It Works)

This project solves the "Spotify Playlist API Ban" (Nov 2024) using a smart **Hybrid Scraping + API Approach**.

1.  **Trigger ⏰:** GitHub Actions initiates the pipeline daily at **23:00 UTC**.
2.  **Extraction (The Bypass) 🕵️:** * Instead of asking Spotify for the playlist (which is blocked for new apps), the script scrapes live track IDs from **Kworb.net** using `BeautifulSoup`.
3.  **Enrichment 💎:**
    * These IDs are sent to the **Spotify Web API** to fetch rich metadata (Album Art, Exact Release Dates, Popularity Scores).
4.  **Transformation 🛠️:** * Handles mixed date formats (e.g., "1963" vs "2024-12-14").
    * Deduplicates data to ensure a clean time-series dataset.
5.  **Storage 💾:** * Data is appended to `spotify_history.csv` and automatically committed back to the repository.

---

## 📂 Dataset Schema
The automated CSV contains the following data points for every track, every day:

| Column | Description |
| :--- | :--- |
| `Date` | Date of data collection |
| `Position` | Rank (1-50) |
| `Song` | Track Name |
| `Artist` | Artist Name(s) |
| `Popularity` | Spotify Virality Score (0-100) |
| `Duration_MS` | Length of track |
| `Release_Date` | Normalized Release Date (YYYY-MM-DD) |
| `Album_Cover_URL` | High-res album art link |

---

## 🛠️ Tech Stack
* **Automation:** GitHub Actions (Cron Jobs)
* **Core Script:** Python (`pandas`, `requests`, `beautifulsoup4`)
* **Security:** Environment Variables (Secrets) for API Credentials
* **Visualization:** Power BI

---

### ⭐ Support
If you find this project cool or useful, give it a **Star**! ⭐
