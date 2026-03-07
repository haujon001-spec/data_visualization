Here is **Phase 4 — Preview Generation Design** for **Project 2: `global_economic_health`**, written in the same structure and depth as your world_populations Phase documents. It ensures:

- Previews are generated consistently for **bubble maps** and **population trendlines**  
- The pipeline integrates with your **local → background → cloud agent** workflow  
- The **heartbeat**, **QA**, and **verification layer** remain intact  
- The design reuses the proven preview architecture from Project 1  

```

---

# Phase 4 — Preview Generation Design  
**Project:** Global Economic Health Dashboard  
**Folder:** `data_visualization/global_economic_health/`  
**Phase:** 4 — Preview Generation  
**Status:** Ready for agent implementation  
**Dependencies:**  
- Phase 2 visualizations  
- Phase 3 QA agents  
- Shared coordination system  
- Verification layer  

---

## 1. Phase Objective

This phase defines how the system generates **MP4 and GIF previews** for the Global Economic Health Dashboard. These previews are used for:

- LinkedIn posts  
- Social media sharing  
- Project documentation  
- Cloud agent notifications  

The preview system must:

- Reuse the proven architecture from Project 1  
- Support both **bubble map** and **population trendline** animations  
- Be fully automated through the orchestrator  
- Pass UI QA and verification checks  
- Produce timestamped, reproducible outputs  

---

## 2. Preview Architecture Overview

### Required Preview Types  
1. **Bubble Map Preview**  
   - Shows GDP bubble sizes changing over time  
   - Shows debt‑to‑GDP color changes  
   - Uses year slider frames  

2. **Population Trendline Preview**  
   - Reuses Project 1’s animated trendline frames  
   - Shows trendlines growing year by year  

3. **Unified Preview (Optional)**  
   - Side‑by‑side bubble map + trendline  
   - 10–15 seconds  
   - 720p resolution  

### Output Formats  
- GIF (optimized palette)  
- MP4 (H.264 codec)  

### Output Paths  
```
reports/media/global_economic_health_preview_<timestamp>.gif
reports/media/global_economic_health_preview_<timestamp>.mp4
```

---

## 3. Script Requirements

### 3.1 Script: `08_generate_previews.py`  
**Purpose:** Generate GIF and MP4 previews from bubble map and trendline frames.

**Inputs:**  
- Bubble map figure  
- Population trendline figure  
- `macro_final_<timestamp>.csv`  
- Frame configuration (FPS, resolution, duration)  

**Outputs:**  
- GIF preview  
- MP4 preview  
- Frame images (PNG)  

**Key Requirements:**  
- Must support both bubble map and trendline frames  
- Must reuse Project 1’s preview logic where possible  
- Must generate frames at 1920×1080 or 1280×720  
- Must downscale GIF to 720p for size optimization  
- Must use consistent color themes  
- Must embed timestamp in filenames  

---

## 4. Frame Generation Requirements

### 4.1 Bubble Map Frames  
Each frame must include:

- Bubble sizes scaled by GDP  
- Bubble colors scaled by debt‑to‑GDP  
- Year label  
- Legend for color scale  
- Map projection  
- Dark theme  

**Frame Count:**  
- 30–60 frames (1 per year or 1 per 2 years)  

**Frame Naming:**  
```
frame_bubblemap_0001.png
frame_bubblemap_0002.png
...
```

---

### 4.2 Population Trendline Frames  
Reuse Project 1’s animated trendline logic:

- Trendlines grow year by year  
- Markers appear as years accumulate  
- Title updates with current year  
- Dark theme  

**Frame Count:**  
- 30–60 frames  

**Frame Naming:**  
```
frame_trendline_0001.png
frame_trendline_0002.png
...
```

---

## 5. GIF Generation Requirements

### GIF Rules  
- FPS: 10  
- Duration: 6–10 seconds  
- Resolution: 1280×720  
- Optimized palette  
- Loop = infinite  

### Output  
```
global_economic_health_preview_<timestamp>.gif
```

### Quality Requirements  
- No flickering  
- No color banding  
- Smooth transitions  
- Consistent font sizes  

---

## 6. MP4 Generation Requirements

### MP4 Rules  
- Codec: H.264  
- FPS: 24  
- Resolution: 1920×1080  
- Bitrate: 5000–8000 kbps  
- No audio  

### Output  
```
global_economic_health_preview_<timestamp>.mp4
```

### Quality Requirements  
- Smooth motion  
- No compression artifacts  
- Accurate color reproduction  

---

## 7. QA Requirements

### 7.1 Preview QA Agent (`agent_ui_qa.py`)  
Must validate:

- Frames render correctly  
- No missing labels  
- No broken color scales  
- No overlapping bubbles beyond threshold  
- Trendlines match underlying data  
- GIF plays smoothly  
- MP4 plays smoothly  
- File sizes within expected range  

### 7.2 QA Output  
- `reports/qa/preview_qa_report_<timestamp>.md`  
- Screenshots of sample frames  

---

## 8. Verification Layer Requirements

### verify_visualization.py  
Must check:

- Frame count matches expected  
- GIF exists and is > 100 KB  
- MP4 exists and is > 500 KB  
- No missing frames  
- No corrupted PNGs  

### verify_code_structure.py  
Must check:

- `08_generate_previews.py` exists  
- Required functions exist  
- No hard‑coded paths  

---

## 9. Orchestrator Integration

Preview generation must run **after**:

- Bubble map  
- Trendline  
- HTML dashboard  
- UI QA  

Sequence:

1. Render bubble map frames  
2. Render trendline frames  
3. Generate GIF  
4. Generate MP4  
5. Run preview QA  
6. Verification layer  
7. Cloud agent notification  

If any step fails, orchestrator must stop immediately.

---

## 10. Heartbeat Requirements

- Background agent heartbeat every 5 seconds  
- Cloud agent heartbeat during preview generation  
- Local agent timeout after 60 seconds  
- All events logged to audit trail  

---

## 11. Deliverables for Phase 4

- `08_generate_previews.py` implemented  
- Bubble map frames  
- Trendline frames  
- GIF preview  
- MP4 preview  
- Preview QA report  
- Verification summary  


