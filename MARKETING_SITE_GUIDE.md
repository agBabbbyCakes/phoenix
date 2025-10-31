# Marketing Site Deployment Guide

## Overview

The marketing site is ready to deploy to Netlify. It's a clean, professional landing page that emphasizes Silverback's core values: **Simple. Private. Powerful. Local control.**

## File Structure

```
marketing-site/
├── index.html          # Main landing page
├── netlify.toml        # Netlify configuration
└── README.md          # Deployment instructions
```

## Deployment Steps

### 1. Quick Deploy (5 minutes)

**Option A: GitHub + Netlify (Recommended)**
1. Create a new GitHub repo (optional, or use existing)
2. Push the `marketing-site` folder
3. Go to [Netlify](https://app.netlify.com)
4. "Add new site" → "Import from Git"
5. Connect GitHub, select repo
6. Build settings:
   - Build command: (leave empty)
   - Publish directory: `marketing-site` (or root if it's its own repo)
7. Deploy!

**Option B: Netlify Drop (Fastest)**
1. Go to [Netlify Drop](https://app.netlify.com/drop)
2. Drag the `marketing-site` folder
3. Done! Get your URL

### 2. Custom Domain (Optional but Recommended)

**Why it matters:**
- Builds trust
- Professional appearance
- Easy to remember

**Suggested domains:**
- `silverback.dev` (~$15/year)
- `silverback.app` (~$20/year)
- `silverbacktools.com` (~$12/year)

**Setup:**
1. Buy domain (Namecheap, Google Domains, etc.)
2. In Netlify: Site settings → Domain management
3. Add custom domain
4. Follow DNS instructions (usually just add a CNAME record)

### 3. Update Download Links

Once your Briefcase builds are ready, update the download buttons in `index.html`:

```html
<!-- Replace these hrefs -->
<a href="YOUR_GITHUB_RELEASES_URL/macos.dmg" class="download-button">
<a href="YOUR_GITHUB_RELEASES_URL/windows.msi" class="download-button">
<a href="YOUR_GITHUB_RELEASES_URL/linux.AppImage" class="download-button">
```

### 4. Add Screenshots/Demo

Replace the placeholder in the "See It In Action" section:

**Option A: Screenshot**
```html
<img src="dashboard-screenshot.png" alt="Silverback Dashboard" class="rounded-lg shadow-xl">
```

**Option B: GIF Demo**
```html
<img src="dashboard-demo.gif" alt="Silverback in Action" class="rounded-lg shadow-xl">
```

**Option C: Video**
```html
<video autoplay loop muted class="rounded-lg shadow-xl">
  <source src="demo.mp4" type="video/mp4">
</video>
```

## Key Sections

### Hero Section
- Clear value proposition
- Download CTA front and center
- Simple, confident messaging

### Value Propositions
- Local Control
- Real-Time Monitoring
- Simple & Powerful

### Trust Section
- Open Source
- Local First
- Privacy Focused
- Developer Built

### Download Section
- Platform-specific downloads
- Version info
- Release notes link

## Email Capture

The site includes a Netlify form for email subscriptions:

**Setup:**
1. Deploy to Netlify (forms auto-enabled)
2. View submissions: Netlify dashboard → Forms
3. Export or integrate with email service (Mailchimp, etc.)

**Optional Integration:**
- Zapier: Auto-add to email list
- Make.com: Connect to your email service
- Netlify Functions: Custom webhook handler

## Analytics (Optional)

**Netlify Analytics:**
- Built-in, paid feature
- Simple setup in dashboard

**Google Analytics:**
Add to `index.html` before `</head>`:
```html
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

## Maintenance

**Update Content:**
- Edit `index.html`
- Push to GitHub
- Netlify auto-deploys

**Add New Sections:**
- Copy existing section structure
- Maintain consistent styling
- Keep it simple

## Next Steps After Deployment

1. ✅ Deploy to Netlify
2. ✅ Add custom domain (optional but recommended)
3. ✅ Add real screenshots/demo
4. ✅ Update download links when builds are ready
5. ✅ Test on mobile devices
6. ✅ Share with beta testers for feedback

## Messaging Guidelines

**Tone:**
- Confident, not hype-y
- Straightforward and clear
- Professional but approachable

**Key Messages:**
- Local control / privacy
- Simple to use
- Powerful features
- No tracking / telemetry
- Open source transparency

**What NOT to do:**
- Overpromise features
- Use marketing jargon
- Bury the download CTA
- Make it complicated

## Support

If you need help:
- Netlify docs: https://docs.netlify.com
- Netlify community: https://answers.netlify.com
- Netlify support: support@netlify.com

---

**Remember:** The goal is momentum, not perfection. Ship it, get feedback, iterate.

