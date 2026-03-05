Below is your complete **Phase 4 GIF/MP4 Preview Design** Markdown file, ready to save as:

```
data_visualization/World_population/docs/Phase4_GIF_MP4_Preview_Design_5Mar2026.md
```

It follows your strict structure, timestamping, and agent‑oriented workflow. It is written so **VS Code, your orchestrator, and future OpenClaw/Telegram agents** can execute the preview‑generation pipeline reliably.

---

# Phase 4 — GIF/MP4 Preview Design (5 Mar 2026)

## 1. Purpose of Phase 4
This phase defines the complete architecture for generating **high‑quality GIF and MP4 previews** of the world‑population bar‑race animation. These previews are essential for:

- **LinkedIn publishing** (native MP4 auto‑plays in feed)
- **Telegram/OpenClaw notifications**
- **QA visual diffing**
- **Version traceability**
- **User engagement and trust** (people avoid unknown URLs but will watch a video)

The preview generator must be deterministic, timestamped, visually polished, and fully compatible with the orchestrator and QA agents.

---

## 2. Preview Output Requirements

### 2.1 Output Files
```
reports/media/population_preview_<3Mar2026>.mp4
reports/media/population_preview_<3Mar2026>.gif
```

### 2.2 Naming Convention
Use **human‑friendly timestamps**:

- `population_preview_3Mar2026.mp4`
- `population_preview_3Mar2026.gif`

### 2.3 Duration
**10–15 seconds**, optimized for LinkedIn engagement.

### 2.4 Resolution
- Preferred: **1080p (1920×1080)**
- Acceptable fallback: **720p (1280×720)**

### 2.5 Aspect Ratio
**16:9**, optimized for social media feeds.

### 2.6 Frame Rate
- MP4: **30 FPS**  
- GIF: **12–15 FPS** (to reduce file size)

---

## 3. Preview Generation Architecture

### 3.1 Script Location
```
scripts/05_generate_gif_mp4_preview.py
```

### 3.2 Responsibilities
- Load processed CSV  
- Render animation frames  
- Maintain consistent color mapping  
- Maintain consistent flag placement  
- Export MP4  
- Export GIF  
- Save with timestamp suffix  
- Return file paths to orchestrator  

### 3.3 Dependencies
- Plotly (static frame rendering)
- Pillow (GIF assembly)
- MoviePy or FFmpeg (MP4 encoding)
- Pandas (data handling)

---

## 4. Frame Rendering Design

### 4.1 Frame Count
For a 10–15 second video:

- MP4: 300–450 frames (30 FPS)
- GIF: 120–180 frames (12–15 FPS)

### 4.2 Frame Generation Strategy
Two options:

#### Option A — Render each year as a frame  
- Simple  
- Fast  
- Less smooth  

#### Option B — Interpolate between years (recommended)  
- Smooth transitions  
- Professional look  
- Better for LinkedIn  

Interpolation method:

```
population_interpolated = population_t + (population_t+1 - population_t) * alpha
```

Where `alpha` is the frame interpolation factor.

### 4.3 Visual Consistency
- Colors must remain consistent across frames  
- Flags must remain aligned  
- Bar order must match ranking  
- Font sizes must remain constant  

---

## 5. MP4 Encoding Requirements

### 5.1 Codec
Use **H.264** for maximum compatibility.

### 5.2 Bitrate
- Target: **4–6 Mbps**  
- Ensures clarity without bloating file size  

### 5.3 Audio
- No audio track  
- Silent video is preferred for LinkedIn autoplay  

### 5.4 Container
`.mp4` only.

### 5.5 Encoding Pipeline
Using MoviePy or FFmpeg:

```
ffmpeg -framerate 30 -i frame_%04d.png -c:v libx264 -pix_fmt yuv420p output.mp4
```

---

## 6. GIF Encoding Requirements

### 6.1 Color Reduction
GIF supports only **256 colors**, so:

- Use dithering  
- Reduce gradients  
- Avoid overly complex backgrounds  

### 6.2 Optimization
- Use Pillow or ImageMagick  
- Optimize palette  
- Reduce FPS to 12–15  

### 6.3 File Size Target
- < 10 MB preferred  
- < 20 MB acceptable  

---

## 7. Integration with Visualization Script

The preview generator must reuse:

- The same color palette  
- The same flag embedding logic  
- The same number formatting  
- The same layout  

This ensures:

- Visual consistency  
- QA accuracy  
- Trustworthy previews  

The visualization script must expose a function:

```
render_frame(year, alpha)
```

Where:

- `year` = base year  
- `alpha` = interpolation factor (0 → 1)

---

## 8. Integration with QA Agents

### 8.1 Data QA Agent
Must pass before preview generation begins.

### 8.2 UI QA Agent
Must pass HTML validation before preview generation.

### 8.3 Code Review Agent
Ensures preview script is maintainable.

### 8.4 Preview QA (Optional)
The orchestrator may:

- Extract a random frame  
- Compare against expected layout  
- Validate flag rendering  
- Validate number formatting  

---

## 9. Integration with Orchestrator (Phase 5)

The orchestrator must:

1. Run ETL  
2. Run Data QA  
3. Build visualization  
4. Generate timestamped HTML  
5. Run UI QA  
6. **Generate MP4 preview**  
7. **Generate GIF preview**  
8. Publish HTML  
9. Notify via Telegram  

### 9.1 Orchestrator Output
Telegram message must include:

- PASS/FAIL summary  
- Link to HTML  
- Attached MP4 preview  
- Attached GIF preview  
- QA reports  

---

## 10. LinkedIn Publishing Requirements

### 10.1 MP4 is the primary asset
LinkedIn auto‑plays MP4 videos, increasing engagement.

### 10.2 GIF is optional
Useful for messaging apps or fallback.

### 10.3 Recommended Post Structure
- Upload MP4 directly  
- Add a screenshot thumbnail  
- Add a short caption  
- Put the HTML link in the comments  

### 10.4 Why this works
- Users trust native media  
- LinkedIn boosts posts without external links  
- MP4 previews attract attention instantly  

---

## 11. Phase 4 To‑Do List (5 Mar 2026)

- Implement `05_generate_gif_mp4_preview.py`  
- Implement frame interpolation  
- Implement MP4 encoding  
- Implement GIF encoding  
- Add timestamp logic  
- Validate preview manually once  
- Integrate with orchestrator  
- Prepare for Telegram publishing  

---

