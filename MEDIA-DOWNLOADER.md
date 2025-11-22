# Media Downloader Documentation

The Media Downloader is a comprehensive system for automatically discovering, downloading, and managing images, videos, and audio files from the internet.

## Features Overview

### 🔍 Search & Discovery
- **Unsplash Integration**: Access millions of free high-quality images
- **Pexels Integration**: Search and download from Pexels library
- **Pixabay Integration**: Free images and videos
- **Multi-Source Search**: Query all APIs simultaneously
- **Smart Results**: Automatically distributes downloads across sources

### ⬇️ Download Capabilities
- **Direct URL Downloads**: Download from any direct image/video URL
- **YouTube Support**: Download videos using yt-dlp
- **Batch Operations**: Download multiple files at once
- **Progress Tracking**: Monitor download progress
- **Automatic Retry**: Handles transient failures
- **Resume Support**: Skips already downloaded files

### 🛠️ Media Management
- **Image Optimization**: Resize and compress images
- **Format Conversion**: Convert between formats (JPG, PNG, WebP, etc.)
- **Thumbnail Generation**: Auto-create thumbnails for videos
- **Duplicate Detection**: Find and remove duplicate files
- **Metadata Tracking**: Track sources, dates, and custom metadata
- **File Organization**: Automatic categorization

### 🔒 Security & Performance
- **Rate Limiting**: Prevents API abuse
- **Input Validation**: Sanitizes all inputs
- **Caching**: Avoids re-downloading files
- **Error Handling**: Comprehensive error recovery
- **Timeout Protection**: Prevents hung downloads

## Installation

### Requirements

**Python Dependencies:**
```bash
pip install flask requests
```

**Optional Dependencies:**
```bash
# For YouTube downloads
pip install yt-dlp

# For image/video processing (system package)
sudo apt-get install ffmpeg
```

### API Keys

To enable search functionality, sign up for free API keys:

1. **Unsplash**: https://unsplash.com/developers
   - 50 requests/hour on free tier
   - Excellent image quality
   
2. **Pexels**: https://www.pexels.com/api/
   - 200 requests/hour on free tier
   - High-quality stock photos
   
3. **Pixabay**: https://pixabay.com/api/docs/
   - 100 requests/minute on free tier
   - Images and videos

**Set Environment Variables:**
```bash
export UNSPLASH_API_KEY="your-unsplash-key"
export PEXELS_API_KEY="your-pexels-key"
export PIXABAY_API_KEY="your-pixabay-key"
```

## Usage

### Web Interface

Access the media manager at: `http://localhost:9999/media`

**Features:**
- **Statistics Tab**: View library statistics
- **Download Tab**: Download from direct URLs
- **Search Tab**: Search and download from APIs
- **Manage Tab**: Optimize, thumbnails, duplicates
- **Browse Tab**: View all media files

### Python API

#### Basic Usage

```python
from media_downloader import MediaDownloader

# Initialize
downloader = MediaDownloader()

# Check stats
stats = downloader.get_media_stats()
print(f"Images: {stats['images']['count']}")
print(f"Videos: {stats['videos']['count']}")
```

#### Download from URLs

```python
# Download images
image_urls = [
    'https://example.com/image1.jpg',
    'https://example.com/image2.png'
]
result = downloader.download_images(image_urls)
print(f"Success: {result['success']}, Failed: {result['failed']}")

# Download videos
video_urls = [
    'https://example.com/video1.mp4'
]
result = downloader.download_videos(video_urls)
```

#### Search and Download

```python
# Search multiple APIs
result = downloader.search_and_download_images(
    query='hypnotic spiral',
    count=20,
    sources=['unsplash', 'pexels', 'pixabay'],
    orientation='landscape'  # or 'portrait', 'squarish'
)

# Search specific API
unsplash_urls = downloader.search_unsplash('meditation', count=10)
downloader.download_images(unsplash_urls)
```

#### YouTube Downloads

```python
# Download from YouTube
success = downloader.download_youtube_video(
    'https://youtube.com/watch?v=dQw4w9WgXcQ',
    quality='720p'  # or '1080p', 'best'
)
```

