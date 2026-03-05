# -*- coding: utf-8 -*-
"""
Phase 4 - Preview Generator
Generate MP4 and GIF previews from visualization data for LinkedIn/social media
"""

from pathlib import Path
from datetime import datetime
import sys
from typing import List
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
import io


def check_dependencies() -> bool:
    """
    Check if required dependencies are installed.
    
    Returns:
        True if all dependencies available
    """
    print("[CHECK] Verifying dependencies...")
    
    try:
        import kaleido
        print("[CHECK] ✓ Kaleido available")
    except ImportError:
        print("[ERROR] Kaleido not installed")
        print("[FIX] Run: pip install kaleido")
        return False
    
    try:
        from PIL import Image
        print("[CHECK] ✓ Pillow available")
    except ImportError:
        print("[ERROR] Pillow not installed")
        print("[FIX] Run: pip install pillow")
        return False
    
    print("[CHECK] All dependencies available")
    return True


def load_processed_data(csv_path: Path) -> pd.DataFrame:
    """Load processed population data."""
    print(f"[LOAD] Reading {csv_path.name}")
    df = pd.read_csv(csv_path, encoding='utf-8')
    print(f"[LOAD] Loaded {len(df)} records")
    return df


def format_population(pop: int) -> str:
    """Format population with M/B suffixes."""
    if pop >= 1_000_000_000:
        return f"{pop/1_000_000_000:.2f}B"
    elif pop >= 1_000_000:
        return f"{pop/1_000_000:.0f}M"
    else:
        return f"{pop:,.0f}"


def create_frame(df: pd.DataFrame, year: int, top_n: int = 30) -> go.Figure:
    """
    Create a single frame for a specific year.
    
    Args:
        df: Full dataset
        year: Year to render
        top_n: Number of countries to show
    
    Returns:
        Plotly Figure object
    """
    # Filter data for this year
    year_data = df[df['year'] == year].copy()
    year_data = year_data.nsmallest(top_n, 'rank')
    year_data = year_data.sort_values('population')
    
    # Create bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=year_data['population'],
        y=year_data['country_name'],
        orientation='h',
        marker=dict(
            color=year_data.index,
            colorscale='Viridis',
            line=dict(width=1, color='rgba(255,255,255,0.3)')
        ),
        text=year_data['population'].apply(lambda x: format_population(x)),
        textposition='outside',
        textfont=dict(size=14, color='#FFFFFF', family='Arial Black'),
        hovertemplate='<b>%{y}</b><br>Population: %{x:,.0f}<extra></extra>'
    ))
    
    # Update layout
    fig.update_layout(
        title=dict(
            text=f'🌍 World Population - {year}<br><sub>Top {top_n} Most Populous Countries</sub>',
            x=0.5,
            xanchor='center',
            font=dict(size=28, color='#FFFFFF')
        ),
        xaxis_title='Population',
        yaxis_title='',
        showlegend=False,
        height=1080,
        width=1920,
        template='plotly_dark',
        font=dict(family='Arial', size=14, color='#E0E0E0'),
        xaxis=dict(
            tickformat='~s',
            showgrid=True,
            gridcolor='rgba(128, 128, 128, 0.3)',
            tickfont=dict(size=14, color='#FFFFFF')
        ),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(size=14, color='#FFFFFF')
        ),
        plot_bgcolor='#1e1e1e',
        paper_bgcolor='#121212',
        margin=dict(l=250, r=150, t=150, b=100)
    )
    
    return fig


def render_frames(df: pd.DataFrame, output_dir: Path, sample_years: List[int], top_n: int = 30) -> List[Path]:
    """
    Render frames for sampled years.
    
    Args:
        df: Full dataset
        output_dir: Directory to save frames
        sample_years: List of years to render
        top_n: Number of countries per frame
    
    Returns:
        List of frame file paths
    """
    frames_dir = output_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"[RENDER] Creating {len(sample_years)} frames...")
    
    frame_paths = []
    for i, year in enumerate(sample_years):
        fig = create_frame(df, year, top_n)
        
        # Export as PNG
        frame_path = frames_dir / f"frame_{i:04d}.png"
        fig.write_image(str(frame_path), format='png', width=1920, height=1080, scale=1)
        frame_paths.append(frame_path)
        
        if (i + 1) % 10 == 0:
            print(f"[RENDER] Rendered {i + 1}/{len(sample_years)} frames")
    
    print(f"[RENDER] ✓ Rendered {len(frame_paths)} frames")
    return frame_paths


