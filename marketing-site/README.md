# Silverback Marketing Site

A clean, professional landing page for Silverback built for Netlify deployment.

## Quick Deploy to Netlify

### Option 1: Deploy from GitHub
1. Push this `marketing-site` folder to your GitHub repo (or create a new repo for it)
2. Go to [Netlify](https://app.netlify.com)
3. Click "Add new site" → "Import an existing project"
4. Connect your GitHub repo
5. Set build settings:
   - Build command: (leave empty, it's static HTML)
   - Publish directory: `marketing-site` (or root if this is its own repo)
6. Deploy!

### Option 2: Drag & Drop
1. Build the site locally (it's just static HTML)
2. Go to [Netlify Drop](https://app.netlify.com/drop)
3. Drag the `marketing-site` folder
4. Done!

### Option 3: Netlify CLI
```bash
cd marketing-site
npm install -g netlify-cli
netlify deploy --prod
```

## Custom Domain Setup

1. In Netlify dashboard, go to Site settings → Domain management
2. Click "Add custom domain"
3. Enter your domain (e.g., `silverback.dev`)
4. Follow Netlify's DNS instructions

### Suggested Domains
- `silverback.dev`
- `silverback.app`
- `silverbacktools.com`
- `silverbackos.com`
- `silverbackclient.com`

## Features

- ✅ Responsive design (mobile-friendly)
- ✅ Netlify Forms integration (email capture)
- ✅ Smooth scrolling navigation
- ✅ Clean, professional design
- ✅ SEO-friendly
- ✅ Fast loading (no heavy frameworks)

## Customization

### Update Download Links
Edit `index.html` and replace `#` with actual download URLs:
```html
<a href="YOUR_DOWNLOAD_URL" class="download-button">
```

### Add Screenshot/Demo
Replace the placeholder in the "See It In Action" section with:
- A screenshot of your dashboard
- A GIF showing the app in action
- Or a video embed

### Update GitHub Links
All GitHub links point to `https://github.com/agBabbbyCakes/phoenix` - update if your repo URL is different.

### Customize Colors
Edit the CSS variables in the `<style>` section:
```css
:root {
    --primary: #2563eb;
    --primary-dark: #1e40af;
}
```

## Email Collection

The site includes a Netlify form for email collection. To set it up:

1. Deploy to Netlify
2. Forms are automatically enabled
3. View submissions in Netlify dashboard → Forms
4. Optionally connect to Zapier/Make for email list integration

## Analytics (Optional)

To add analytics, add before `</head>`:
```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

Or use Netlify Analytics (paid feature).

## Local Development

Just open `index.html` in a browser, or use a simple server:

```bash
cd marketing-site
python3 -m http.server 8000
# Or
npx serve .
```

Then visit `http://localhost:8000`

## Next Steps

1. **Add Screenshots**: Replace placeholder with real dashboard screenshots
2. **Create Demo GIF**: Show the app in action
3. **Buy Domain**: Get a custom domain for trust
4. **Update Links**: Add actual download URLs once builds are ready
5. **Add Docs**: Link to documentation or create a simple docs section