#### Batch Operations

```python
# Download multiple items with progress
items = [
    {'url': 'https://example.com/img1.jpg', 'type': 'image', 'metadata': {'category': 'spirals'}},
    {'url': 'https://example.com/img2.png', 'type': 'image', 'metadata': {'category': 'fractals'}},
    {'url': 'https://youtube.com/watch?v=...', 'type': 'video'}
]

def progress_callback(current, total, item):
    print(f"Downloading {current}/{total}: {item['url']}")

result = downloader.batch_download(items, progress_callback)
```

#### Image Optimization

```python
# Optimize all images
count = downloader.optimize_images(
    max_dimension=1920,  # Maximum width or height
    quality=85           # JPEG quality 1-100
)
print(f"Optimized {count} images")

# Convert image format
output = downloader.convert_image_format(
    'path/to/image.png',
    output_format='jpg',
    quality=90
)
```

#### Video Thumbnails

```python
# Generate thumbnails for all videos
count = downloader.generate_thumbnails(
    size=(320, 180)  # Width, height
)
print(f"Generated {count} thumbnails")
```

#### File Management

```python
# List all files
files = downloader.list_media_files(
    media_type='images',  # or 'videos', 'audio', 'all'
    include_info=True
)

for file in files:
    print(f"{file['filename']}: {file['size_mb']} MB")

# Get file info
info = downloader.get_file_info('path/to/file.jpg')
print(info)

# Find duplicates
duplicates = downloader.find_duplicates()
for hash_val, files in duplicates.items():
    print(f"Duplicates: {files}")

# Remove duplicates (keeps first)
removed = downloader.remove_duplicates(keep_first=True)
print(f"Removed {removed} duplicates")

# Clear media
downloader.clear_media('images')  # or 'videos', 'audio', 'all'
```

### REST API

All endpoints accept and return JSON.

#### GET /api/media/stats

Get media library statistics.

**Response:**
```json
{
  "status": "success",
  "stats": {
    "images": {"count": 50, "cached": 45},
    "videos": {"count": 10, "cached": 8},
    "audio": {"count": 5, "cached": 5}
  },
  "total_files": 65,
  "total_size_mb": 523.45
}
```

#### POST /api/media/download

Download from direct URLs.

**Request:**
```json
{
  "urls": ["https://example.com/image.jpg"],
  "type": "image"
}
```

**Response:**
```json
{
  "status": "success",
  "result": {
    "success": 1,
    "failed": 0,
    "skipped": 0
  }
}
```

#### POST /api/media/search

Search and download images.

**Request:**
```json
{
  "query": "hypnotic spiral",
  "count": 10,
  "sources": ["unsplash", "pexels", "pixabay"]
}
```

**Response:**
```json
{
  "status": "success",
  "query": "hypnotic spiral",
  "result": {
    "success": 10,
    "failed": 0,
    "skipped": 0
  }
}
```

#### GET /api/media/list

List media files.

**Query Parameters:**
- `type`: 'images', 'videos', 'audio', or 'all' (default: 'all')
- `info`: 'true' or 'false' (default: 'false')

**Response:**
```json
{
  "status": "success",
  "type": "all",
  "count": 65,
  "files": [
    {
      "filename": "abc123.jpg",
      "size_mb": 2.3,
      "type": "image",
      "modified": "2025-11-22T07:30:00"
    }
  ]
}
```

#### POST /api/media/optimize

Optimize images.

**Request:**
```json
{
  "max_dimension": 1920,
  "quality": 85
}
```

**Response:**
```json
{
  "status": "success",
  "optimized": 25
}
```

#### POST /api/media/thumbnails

Generate video thumbnails.

**Response:**
```json
{
  "status": "success",
  "generated": 10
}
```

#### GET /api/media/duplicates

Find duplicate files.

**Response:**
```json
{
  "status": "success",
  "duplicate_sets": 3,
  "duplicates": {
    "hash1": ["file1.jpg", "file2.jpg"],
    "hash2": ["file3.mp4", "file4.mp4"]
  }
}
```

