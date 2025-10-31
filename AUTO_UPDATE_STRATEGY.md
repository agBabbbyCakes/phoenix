# Auto-Update Strategy for Phoenix Dashboard

## Overview

Implement an auto-update mechanism that allows pushing updates without requiring users to manually rebuild or reinstall the app.

## Strategy Outline

### 1. Update Server Architecture

**Components:**
- **Update API Server**: Host a simple REST API that provides version information and update packages
- **Manifest File**: JSON file containing current version, download URLs, changelog
- **Update Client**: Built into the Phoenix Dashboard app

### 2. Update Flow

**Check Phase:**
- On app startup, check for updates (configurable interval)
- Send current app version to update server
- Compare with latest available version
- Store last check timestamp to avoid excessive checks

**Download Phase:**
- If update available, prompt user (or auto-download based on settings)
- Download update package (delta or full)
- Verify checksum/signature
- Store in temp directory

**Install Phase:**
- Close current app instance
- Backup current installation
- Extract new version
- Replace application files (or use symlinks)
- Restart application

**Rollback:**
- Keep previous version as backup
- Allow rollback if update fails
- Auto-rollback on critical errors

### 3. Implementation Approaches

**Option A: Application-Level Updates**
- Update Python packages and app code
- Pros: Simple, works across platforms
- Cons: Requires Python runtime, larger downloads

**Option B: Full Bundle Replacement**
- Replace entire Briefcase bundle
- Pros: Complete updates, consistent state
- Cons: Larger downloads, platform-specific

**Option C: Hybrid Approach** (Recommended)
- Small updates: Update app code only
- Major updates: Full bundle replacement
- Use semantic versioning (major.minor.patch)

### 4. Update Server Requirements

**Endpoints:**
```
GET /api/version/check?current_version=0.1.0&platform=macOS
  → Returns: {latest_version, download_url, changelog, checksum}

GET /api/version/download?version=0.1.1&platform=macOS
  → Returns: Update package (zip/tar.gz)
```

**Storage:**
- Version manifest (JSON)
- Update packages per platform
- Signature files for verification

### 5. Security Considerations

- **Code Signing**: Verify update packages are signed
- **HTTPS Only**: All update traffic over HTTPS
- **Checksum Verification**: SHA-256 checksums for packages
- **Signature Verification**: Verify package signatures before install

### 6. User Experience

**Update Notifications:**
- Show update available badge
- Display changelog
- "Install Now" or "Remind Later" options
- Background download option

**Settings:**
- Auto-update (enabled/disabled)
- Update frequency (daily/weekly/on-demand)
- Beta channel option

**Progress Indicators:**
- Download progress bar
- Installation status
- Restart prompt

### 7. Rollout Strategy

**Phased Rollout:**
- Beta testers first (10%)
- Gradual rollout (25%, 50%, 100%)
- Monitor error rates, pause if issues

**A/B Testing:**
- Different update frequencies
- Different notification styles
- Collect telemetry on update success rates

### 8. Implementation Priority

**Phase 1: Basic Check & Download**
- Manual update check
- Download and install updates
- Basic error handling

**Phase 2: Auto-Check & Notifications**
- Automatic version checking
- User notifications
- Settings UI

**Phase 3: Background Updates**
- Background download
- Scheduled updates
- Auto-install (optional)

**Phase 4: Advanced Features**
- Delta updates
- Rollback mechanism
- Telemetry and analytics

## Technical Notes

- Use `requests` library for update server communication
- Store update preferences in local config file
- Use platform-specific update mechanisms where possible
- Consider using libraries like `pyupdater` or `pyinstaller-update`

## Future Considerations

- Cloud-based update server (AWS S3, GitHub Releases)
- CDN for fast downloads
- Staging environment for testing updates
- Update analytics dashboard

