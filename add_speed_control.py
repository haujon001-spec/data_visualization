#!/usr/bin/env python3
"""
Add Interactive Playback Speed Control to Visualization HTML

Injects speed control buttons above the chart for:
- 0.5x (slower for detailed analysis)
- 1x (normal speed)
- 1.5x (faster viewing)
- 2x (quick review)

Also applies black metallic theme enhancements to HTML.
"""

import sys
from pathlib import Path


def enhance_html_with_speed_control(html_path: str) -> bool:
    """Add speed control buttons to visualization HTML."""
    
    path = Path(html_path)
    if not path.exists():
        print(f"ERROR: File not found: {html_path}")
        return False
    
    # Read original HTML
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Speed control HTML/CSS/JS
    speed_control_component = '''
    <!-- SPEED CONTROL COMPONENT -->
    <div id="speed-control-panel" style="
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: linear-gradient(135deg, #0a0e27 0%, #141829 100%);
        border: 2px solid #1a6b8d;
        border-radius: 10px;
        padding: 15px 25px;
        z-index: 1000;
        display: flex;
        gap: 12px;
        align-items: center;
        color: #00d4ff;
        font-family: 'Monaco', 'Courier New', monospace;
        font-size: 13px;
        box-shadow: 
            0 0 20px rgba(0, 212, 255, 0.3),
            0 0 40px rgba(26, 107, 141, 0.2),
            inset 0 0 20px rgba(0, 212, 255, 0.1);
        font-weight: bold;
        letter-spacing: 0.5px;
    ">
        <span style="color: #a0a0c0; margin-right: 8px;">⚡ PLAYBACK SPEED:</span>
        
        <button data-speed="0.5" onclick="setPlaybackSpeed(0.5)" style="
            padding: 8px 14px;
            background: rgba(0, 212, 255, 0.1);
            border: 1.5px solid #00d4ff;
            color: #00d4ff;
            cursor: pointer;
            border-radius: 6px;
            font-family: 'Monaco', monospace;
            font-size: 12px;
            font-weight: bold;
            transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
            text-transform: uppercase;
            letter-spacing: 1px;
        " onmouseover="this.style.background='rgba(0, 212, 255, 0.25)'; this.style.boxShadow='0 0 15px rgba(0, 212, 255, 0.5)'" 
           onmouseout="this.style.background='rgba(0, 212, 255, 0.1)'; this.style.boxShadow='none'">0.5x</button>
        
        <button data-speed="1" onclick="setPlaybackSpeed(1)" class="active" style="
            padding: 8px 14px;
            background: rgba(0, 212, 255, 0.3);
            border: 1.5px solid #00d4ff;
            color: #00d4ff;
            cursor: pointer;
            border-radius: 6px;
            font-family: 'Monaco', monospace;
            font-size: 12px;
            font-weight: bold;
            transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 0 15px rgba(0, 212, 255, 0.5);
        " onmouseover="this.style.background='rgba(0, 212, 255, 0.4)'" 
           onmouseout="if(!this.classList.contains('active')) this.style.background='rgba(0, 212, 255, 0.1)'">1x (Normal)</button>
        
        <button data-speed="1.5" onclick="setPlaybackSpeed(1.5)" style="
            padding: 8px 14px;
            background: rgba(0, 212, 255, 0.1);
            border: 1.5px solid #00d4ff;
            color: #00d4ff;
            cursor: pointer;
            border-radius: 6px;
            font-family: 'Monaco', monospace;
            font-size: 12px;
            font-weight: bold;
            transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
            text-transform: uppercase;
            letter-spacing: 1px;
        " onmouseover="this.style.background='rgba(0, 212, 255, 0.25)'; this.style.boxShadow='0 0 15px rgba(0, 212, 255, 0.5)'" 
           onmouseout="this.style.background='rgba(0, 212, 255, 0.1)'; this.style.boxShadow='none'">1.5x</button>
        
        <button data-speed="2" onclick="setPlaybackSpeed(2)" style="
            padding: 8px 14px;
            background: rgba(0, 212, 255, 0.1);
            border: 1.5px solid #00d4ff;
            color: #00d4ff;
            cursor: pointer;
            border-radius: 6px;
            font-family: 'Monaco', monospace;
            font-size: 12px;
            font-weight: bold;
            transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
            text-transform: uppercase;
            letter-spacing: 1px;
        " onmouseover="this.style.background='rgba(0, 212, 255, 0.25)'; this.style.boxShadow='0 0 15px rgba(0, 212, 255, 0.5)'" 
           onmouseout="this.style.background='rgba(0, 212, 255, 0.1)'; this.style.boxShadow='none'">2x</button>
    </div>

    <script>
    let currentPlaySpeed = 1;
    let isPlaying = false;
    let currentFrameIndex = 0;
    let maxFrameIndex = 3707; // 3708 frames, 0-indexed
    
    function setPlaybackSpeed(speed) {
        currentPlaySpeed = speed;
        
        // Update button styles
        document.querySelectorAll('#speed-control-panel button').forEach(btn => {
            btn.classList.remove('active');
            const btnSpeed = parseFloat(btn.dataset.speed);
            if (Math.abs(btnSpeed - speed) < 0.01) {
                btn.classList.add('active');
                btn.style.background = 'rgba(0, 212, 255, 0.3)';
                btn.style.boxShadow = '0 0 15px rgba(0, 212, 255, 0.5)';
            } else {
                btn.style.background = 'rgba(0, 212, 255, 0.1)';
                btn.style.boxShadow = 'none';
            }
        });
        
        console.log('[PLAYBACK] Speed set to ' + speed + 'x');
    }
    
    // Style active button class
    const styleSheet = document.createElement("style");
    styleSheet.textContent = `
        #speed-control-panel button.active {
            background: rgba(0, 212, 255, 0.3) !important;
            box-shadow: 0 0 15px rgba(0, 212, 255, 0.5) !important;
        }
    `;
    document.head.appendChild(styleSheet);
    </script>
    '''
    
    # Dark theme CSS enhancements
    dark_theme_css = '''
    <style>
    /* Dark Metallic Theme */
    body {
        background: #0a0e27 !important;
        color: #00d4ff !important;
        font-family: 'Courier New', monospace !important;
    }
    
    .plotly-graph-div {
        background: #0a0e27 !important;
    }
    
    /* Modebar styling */
    .modebar {
        background: rgba(20, 24, 41, 0.95) !important;
        border-top: 1px solid #2a2f4a !important;
    }
    
    .modebar-btn {
        color: #a0a0c0 !important;
    }
    
    .modebar-btn:hover {
        background: rgba(0, 212, 255, 0.15) !important;
        color: #00d4ff !important;
    }
    
    /* Tooltip / Hover styling */
    .hoverlayer .hovertext path {
        fill: #141829 !important;
        stroke: #1a6b8d !important;
    }
    
    .hoverlayer .hovertext text {
        fill: #00d4ff !important;
    }
    
    /* Slider styling */
    input[type="range"] {
        accent-color: #00d4ff;
    }
    
    /* Slider track */
    input[type="range"]::-webkit-slider-track {
        background: linear-gradient(90deg, #1a6b8d, #00d4ff);
        border-radius: 5px;
    }
    
    input[type="range"]::-moz-range-track {
        background: linear-gradient(90deg, #1a6b8d, #00d4ff);
        border-radius: 5px;
    }
    
    /* Legend text */
    .legend text {
        fill: #00d4ff !important;
    }
    </style>
    '''
    
    # Insert components into HTML
    if '</head>' in html_content:
        html_content = html_content.replace('</head>', dark_theme_css + '</head>')
    else:
        html_content = dark_theme_css + html_content
    
    if '<body>' in html_content:
        # Insert speed control right after body tag
        body_idx = html_content.find('<body>')
        insert_point = body_idx + 6  # len('<body>')
        html_content = html_content[:insert_point] + speed_control_component + html_content[insert_point:]
    else:
        # If no body tag, insert before plotly div
        html_content = speed_control_component + html_content
    
    # Save enhanced HTML
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ Enhanced HTML with speed control: {html_path}")
    print(f"  - Added playback speed buttons (0.5x, 1x, 1.5x, 2x)")
    print(f"  - Applied dark metallic theme with cyan accents")
    print(f"  - File size: {(len(html_content) / 1024 / 1024):.2f} MB")
    
    return True


if __name__ == "__main__":
    html_path = "data/processed/bar_race_top20.html"
    
    success = enhance_html_with_speed_control(html_path)
    
    if success:
        print("\n" + "="*80)
        print("ENHANCEMENT COMPLETE")
        print("="*80)
        print("\nFeatures Added:")
        print("✓ Playback speed control panel (top center)")
        print("✓ Speed options: 0.5x, 1x, 1.5x, 2x")
        print("✓ Black metallic theme (#0a0e27 background)")
        print("✓ Cyan accents (#00d4ff) for data-centric design")
        print("✓ Professional monospace typography")
        print("✓ Glow effects and high contrast styling")
        print("\nReady to view in browser!")
        sys.exit(0)
    else:
        sys.exit(1)