#### POST /api/media/clear

Clear media files.

**Request:**
```json
{
  "type": "images"
}
```

**Response:**
```json
{
  "status": "success",
  "cleared": "images"
}
```

## Configuration

### Media Directory Structure

```
hub/media/
├── video/          # Video files
├── img/            # Image files
├── audio/          # Audio files
├── thumbnails/     # Auto-generated thumbnails
├── .temp/          # Temporary files
├── .download_cache.json    # Download cache
└── .metadata.json          # File metadata
```

### Supported Formats

**Images:** .jpg, .jpeg, .png, .gif, .webp, .bmp, .tiff

**Videos:** .mp4, .mkv, .webm, .avi, .mov, .flv, .wmv

**Audio:** .mp3, .wav, .ogg, .flac, .m4a, .aac

### Rate Limiting

- API requests: 1 request per second
- Web UI downloads: 5 per minute per IP
- Web UI searches: 3 per minute per IP
- Optimization: 2 per minute per IP

### Caching

The downloader maintains a cache to avoid re-downloading:
- URL hash to filename mapping
- Source information for each file
- Metadata associated with downloads

Cache is stored in `.download_cache.json` and persists across restarts.

## Best Practices

### API Usage

1. **Get API Keys**: Sign up for free API keys from all three services
2. **Monitor Limits**: Check API rate limits in service dashboards
3. **Use Specific Queries**: More specific queries yield better results
4. **Mix Sources**: Different sources have different content styles

### Performance

1. **Batch Downloads**: Use batch operations for multiple files
2. **Optimize Regularly**: Run optimization on new downloads
3. **Clean Duplicates**: Periodically check for and remove duplicates
4. **Monitor Storage**: Keep an eye on disk usage

### Organization

1. **Use Metadata**: Add metadata to downloads for categorization
2. **Generate Thumbnails**: Helpful for browsing video content
3. **Clear Old Content**: Remove unused media periodically

## Troubleshooting

### API Not Working

**Problem:** "API key not configured" error

**Solution:**
```bash
# Check environment variables
echo $UNSPLASH_API_KEY
echo $PEXELS_API_KEY
echo $PIXABAY_API_KEY

# Set in Docker Compose
# Add to docker-compose.yml under environment:
environment:
  - UNSPLASH_API_KEY=${UNSPLASH_API_KEY}
  - PEXELS_API_KEY=${PEXELS_API_KEY}
  - PIXABAY_API_KEY=${PIXABAY_API_KEY}
```

### YouTube Downloads Failing

**Problem:** "yt-dlp not installed" error

**Solution:**
```bash
# Install yt-dlp
pip install yt-dlp

# Or in Docker, add to requirements.txt:
echo "yt-dlp>=2023.0.0" >> requirements.txt
docker compose build --no-cache
```

### Optimization Not Working

**Problem:** "ffmpeg not installed" warning

**Solution:**
```bash
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install ffmpeg

# Or in Dockerfile:
RUN apt-get update && apt-get install -y ffmpeg
```

### Downloads Are Slow

**Causes:**
1. Large file sizes
2. Slow network connection
3. API rate limiting

**Solutions:**
1. Download smaller batches
2. Use lower quality settings
3. Spread downloads over time

### Storage Issues

**Problem:** Running out of disk space

**Solution:**
```python
# Clear old media
downloader.clear_media('images')  # Clear specific type

# Or remove duplicates
downloader.remove_duplicates()

# Or optimize to reduce size
downloader.optimize_images(max_dimension=1280, quality=75)
```

## Examples

### Example 1: Build Image Library

