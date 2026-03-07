# -*- coding: utf-8 -*-
"""
Phase 2: Generate Preview Videos

Generates GIF and MP4 previews from Plotly figures for social media sharing.
- GIF: 10 FPS, 720p, 5-10 second loop (one full cycle through years)
- MP4: 24 FPS, 1080p, 15+ second video

Output: reports/html/preview_*.gif
        reports/html/preview_*.mp4
"""

import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
import logging
import subprocess
import tempfile
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class PreviewGenerator:
    """Generates animated preview videos from macro-economic data."""
    
    def __init__(self, project_root: Path = None):
        """Initialize preview generator."""
        self.project_root = project_root or Path(__file__).parent.parent
    
    def check_dependencies(self) -> bool:
        """Check for required dependencies (ffmpeg, kaleido)."""
        logger.info("[CHECK] Verifying dependencies...")
        
        try:
            # Check for ffmpeg
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True)
            if result.returncode != 0:
                logger.warning("[CHECK] ffmpeg not found - skipping video generation")
                return False
            logger.info("[CHECK] ffmpeg found ✓")
        except FileNotFoundError:
            logger.warning("[CHECK] ffmpeg not installed - video generation disabled")
            return False
        
        return True
    
    def load_data(self) -> pd.DataFrame:
        """Load latest macro_final dataset."""
        import glob
        
        logger.info("[LOAD] Searching for macro_final data...")
        pattern = str(self.project_root / 'csv' / 'processed' / 'macro_final_*.csv')
        files = glob.glob(pattern)
        
        if not files:
            raise ValueError("No macro_final CSV found")
        
        latest = max(files, key=lambda p: Path(p).stat().st_mtime)
        df = pd.read_csv(latest)
        logger.info(f"[LOAD] {len(df)} rows loaded")
        
        return df
    
    def create_preview_figure(self, df: pd.DataFrame) -> list:
        """Create frame-by-frame figures for animation."""
        logger.info("[FRAME] Creating animation frames...")
        
        years = sorted(df['year'].unique())
        frames = []
        
        for year in years:
            year_data = df[df['year'] == year].copy()
            
            # Filter for valid data
            year_data = year_data.dropna(subset=['gdp_per_capita', 'population', 'gdp_usd'])
            year_data = year_data[(year_data['gdp_per_capita'] > 0) & (year_data['population'] > 0)]
            
            if len(year_data) < 10:
                continue
            
            # Prepare bubble sizes and colors
            year_data['bubble_size'] = (year_data['gdp_usd'] / 1e10).clip(lower=1)
            year_data['debt_color'] = year_data['debt_to_gdp'].fillna(0)
            
            frames.append({
                'year': year,
                'data': year_data
            })
        
        logger.info(f"[FRAME] {len(frames)} frames prepared")
        
        return frames
    
    def generate_static_frames(self, frames: list, output_dir: Path, format: str = 'png') -> list:
        """Generate static frame images."""
        logger.info(f"[STATIC] Generating {len(frames)} frame images...")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        frame_files = []
        
        for i, frame_info in enumerate(frames):
            year = frame_info['year']
            data = frame_info['data']
            
            # Create figure for this frame
            fig = go.Figure()
            
            fig.add_trace(
                go.Scatter(
                    x=data['gdp_per_capita'],
                    y=data['population'],
                    mode='markers',
                    marker=dict(
                        size=data['bubble_size'].clip(lower=5, upper=40),
                        color=data['debt_color'],
                        colorscale='RdYlGn_r',
                        opacity=0.7,
                        line=dict(width=1, color='white')
                    ),
                    hovertemplate='<b>%{customdata}</b><extra></extra>',
                    customdata=data['country_name']
                )
            )
            
            fig.update_layout(
                title=f'Global Economic Health - {int(year)}',
                xaxis_title='GDP per Capita (USD, log)',
                yaxis_title='Population (log)',
                xaxis_type='log',
                yaxis_type='log',
                width=1280,
                height=720,
                template='plotly_white'
            )
            
            # Save frame
            frame_file = output_dir / f'frame_{i:04d}.{format}'
            
            try:
                fig.write_image(str(frame_file), format=format)
                frame_files.append(frame_file)
                
                if (i + 1) % 10 == 0:
                    logger.info(f"[STATIC] {i+1}/{len(frames)} frames rendered")
            
            except Exception as e:
                logger.warning(f"[STATIC] Could not render frame {i}: {str(e)}")
        
        logger.info(f"[STATIC] {len(frame_files)} frames generated")
        
        return frame_files
    
    def create_gif(self, frame_files: list, output_path: Path, fps: int = 10):
        """Create animated GIF from frame images."""
        logger.info(f"[GIF] Creating animated GIF ({fps} FPS)...")
        
        if not frame_files:
            logger.warning("[GIF] No frames available")
            return None
        
        try:
            # Use imageio if available
            import imageio
            
            images = [imageio.imread(str(f)) for f in frame_files]
            imageio.mimsave(str(output_path), images, fps=fps, loop=0)
            
            logger.info(f"[GIF] GIF created: {output_path.name}")
            logger.info(f"[GIF] Size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
            
            return output_path
        
        except ImportError:
            logger.warning("[GIF] imageio not installed - skipping GIF generation")
            return None
        except Exception as e:
            logger.error(f"[GIF] Error creating GIF: {str(e)}")
            return None
    
    def create_video(self, frame_files: list, output_path: Path, fps: int = 24):
        """Create MP4 video from frame images using ffmpeg."""
        logger.info(f"[VIDEO] Creating MP4 video ({fps} FPS)...")
        
        if not frame_files:
            logger.warning("[VIDEO] No frames available")
            return None
        
        try:
            # Create input pattern for ffmpeg
            frame_pattern = str(frame_files[0].parent / 'frame_%04d.png')
            
            # ffmpeg command
            cmd = [
                'ffmpeg',
                '-framerate', str(fps),
                '-i', frame_pattern,
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-crf', '23',
                '-y',
                str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info(f"[VIDEO] MP4 created: {output_path.name}")
                logger.info(f"[VIDEO] Size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
                return output_path
            else:
                logger.error(f"[VIDEO] ffmpeg error: {result.stderr[:200]}")
                return None
        
        except subprocess.TimeoutExpired:
            logger.error("[VIDEO] Video creation timeout")
            return None
        except Exception as e:
            logger.error(f"[VIDEO] Error creating video: {str(e)}")
            return None
    
    def generate_previews(self):
        """Generate all preview formats."""
        logger.info("=" * 70)
        logger.info("GENERATING PREVIEW VIDEOS")
        logger.info("=" * 70)
        
        # Check dependencies
        has_ffmpeg = self.check_dependencies()
        
        # Load data
        df = self.load_data()
        
        # Create frames
        frames = self.create_preview_figure(df)
        
        # Create temporary directory for frame images
        with tempfile.TemporaryDirectory() as tmpdir:
            frame_dir = Path(tmpdir)
            
            # Generate static frames
            frame_files = self.generate_static_frames(frames, frame_dir, format='png')
            
            if not frame_files:
                logger.error("[PREVIEW] No frames generated")
                return None
            
            # Create output directory
            output_dir = self.project_root / 'reports' / 'html'
            output_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%d%b%Y_%H%M%S").upper()
            results = {}
            
            # Generate GIF
            try:
                gif_path = output_dir / f'preview_{timestamp}.gif'
                gif_result = self.create_gif(frame_files, gif_path, fps=10)
                results['gif'] = gif_result
            except Exception as e:
                logger.warning(f"[GIF] Generation failed: {str(e)}")
                results['gif'] = None
            
            # Generate MP4 (if ffmpeg available)
            if has_ffmpeg:
                try:
                    mp4_path = output_dir / f'preview_{timestamp}.mp4'
                    mp4_result = self.create_video(frame_files, mp4_path, fps=24)
                    results['mp4'] = mp4_result
                except Exception as e:
                    logger.warning(f"[VIDEO] Generation failed: {str(e)}")
                    results['mp4'] = None
            else:
                results['mp4'] = None
        
        return results


def main():
    """Main execution function."""
    project_root = Path(__file__).parent.parent
    
    generator = PreviewGenerator(project_root)
    
    try:
        results = generator.generate_previews()
        
        if results and (results.get('gif') or results.get('mp4')):
            logger.info("\n✅ Preview generation complete")
            return 0
        else:
            logger.warning("\n⚠️  Preview generation completed with warnings")
            return 1
    
    except Exception as e:
        logger.error(f"\n❌ Error: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
