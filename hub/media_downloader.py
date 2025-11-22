#!/usr/bin/env python3
"""
Media Downloader for Hypno Hub
Automatically downloads images and videos from the internet for use in sessions.

Features:
- Direct URL downloads for images and videos
- API integration for Unsplash, Pexels, and Pixabay
- YouTube video download support (yt-dlp)
- Batch operations with progress tracking
- Image format conversion and optimization
- Video format conversion and compression
- Thumbnail generation
- Duplicate detection
- Metadata extraction
- Automatic categorization
- Smart queuing and rate limiting
"""

import os
import logging
import requests
import hashlib
import mimetypes
import subprocess
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import json
import time
from datetime import datetime
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MediaDownloader:
    """Download and manage media files from the internet with advanced features."""
    
    # API endpoints
    UNSPLASH_API = "https://api.unsplash.com"
    PEXELS_API = "https://api.pexels.com/v1"
    PIXABAY_API = "https://pixabay.com/api"
    
    # Supported formats
    IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff']
    VIDEO_FORMATS = ['.mp4', '.mkv', '.webm', '.avi', '.mov', '.flv', '.wmv']
    AUDIO_FORMATS = ['.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac']
    
    def __init__(self, media_dir: str = None):
        """
        Initialize media downloader with advanced features.
        
        Args:
            media_dir: Base directory for media files (default: from env or /home/beta/hub/media)
        """
        if media_dir is None:
            media_dir = os.getenv('MEDIA_DIR', '/home/beta/hub/media')
        self.media_dir = media_dir
        self.video_dir = os.path.join(media_dir, "video")
        self.img_dir = os.path.join(media_dir, "img")
        self.audio_dir = os.path.join(media_dir, "audio")
        self.thumbnails_dir = os.path.join(media_dir, "thumbnails")
        self.temp_dir = os.path.join(media_dir, ".temp")
        self.cache_file = os.path.join(media_dir, ".download_cache.json")
        self.metadata_file = os.path.join(media_dir, ".metadata.json")
        
        # Ensure directories exist
        os.makedirs(self.video_dir, exist_ok=True)
        os.makedirs(self.img_dir, exist_ok=True)
        os.makedirs(self.audio_dir, exist_ok=True)
        os.makedirs(self.thumbnails_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Load cache and metadata
        self.cache = self._load_cache()
        self.metadata = self._load_metadata()
        
        # API keys from environment
        self.unsplash_key = os.getenv('UNSPLASH_API_KEY')
        self.pexels_key = os.getenv('PEXELS_API_KEY')
        self.pixabay_key = os.getenv('PIXABAY_API_KEY')
        
        # Rate limiting
        self.last_request_time = {}
        self.min_request_interval = 1.0  # seconds between requests
        
        # Download queue
        self.download_queue = []
        self.download_stats = {"total": 0, "success": 0, "failed": 0, "skipped": 0}
        
        logger.info(f"Initialized MediaDownloader with media_dir: {media_dir}")
        logger.info(f"API Keys configured: Unsplash={bool(self.unsplash_key)}, "
                   f"Pexels={bool(self.pexels_key)}, Pixabay={bool(self.pixabay_key)}")
    
    def _load_cache(self) -> Dict:
        """Load download cache from file."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
        return {
            "images": [], 
            "videos": [], 
            "audio": [],
            "hashes": {},  # URL hash to filename mapping
            "sources": {}  # filename to source info mapping
        }
    
    def _load_metadata(self) -> Dict:
        """Load metadata from file."""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load metadata: {e}")
        return {}
    
    def _save_metadata(self):
        """Save metadata to file."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")
    
    def _save_cache(self):
        """Save download cache to file."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
    
    def _get_file_hash(self, url: str) -> str:
        """Generate a hash for a URL to use as filename."""
        return hashlib.md5(url.encode()).hexdigest()
    
    def download_file(self, url: str, destination: str, timeout: int = 30) -> bool:
        """
        Download a file from URL to destination.
        
        Args:
            url: URL to download from
            destination: Path to save file
            timeout: Request timeout in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Downloading from {url}")
            
            # Check if already downloaded
            if os.path.exists(destination):
                logger.info(f"File already exists: {destination}")
                return True
            
            # Download with streaming to handle large files
            response = requests.get(url, stream=True, timeout=timeout, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            if response.status_code == 200:
                # Check content type
                content_type = response.headers.get('content-type', '')
                logger.info(f"Content-Type: {content_type}")
                
                # Write file in chunks
                with open(destination, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                file_size = os.path.getsize(destination)
                logger.info(f"Successfully downloaded {file_size} bytes to {destination}")
                return True
            else:
                logger.error(f"Failed to download: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            logger.error(f"Timeout downloading from {url}")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error downloading from {url}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error downloading from {url}: {e}")
            return False
    
    def download_images(self, urls: List[str], metadata: Dict = None) -> Dict[str, int]:
        """
        Download images from a list of URLs with metadata tracking.
        
        Args:
            urls: List of image URLs
            metadata: Optional metadata to attach to downloaded files
            
        Returns:
            Dictionary with download statistics
        """
        stats = {"success": 0, "failed": 0, "skipped": 0}
        
        for url in urls:
            # Generate filename from hash
            file_hash = self._get_file_hash(url)
            
            # Detect extension from URL
            ext = ".jpg"
            if url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp')):
                ext = os.path.splitext(url.lower())[1]
            
            filename = f"{file_hash}{ext}"
            destination = os.path.join(self.img_dir, filename)
            
            # Check cache
            if url in self.cache.get("images", []):
                logger.info(f"Image already in cache: {url}")
                stats["skipped"] += 1
                continue
            
            # Download
            if self.download_file(url, destination):
                self.cache.setdefault("images", []).append(url)
                self.cache.setdefault("hashes", {})[url] = filename
                self.cache.setdefault("sources", {})[filename] = {
                    "url": url,
                    "downloaded_at": datetime.now().isoformat(),
                    "type": "image"
                }
                
                # Store metadata
                if metadata:
                    self.metadata[filename] = metadata
                    self._save_metadata()
                
                stats["success"] += 1
            else:
                stats["failed"] += 1
        
        self._save_cache()
        logger.info(f"Image download stats: {stats}")
        return stats
    
    def download_videos(self, urls: List[str], metadata: Dict = None) -> Dict[str, int]:
        """
        Download videos from a list of URLs with metadata tracking.
        
        Args:
            urls: List of video URLs
            metadata: Optional metadata to attach to downloaded files
            
        Returns:
            Dictionary with download statistics
        """
        stats = {"success": 0, "failed": 0, "skipped": 0}
        
        for url in urls:
            # Generate filename from hash
            file_hash = self._get_file_hash(url)
            
            # Detect extension from URL
            ext = ".mp4"
            if url.lower().endswith(('.mp4', '.mkv', '.webm', '.avi', '.mov', '.flv')):
                ext = os.path.splitext(url.lower())[1]
            
            filename = f"{file_hash}{ext}"
            destination = os.path.join(self.video_dir, filename)
            
            # Check cache
            if url in self.cache.get("videos", []):
                logger.info(f"Video already in cache: {url}")
                stats["skipped"] += 1
                continue
            
            # Download
            if self.download_file(url, destination):
                self.cache.setdefault("videos", []).append(url)
                self.cache.setdefault("hashes", {})[url] = filename
                self.cache.setdefault("sources", {})[filename] = {
                    "url": url,
                    "downloaded_at": datetime.now().isoformat(),
                    "type": "video"
                }
                
                # Store metadata
                if metadata:
                    self.metadata[filename] = metadata
                    self._save_metadata()
                
                stats["success"] += 1
            else:
                stats["failed"] += 1
        
        self._save_cache()
        logger.info(f"Video download stats: {stats}")
        return stats
    
    def _rate_limit(self, api_name: str):
        """Apply rate limiting for API requests."""
        now = time.time()
        last_time = self.last_request_time.get(api_name, 0)
        elapsed = now - last_time
        
        if elapsed < self.min_request_interval:
            sleep_time = self.min_request_interval - elapsed
            logger.debug(f"Rate limiting {api_name}: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        self.last_request_time[api_name] = time.time()
    
    def search_unsplash(self, query: str, count: int = 10, orientation: str = None) -> List[str]:
        """
        Search Unsplash for images.
        
        Args:
            query: Search query
            count: Number of images (max 30 per request)
            orientation: 'landscape', 'portrait', or 'squarish'
            
        Returns:
            List of image URLs
        """
        if not self.unsplash_key:
            logger.error("UNSPLASH_API_KEY not set")
            return []
        
        self._rate_limit("unsplash")
        
        try:
            params = {
                "query": query,
                "per_page": min(count, 30),
                "client_id": self.unsplash_key
            }
            if orientation:
                params["orientation"] = orientation
            
            response = requests.get(
                f"{self.UNSPLASH_API}/search/photos",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                urls = [photo["urls"]["regular"] for photo in data.get("results", [])]
                logger.info(f"Found {len(urls)} images on Unsplash for '{query}'")
                return urls
            else:
                logger.error(f"Unsplash API error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching Unsplash: {e}")
            return []
    
    def search_pexels(self, query: str, count: int = 10, orientation: str = None) -> List[str]:
        """
        Search Pexels for images.
        
        Args:
            query: Search query
            count: Number of images (max 80 per request)
            orientation: 'landscape', 'portrait', or 'square'
            
        Returns:
            List of image URLs
        """
        if not self.pexels_key:
            logger.error("PEXELS_API_KEY not set")
            return []
        
        self._rate_limit("pexels")
        
        try:
            params = {
                "query": query,
                "per_page": min(count, 80)
            }
            if orientation:
                params["orientation"] = orientation
            
            response = requests.get(
                f"{self.PEXELS_API}/search",
                params=params,
                headers={"Authorization": self.pexels_key},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                urls = [photo["src"]["large"] for photo in data.get("photos", [])]
                logger.info(f"Found {len(urls)} images on Pexels for '{query}'")
                return urls
            else:
                logger.error(f"Pexels API error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching Pexels: {e}")
            return []
    
    def search_pixabay(self, query: str, count: int = 10, image_type: str = "photo") -> List[str]:
        """
        Search Pixabay for images.
        
        Args:
            query: Search query
            count: Number of images (max 200 per request)
            image_type: 'all', 'photo', 'illustration', 'vector'
            
        Returns:
            List of image URLs
        """
        if not self.pixabay_key:
            logger.error("PIXABAY_API_KEY not set")
            return []
        
        self._rate_limit("pixabay")
        
        try:
            params = {
                "key": self.pixabay_key,
                "q": query,
                "per_page": min(count, 200),
                "image_type": image_type,
                "safesearch": "true"
            }
            
            response = requests.get(
                self.PIXABAY_API,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                urls = [hit["largeImageURL"] for hit in data.get("hits", [])]
                logger.info(f"Found {len(urls)} images on Pixabay for '{query}'")
                return urls
            else:
                logger.error(f"Pixabay API error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching Pixabay: {e}")
            return []
    
    def search_and_download_images(
        self, 
        query: str, 
        count: int = 10, 
        sources: List[str] = ["unsplash", "pexels", "pixabay"],
        orientation: str = None
    ) -> Dict[str, int]:
        """
        Search multiple sources and download images.
        
        Args:
            query: Search query
            count: Total number of images to download
            sources: List of sources to search
            orientation: Image orientation preference
            
        Returns:
            Dictionary with download statistics
        """
        all_urls = []
        per_source = count // len(sources) + 1
        
        # Search all sources
        if "unsplash" in sources:
            all_urls.extend(self.search_unsplash(query, per_source, orientation))
        
        if "pexels" in sources:
            all_urls.extend(self.search_pexels(query, per_source, orientation))
        
        if "pixabay" in sources:
            all_urls.extend(self.search_pixabay(query, per_source))
        
        # Download found images
        if all_urls:
            urls_to_download = all_urls[:count]
            logger.info(f"Downloading {len(urls_to_download)} images for query '{query}'")
            return self.download_images(urls_to_download, metadata={"query": query, "source": "api"})
        else:
            logger.warning(f"No images found for query '{query}'")
            return {"success": 0, "failed": 0, "skipped": 0}
    
    def download_youtube_video(self, url: str, quality: str = "720p") -> bool:
        """
        Download video from YouTube using yt-dlp.
        
        Args:
            url: YouTube video URL
            quality: Preferred quality (e.g., '720p', '1080p', 'best')
            
        Returns:
            True if successful
        """
        try:
            # Check if yt-dlp is available
            result = subprocess.run(
                ["which", "yt-dlp"],
                capture_output=True,
                timeout=5
            )
            
            if result.returncode != 0:
                logger.error("yt-dlp not installed. Install with: pip install yt-dlp")
                return False
            
            # Generate output filename
            file_hash = self._get_file_hash(url)
            output_template = os.path.join(self.video_dir, f"{file_hash}.%(ext)s")
            
            # Parse quality (handle '720p' or '720')
            quality_num = quality.rstrip('p') if quality.endswith('p') else quality
            
            # Download video
            logger.info(f"Downloading YouTube video: {url}")
            cmd = [
                "yt-dlp",
                "-f", f"bestvideo[height<={quality_num}]+bestaudio/best[height<={quality_num}]",
                "--merge-output-format", "mp4",
                "-o", output_template,
                "--no-playlist",
                "--quiet",
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=300)
            
            if result.returncode == 0:
                self.cache.setdefault("videos", []).append(url)
                self._save_cache()
                logger.info(f"Successfully downloaded YouTube video")
                return True
            else:
                logger.error(f"Failed to download: {result.stderr.decode()}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Download timeout (5 minutes)")
            return False
        except Exception as e:
            logger.error(f"Error downloading YouTube video: {e}")
            return False
    
    def batch_download(
        self, 
        items: List[Dict[str, str]], 
        progress_callback=None
    ) -> Dict[str, int]:
        """
        Batch download multiple items with progress tracking.
        
        Args:
            items: List of dicts with 'url', 'type' ('image'/'video'), and optional 'metadata'
            progress_callback: Optional callback function(current, total, item)
            
        Returns:
            Dictionary with download statistics
        """
        stats = {"success": 0, "failed": 0, "skipped": 0, "total": len(items)}
        
        for i, item in enumerate(items):
            url = item.get("url")
            media_type = item.get("type", "image")
            metadata = item.get("metadata", {})
            
            if progress_callback:
                progress_callback(i + 1, len(items), item)
            
            try:
                if media_type == "image":
                    result = self.download_images([url], metadata=metadata)
                elif media_type == "video":
                    if "youtube.com" in url or "youtu.be" in url:
                        success = self.download_youtube_video(url)
                        result = {"success": 1 if success else 0, "failed": 0 if success else 1}
                    else:
                        result = self.download_videos([url], metadata=metadata)
                else:
                    logger.warning(f"Unknown media type: {media_type}")
                    continue
                
                stats["success"] += result.get("success", 0)
                stats["failed"] += result.get("failed", 0)
                stats["skipped"] += result.get("skipped", 0)
                
            except Exception as e:
                logger.error(f"Error downloading {url}: {e}")
                stats["failed"] += 1
        
        logger.info(f"Batch download complete: {stats}")
        return stats
    
    def get_media_stats(self) -> Dict:
        """
        Get statistics about downloaded media.
        
        Returns:
            Dictionary with media statistics
        """
        stats = {
            "images": {
                "count": len(os.listdir(self.img_dir)) if os.path.exists(self.img_dir) else 0,
                "cached": len(self.cache.get("images", []))
            },
            "videos": {
                "count": len(os.listdir(self.video_dir)) if os.path.exists(self.video_dir) else 0,
                "cached": len(self.cache.get("videos", []))
            },
            "audio": {
                "count": len(os.listdir(self.audio_dir)) if os.path.exists(self.audio_dir) else 0,
                "cached": len(self.cache.get("audio", []))
            }
        }
        return stats
    
    def clear_media(self, media_type: str = "all") -> bool:
        """
        Clear downloaded media files.
        
        Args:
            media_type: Type of media to clear ("images", "videos", "audio", or "all")
            
        Returns:
            True if successful
        """
        try:
            if media_type in ("images", "all"):
                for file in os.listdir(self.img_dir):
                    file_path = os.path.join(self.img_dir, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                self.cache["images"] = []
                logger.info("Cleared images")
            
            if media_type in ("videos", "all"):
                for file in os.listdir(self.video_dir):
                    file_path = os.path.join(self.video_dir, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                self.cache["videos"] = []
                logger.info("Cleared videos")
            
            if media_type in ("audio", "all"):
                for file in os.listdir(self.audio_dir):
                    file_path = os.path.join(self.audio_dir, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                self.cache["audio"] = []
                logger.info("Cleared audio")
            
            self._save_cache()
            return True
            
        except Exception as e:
            logger.error(f"Error clearing media: {e}")
            return False
    
    def convert_image_format(self, input_path: str, output_format: str = "jpg", quality: int = 85) -> Optional[str]:
        """
        Convert image to different format using FFmpeg.
        
        Args:
            input_path: Path to input image
            output_format: Output format (jpg, png, webp, etc.)
            quality: Quality for lossy formats (1-100)
            
        Returns:
            Path to converted image or None
        """
        try:
            # Check if ffmpeg is available
            result = subprocess.run(["which", "ffmpeg"], capture_output=True, timeout=5)
            if result.returncode != 0:
                logger.warning("ffmpeg not installed, skipping conversion")
                return None
            
            output_path = os.path.splitext(input_path)[0] + f".{output_format}"
            
            # Convert quality (1-100) to ffmpeg scale (2-31, lower is better)
            # quality 100 -> 2 (best), quality 1 -> 31 (worst)
            ffmpeg_quality = max(2, min(31, int(31 - (quality / 100 * 29))))
            
            cmd = [
                "ffmpeg", "-i", input_path,
                "-q:v", str(ffmpeg_quality),
                "-y", output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            
            if result.returncode == 0 and os.path.exists(output_path):
                logger.info(f"Converted {input_path} to {output_format}")
                return output_path
            else:
                logger.error(f"Conversion failed: {result.stderr.decode()}")
                return None
                
        except Exception as e:
            logger.error(f"Error converting image: {e}")
            return None
    
    def optimize_images(self, max_dimension: int = 1920, quality: int = 85) -> int:
        """
        Optimize all images in the img directory.
        
        Args:
            max_dimension: Maximum width or height
            quality: JPEG quality (1-100)
            
        Returns:
            Number of images optimized
        """
        count = 0
        
        for filename in os.listdir(self.img_dir):
            if not any(filename.lower().endswith(ext) for ext in self.IMAGE_FORMATS):
                continue
            
            input_path = os.path.join(self.img_dir, filename)
            
            try:
                # Use ffmpeg to resize and optimize
                result = subprocess.run(
                    ["which", "ffmpeg"],
                    capture_output=True,
                    timeout=5
                )
                
                if result.returncode != 0:
                    logger.warning("ffmpeg not installed, skipping optimization")
                    break
                
                temp_path = os.path.join(self.temp_dir, filename)
                
                # Convert quality (1-100) to ffmpeg scale (2-31, lower is better)
                ffmpeg_quality = max(2, min(31, int(31 - (quality / 100 * 29))))
                
                cmd = [
                    "ffmpeg", "-i", input_path,
                    "-vf", f"scale='min({max_dimension},iw)':'min({max_dimension},ih)':force_original_aspect_ratio=decrease",
                    "-q:v", str(ffmpeg_quality),
                    "-y", temp_path
                ]
                
                result = subprocess.run(cmd, capture_output=True, timeout=30)
                
                if result.returncode == 0 and os.path.exists(temp_path):
                    # Replace original with optimized
                    os.replace(temp_path, input_path)
                    count += 1
                    logger.info(f"Optimized {filename}")
                    
            except Exception as e:
                logger.error(f"Error optimizing {filename}: {e}")
        
        logger.info(f"Optimized {count} images")
        return count
    
    def generate_thumbnails(self, size: Tuple[int, int] = (320, 180)) -> int:
        """
        Generate thumbnails for all videos.
        
        Args:
            size: Thumbnail size (width, height)
            
        Returns:
            Number of thumbnails generated
        """
        count = 0
        
        for filename in os.listdir(self.video_dir):
            if not any(filename.lower().endswith(ext) for ext in self.VIDEO_FORMATS):
                continue
            
            video_path = os.path.join(self.video_dir, filename)
            thumb_name = os.path.splitext(filename)[0] + ".jpg"
            thumb_path = os.path.join(self.thumbnails_dir, thumb_name)
            
            if os.path.exists(thumb_path):
                logger.debug(f"Thumbnail already exists: {thumb_name}")
                continue
            
            try:
                # Use ffmpeg to extract frame
                result = subprocess.run(
                    ["which", "ffmpeg"],
                    capture_output=True,
                    timeout=5
                )
                
                if result.returncode != 0:
                    logger.warning("ffmpeg not installed, skipping thumbnails")
                    break
                
                cmd = [
                    "ffmpeg", "-i", video_path,
                    "-ss", "00:00:01",
                    "-vframes", "1",
                    "-vf", f"scale={size[0]}:{size[1]}",
                    "-y", thumb_path
                ]
                
                result = subprocess.run(cmd, capture_output=True, timeout=30)
                
                if result.returncode == 0 and os.path.exists(thumb_path):
                    count += 1
                    logger.info(f"Generated thumbnail for {filename}")
                    
            except Exception as e:
                logger.error(f"Error generating thumbnail for {filename}: {e}")
        
        logger.info(f"Generated {count} thumbnails")
        return count
    
    def get_file_info(self, filepath: str) -> Dict:
        """
        Get detailed information about a media file.
        
        Args:
            filepath: Path to media file
            
        Returns:
            Dictionary with file information
        """
        info = {
            "filename": os.path.basename(filepath),
            "path": filepath,
            "size_bytes": os.path.getsize(filepath) if os.path.exists(filepath) else 0,
            "size_mb": round(os.path.getsize(filepath) / (1024 * 1024), 2) if os.path.exists(filepath) else 0,
            "modified": datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat() if os.path.exists(filepath) else None,
            "type": None,
            "metadata": self.metadata.get(os.path.basename(filepath), {})
        }
        
        # Detect type
        ext = os.path.splitext(filepath)[1].lower()
        if ext in self.IMAGE_FORMATS:
            info["type"] = "image"
        elif ext in self.VIDEO_FORMATS:
            info["type"] = "video"
        elif ext in self.AUDIO_FORMATS:
            info["type"] = "audio"
        
        return info
    
    def list_media_files(self, media_type: str = "all", include_info: bool = False) -> List:
        """
        List all media files with optional detailed information.
        
        Args:
            media_type: Type of media to list ("images", "videos", "audio", or "all")
            include_info: Include detailed file information
            
        Returns:
            List of filenames or file info dictionaries
        """
        files = []
        
        dirs = []
        if media_type in ("images", "all"):
            dirs.append(("images", self.img_dir))
        if media_type in ("videos", "all"):
            dirs.append(("videos", self.video_dir))
        if media_type in ("audio", "all"):
            dirs.append(("audio", self.audio_dir))
        
        for media_type_name, directory in dirs:
            if not os.path.exists(directory):
                continue
            
            for filename in os.listdir(directory):
                filepath = os.path.join(directory, filename)
                
                if not os.path.isfile(filepath):
                    continue
                
                if include_info:
                    info = self.get_file_info(filepath)
                    info["category"] = media_type_name
                    files.append(info)
                else:
                    files.append(filename)
        
        return files
    
    def find_duplicates(self) -> Dict[str, List[str]]:
        """
        Find duplicate files based on file hash.
        
        Returns:
            Dictionary mapping hashes to lists of duplicate files
        """
        file_hashes = {}
        
        for media_file in self.list_media_files(include_info=True):
            filepath = media_file["path"]
            
            try:
                # Calculate file hash
                hash_md5 = hashlib.md5()
                with open(filepath, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hash_md5.update(chunk)
                file_hash = hash_md5.hexdigest()
                
                if file_hash in file_hashes:
                    file_hashes[file_hash].append(filepath)
                else:
                    file_hashes[file_hash] = [filepath]
                    
            except Exception as e:
                logger.error(f"Error hashing {filepath}: {e}")
        
        # Return only duplicates
        duplicates = {h: files for h, files in file_hashes.items() if len(files) > 1}
        
        if duplicates:
            logger.info(f"Found {len(duplicates)} sets of duplicate files")
        else:
            logger.info("No duplicate files found")
        
        return duplicates
    
    def remove_duplicates(self, keep_first: bool = True) -> int:
        """
        Remove duplicate files.
        
        Args:
            keep_first: Keep the first file in each duplicate set
            
        Returns:
            Number of files removed
        """
        duplicates = self.find_duplicates()
        removed = 0
        
        for file_hash, files in duplicates.items():
            # Keep one file, remove the rest
            keep_file = files[0] if keep_first else files[-1]
            remove_files = [f for f in files if f != keep_file]
            
            for filepath in remove_files:
                try:
                    os.remove(filepath)
                    removed += 1
                    logger.info(f"Removed duplicate: {filepath}")
                except Exception as e:
                    logger.error(f"Error removing {filepath}: {e}")
        
        logger.info(f"Removed {removed} duplicate files")
        return removed


def main():
    """Test and demonstrate media downloader functionality."""
    downloader = MediaDownloader()
    
    # Show current stats
    logger.info("=== Current Media Stats ===")
    stats = downloader.get_media_stats()
    logger.info(f"Images: {stats['images']['count']} files (cached: {stats['images']['cached']})")
    logger.info(f"Videos: {stats['videos']['count']} files (cached: {stats['videos']['cached']})")
    logger.info(f"Audio: {stats['audio']['count']} files (cached: {stats['audio']['cached']})")
    
    # Check API keys
    logger.info("\n=== API Configuration ===")
    logger.info(f"Unsplash API: {'✓ Configured' if downloader.unsplash_key else '✗ Not configured'}")
    logger.info(f"Pexels API: {'✓ Configured' if downloader.pexels_key else '✗ Not configured'}")
    logger.info(f"Pixabay API: {'✓ Configured' if downloader.pixabay_key else '✗ Not configured'}")
    
    if not any([downloader.unsplash_key, downloader.pexels_key, downloader.pixabay_key]):
        logger.info("\nTo enable API features, set environment variables:")
        logger.info("  export UNSPLASH_API_KEY='your-key'")
        logger.info("  export PEXELS_API_KEY='your-key'")
        logger.info("  export PIXABAY_API_KEY='your-key'")
    
    # List media files
    logger.info("\n=== Media Files ===")
    files = downloader.list_media_files(include_info=True)
    if files:
        logger.info(f"Found {len(files)} total files")
        for file_info in files[:5]:  # Show first 5
            logger.info(f"  {file_info['filename']} ({file_info['size_mb']} MB, {file_info['type']})")
        if len(files) > 5:
            logger.info(f"  ... and {len(files) - 5} more")
    else:
        logger.info("No media files found")
    
    # Example usage
    logger.info("\n=== Usage Examples ===")
    
    logger.info("\n1. Download images from direct URLs:")
    logger.info("  downloader.download_images([")
    logger.info("      'https://example.com/image1.jpg',")
    logger.info("      'https://example.com/image2.png'")
    logger.info("  ])")
    
    logger.info("\n2. Search and download images from APIs:")
    logger.info("  downloader.search_and_download_images(")
    logger.info("      query='hypnotic spiral',")
    logger.info("      count=10,")
    logger.info("      sources=['unsplash', 'pexels', 'pixabay']")
    logger.info("  )")
    
    logger.info("\n3. Download videos from URLs:")
    logger.info("  downloader.download_videos([")
    logger.info("      'https://example.com/video1.mp4'")
    logger.info("  ])")
    
    logger.info("\n4. Download from YouTube:")
    logger.info("  downloader.download_youtube_video(")
    logger.info("      'https://youtube.com/watch?v=...',")
    logger.info("      quality='720p'")
    logger.info("  )")
    
    logger.info("\n5. Batch download multiple items:")
    logger.info("  items = [")
    logger.info("      {'url': 'https://...jpg', 'type': 'image'},")
    logger.info("      {'url': 'https://...mp4', 'type': 'video'}")
    logger.info("  ]")
    logger.info("  downloader.batch_download(items)")
    
    logger.info("\n6. Optimize images:")
    logger.info("  downloader.optimize_images(max_dimension=1920, quality=85)")
    
    logger.info("\n7. Generate video thumbnails:")
    logger.info("  downloader.generate_thumbnails(size=(320, 180))")
    
    logger.info("\n8. Find and remove duplicates:")
    logger.info("  duplicates = downloader.find_duplicates()")
    logger.info("  downloader.remove_duplicates()")
    
    logger.info("\n9. Get detailed file info:")
    logger.info("  files = downloader.list_media_files(include_info=True)")
    logger.info("  for file in files:")
    logger.info("      print(file)")
    
    logger.info("\n10. Clear media:")
    logger.info("  downloader.clear_media('images')  # or 'videos', 'audio', 'all'")


if __name__ == "__main__":
    main()