```python
from media_downloader import MediaDownloader

downloader = MediaDownloader()

# Search and download from multiple topics
topics = ['meditation', 'hypnotic spiral', 'abstract art', 'fractals', 'zen']

for topic in topics:
    print(f"Downloading images for: {topic}")
    result = downloader.search_and_download_images(
        query=topic,
        count=10,
        sources=['unsplash', 'pexels', 'pixabay']
    )
    print(f"Success: {result['success']}, Failed: {result['failed']}")

# Optimize all downloads
print("Optimizing images...")
count = downloader.optimize_images(max_dimension=1920, quality=85)
print(f"Optimized {count} images")

# Show stats
stats = downloader.get_media_stats()
print(f"\nTotal images: {stats['images']['count']}")
```

### Example 2: Download Video Library

```python
from media_downloader import MediaDownloader

downloader = MediaDownloader()

# List of YouTube videos
youtube_urls = [
    'https://youtube.com/watch?v=video1',
    'https://youtube.com/watch?v=video2',
    'https://youtube.com/watch?v=video3'
]

# Download all videos
for url in youtube_urls:
    print(f"Downloading: {url}")
    success = downloader.download_youtube_video(url, quality='720p')
    if success:
        print("✓ Success")
    else:
        print("✗ Failed")

# Generate thumbnails
print("\nGenerating thumbnails...")
count = downloader.generate_thumbnails(size=(320, 180))
print(f"Generated {count} thumbnails")
```

### Example 3: Automated Maintenance

```python
from media_downloader import MediaDownloader

downloader = MediaDownloader()

# Find and remove duplicates
print("Finding duplicates...")
duplicates = downloader.find_duplicates()
if duplicates:
    print(f"Found {len(duplicates)} sets of duplicates")
    removed = downloader.remove_duplicates()
    print(f"Removed {removed} duplicate files")

# Optimize images
print("\nOptimizing images...")
count = downloader.optimize_images(max_dimension=1920, quality=85)
print(f"Optimized {count} images")

# Generate missing thumbnails
print("\nGenerating thumbnails...")
count = downloader.generate_thumbnails()
print(f"Generated {count} new thumbnails")

# Show final stats
stats = downloader.get_media_stats()
files = downloader.list_media_files(include_info=True)
total_size = sum(f['size_mb'] for f in files)

print(f"\nLibrary Summary:")
print(f"Images: {stats['images']['count']}")
print(f"Videos: {stats['videos']['count']}")
print(f"Audio: {stats['audio']['count']}")
print(f"Total Size: {total_size:.2f} MB")
```

## Advanced Features

### Custom Metadata

```python
# Download with custom metadata
result = downloader.download_images(
    urls=['https://example.com/image.jpg'],
    metadata={
        'category': 'spirals',
        'tags': ['hypnotic', 'colorful'],
        'source': 'custom_collection',
        'created_by': 'artist_name'
    }
)

# Access metadata later
files = downloader.list_media_files(include_info=True)
for file in files:
    if file.get('metadata'):
        print(f"{file['filename']}: {file['metadata']}")
```

### Progress Callbacks

```python
def show_progress(current, total, item):
    percentage = (current / total) * 100
    print(f"[{percentage:.1f}%] Downloading: {item['url']}")

items = [...]  # List of items
result = downloader.batch_download(items, progress_callback=show_progress)
```

### File Information

```python
# Get detailed file info
info = downloader.get_file_info('/path/to/file.jpg')
print(f"Filename: {info['filename']}")
print(f"Size: {info['size_mb']} MB")
print(f"Type: {info['type']}")
print(f"Modified: {info['modified']}")
print(f"Metadata: {info['metadata']}")
```

## Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **Rate Limiting**: Built-in protection prevents API abuse
3. **Input Validation**: All URLs and inputs are sanitized
4. **File Types**: Only allowed file types are downloaded
5. **Timeout Protection**: All downloads have timeout limits

## Performance Tips

1. **Use Batch Operations**: More efficient than individual downloads
2. **Enable Caching**: Prevents duplicate downloads
3. **Optimize Storage**: Run optimization regularly
4. **Monitor API Limits**: Stay within free tier limits
5. **Use Appropriate Quality**: Balance quality vs file size

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation
3. Check logs in `hub/logs/`
4. Open an issue on GitHub

## License

The Media Downloader is part of Hypno-Hub and follows the same MIT license.