def create_gif(frame_paths: List[Path], output_path: Path, fps: int = 10) -> None:
    """
    Create GIF from frames.
    
    Args:
        frame_paths: List of frame paths
        output_path: Output GIF file
        fps: Frames per second
    """
    print(f"[GIF] Creating animation at {fps} FPS...")
    
    # Load images
    images = []
    for path in frame_paths:
        img = Image.open(path)
        # Resize to 720p for smaller file size
        img = img.resize((1280, 720), Image.Resampling.LANCZOS)
        images.append(img)
    
    # Save as GIF
    duration_ms = int(1000 / fps)
    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:],
        duration=duration_ms,
        loop=0,
        optimize=True
    )
    
    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"[GIF] ✓ Created {output_path.name} ({file_size_mb:.2f} MB)")


def create_mp4_from_gif(gif_path: Path, mp4_path: Path) -> None:
    """
    Convert GIF to MP4 using ImageMagick or manual frame extraction.
    
    Args:
        gif_path: Input GIF file
        mp4_path: Output MP4 file
    """
    print(f"[MP4] Converting GIF to MP4...")
    
    try:
        from moviepy.editor import VideoFileClip
        
        # Load GIF and save as MP4
        clip = VideoFileClip(str(gif_path))
        clip.write_videofile(
            str(mp4_path),
            codec='libx264',
            audio=False,
            bitrate='5000k',
            fps=24,
            logger=None
        )
        
        file_size_mb = mp4_path.stat().st_size / (1024 * 1024)
        print(f"[MP4] ✓ Created {mp4_path.name} ({file_size_mb:.2f} MB)")
        
    except Exception as e:
        print(f"[WARNING] Could not create MP4: {e}")
        print("[INFO] You can use the GIF file for now, or install ffmpeg for MP4 support")


def main() -> None:
    """Main execution function."""
    print("=" * 70)
    print("GENERATING PREVIEW FILES FOR LINKEDIN")
    print("=" * 70)
    
    # Check dependencies
    if not check_dependencies():
        print("\n[ERROR] Missing dependencies")
        sys.exit(1)
    
    # Setup paths
    base_dir = Path(__file__).parent.parent
    processed_dir = base_dir / "csv" / "processed"
    media_dir = base_dir / "reports" / "media"
    media_dir.mkdir(parents=True, exist_ok=True)
    
    # Find most recent processed file
    processed_files = sorted(processed_dir.glob("population_top50_*.csv"))
    
    if not processed_files:
        print("[ERROR] No processed data found")
        print("[FIX] Run scripts/02_transform_rank_top50.py first")
        sys.exit(1)
    
    csv_path = processed_files[-1]
    
    # Load data
    df = load_processed_data(csv_path)
    
    # Sample years for animation (65 years → ~60 frames for 6-sec GIF at 10fps)
    all_years = sorted(df['year'].unique())
    # Sample every other year for smoother animation
    sample_years = all_years[::1]  # Use all years
    
    print(f"[PLAN] Creating animation with {len(sample_years)} frames")
    print(f"[PLAN] Duration: ~{len(sample_years)/10:.1f} seconds at 10 FPS")
    
    # Render frames
    frame_paths = render_frames(df, media_dir, sample_years, top_n=30)
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%d%b%Y")
    gif_path = media_dir / f"population_preview_{timestamp}.gif"
    mp4_path = media_dir / f"population_preview_{timestamp}.mp4"
    
    # Create GIF
    create_gif(frame_paths, gif_path, fps=10)
    
    # Try to create MP4
    create_mp4_from_gif(gif_path, mp4_path)
    
    print("=" * 70)
    print("✓ PREVIEW GENERATION COMPLETE")
    print("=" * 70)
    print(f"GIF: {gif_path}")
    if mp4_path.exists():
        print(f" MP4: {mp4_path}")
    print("\nReady for LinkedIn upload!")


if __name__ == "__main__":
    main()
