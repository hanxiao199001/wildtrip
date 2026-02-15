---
name: image-fetcher
description: Automatically fetch free stock photos from Unsplash and Pexels based on keywords. Perfect for finding images for articles and social media.
---

# Image Fetcher

Automatically download free, high-quality stock photos based on keywords.

## Features

- Search Unsplash & Pexels (免费图库)
- Download images directly
- Filter by orientation (landscape/portrait/square)
- Organize by topic
- 100% free for commercial use

## Usage

### Command line
```bash
# Fetch single image
node fetch-image.cjs "West Lake Hangzhou sunset" --output ./images/

# Fetch multiple images for article
node fetch-article-images.cjs article.md --config images.json
```

### In conversation
> "帮我找10张苏东坡相关的免费图片"
> "为这篇文章抓取配图"

## Config

Create `image-config.json`:
```json
{
  "unsplash_key": "YOUR_KEY",  // Get from unsplash.com/developers
  "pexels_key": "YOUR_KEY",     // Get from pexels.com/api
  "output_dir": "./images/",
  "orientation": "landscape",    // landscape/portrait/square
  "per_page": 10
}
```

## API Keys (Optional)

Without keys: 50 requests/hour (demo mode)
With keys: unlimited (free registration)

**Get keys:**
- Unsplash: https://unsplash.com/oauth/applications
- Pexels: https://www.pexels.com/api/

## Output

Images saved with descriptive filenames:
- `west-lake-sunset-1.jpg`
- `red-cliff-yangtze-2.jpg`

Metadata saved as `images.json`:
- Photo credits
- License info
- Download URLs
