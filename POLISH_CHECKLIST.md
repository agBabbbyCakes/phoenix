# Phoenix Dashboard - Polish & Trust Checklist

## Code Signing & Security

### macOS Code Signing
- [ ] **Apple Developer Account**: Sign up for Apple Developer Program ($99/year)
- [ ] **Developer ID Certificate**: Obtain Developer ID Application certificate
- [ ] **Code Sign App**: Sign the .app bundle with `codesign --deep --force --sign "Developer ID Application: Your Name" "Phoenix Dashboard.app"`
- [ ] **Notarize App**: Submit to Apple for notarization (required for Gatekeeper)
- [ ] **Hardened Runtime**: Enable hardened runtime with entitlements
- [ ] **Test Signed Build**: Verify signature with `codesign --verify --verbose "Phoenix Dashboard.app"`
- [ ] **Gatekeeper Test**: Test on clean macOS machine to verify Gatekeeper acceptance

### Windows Code Signing
- [ ] **Code Signing Certificate**: Obtain certificate from trusted CA (DigiCert, Sectigo, etc.)
- [ ] **Sign Executable**: Use `signtool` to sign the .exe and .msi
- [ ] **Timestamp Server**: Add timestamp to signature for long-term validity
- [ ] **Test Signature**: Verify with `signtool verify /pa "Phoenix Dashboard.exe"`
- [ ] **Windows Defender**: Submit to Windows Defender for scanning (optional but recommended)

### Certificate Requirements
- [ ] Choose between self-signed (testing) vs. CA-signed (production)
- [ ] Store certificates securely (keychain/password manager)
- [ ] Document certificate renewal dates
- [ ] Automate signing in build process

## Custom Installer Icons & UI

### App Icons
- [ ] **App Icon Design**: Create 512x512 master icon (PNG/SVG)
- [ ] **Icon Variations**: Generate platform-specific sizes
  - macOS: 16x16, 32x32, 128x128, 256x256, 512x512, 1024x1024
  - Windows: 16x16, 32x32, 48x48, 256x256
  - Linux: 16x16, 32x32, 48x48, 256x256
- [ ] **Icon Format**: Convert to .icns (macOS), .ico (Windows)
- [ ] **Test Icons**: Verify icons display correctly in Finder/Explorer

### Installer Branding
- [ ] **macOS DMG Background**: Custom background image for DMG
- [ ] **macOS DMG Icon**: Place app icon with drag-to-Applications arrow
- [ ] **Windows Installer UI**: Custom installer wizard graphics
- [ ] **Linux AppImage Icon**: Ensure proper icon embedding
- [ ] **Installer License**: Add license agreement to installer
- [ ] **Installer Readme**: Include release notes in installer

### Resources Needed
- [ ] Create `resources/phoenix.icns` (macOS)
- [ ] Create `resources/phoenix.ico` (Windows)
- [ ] Create `resources/phoenix.png` (Linux, 256x256)
- [ ] Create DMG background image (if using custom DMG)

## Splash Screen

### Implementation
- [ ] **Design Splash Screen**: Create splash screen graphic (800x600 or similar)
- [ ] **Version Display**: Show version number on splash
- [ ] **Loading Animation**: Optional spinner or progress bar
- [ ] **Brand Colors**: Match app theme colors
- [ ] **Timing**: Display for minimum 2-3 seconds or until server ready

### Current Status
- ✅ Basic splash screen implemented in `phoenix_dashboard/__main__.py`
- [ ] Replace with branded splash image
- [ ] Add app logo/branding
- [ ] Add loading animation
- [ ] Add version info display

## App Menu

### macOS Menu Bar
- [ ] **Application Menu**: Phoenix Dashboard menu (About, Preferences, Quit)
- [ ] **File Menu**: (if applicable)
- [ ] **Edit Menu**: Standard macOS Edit menu items
- [ ] **View Menu**: Refresh, Reload options
- [ ] **Window Menu**: Window management (if multi-window)
- [ ] **Help Menu**: Help, Documentation, Support

### Windows Menu Bar
- [ ] **File Menu**: Standard Windows File menu
- [ ] **Edit Menu**: Standard Edit menu
- [ ] **View Menu**: Refresh, Reload
- [ ] **Tools Menu**: Settings, Preferences
- [ ] **Help Menu**: Help, About

### Implementation
- [ ] Create menu bar structure in tkinter
- [ ] Add keyboard shortcuts (Cmd+Q, Cmd+, for preferences, etc.)
- [ ] Add About dialog with version info
- [ ] Add Preferences/Settings window

### Menu Items Priority
1. **About**: Show version, copyright, license
2. **Preferences**: App settings (port, auto-start browser, etc.)
3. **Check for Updates**: Manual update check
4. **Quit/Exit**: Proper app termination

## Local Settings Storage

### Storage Mechanism
- [ ] **Choose Storage**: Decide on storage format (JSON, configparser, SQLite)
- [ ] **Storage Location**: Platform-appropriate locations
  - macOS: `~/Library/Application Support/Phoenix Dashboard/`
  - Windows: `%APPDATA%/Phoenix Dashboard/`
  - Linux: `~/.config/phoenix-dashboard/`
- [ ] **Settings File**: Create `config.json` or `settings.ini`

### Settings to Store
- [ ] **Server Port**: User's preferred port (default: 8000)
- [ ] **Auto-open Browser**: Whether to auto-open browser on startup
- [ ] **Window Size/Position**: Remember window geometry
- [ ] **Update Preferences**: Auto-update enabled, check frequency
- [ ] **Last Update Check**: Timestamp of last update check
- [ ] **User Preferences**: Theme, language, etc.

### Implementation
- [ ] Create `phoenix_dashboard/config.py` for settings management
- [ ] Load settings on startup
- [ ] Save settings on change
- [ ] Provide settings UI (Preferences window)
- [ ] Handle missing/corrupt settings gracefully

## Version Info Display

### About Dialog
- [ ] **Version Number**: Display current version (0.1.0)
- [ ] **Build Number**: Include build number/commit hash
- [ ] **Copyright**: Copyright notice
- [ ] **License**: License information (MIT)
- [ ] **Credits**: Acknowledgments, libraries used
- [ ] **Links**: Website, GitHub, Support

### Version Sources
- [ ] **pyproject.toml**: Read version from `[project] version`
- [ ] **Runtime Display**: Show in About dialog
- [ ] **Build Info**: Include build date, Python version
- [ ] **Update Check**: Show latest available version

### Implementation
- [ ] Create About dialog window
- [ ] Read version from pyproject.toml at build time
- [ ] Display in Help > About menu
- [ ] Include in splash screen (optional)
- [ ] Add version to window title (optional)

## Additional Polish Items

### Error Handling
- [ ] **User-Friendly Messages**: Replace technical errors with user-friendly messages
- [ ] **Error Logging**: Log errors to file for debugging
- [ ] **Crash Reports**: Optional crash reporting service
- [ ] **Recovery**: Graceful handling of server crashes

### Documentation
- [ ] **User Guide**: Basic user documentation
- [ ] **Release Notes**: Changelog for each version
- [ ] **FAQ**: Common questions and answers
- [ ] **Support**: Contact information, support channels

### Performance
- [ ] **Startup Time**: Optimize app startup (< 5 seconds)
- [ ] **Memory Usage**: Monitor and optimize memory footprint
- [ ] **CPU Usage**: Ensure minimal CPU usage when idle
- [ ] **Network**: Handle network errors gracefully

### Accessibility
- [ ] **Keyboard Navigation**: Full keyboard support
- [ ] **Screen Readers**: Test with VoiceOver (macOS), NVDA (Windows)
- [ ] **High Contrast**: Support high contrast modes
- [ ] **Font Scaling**: Respect system font size preferences

### Testing
- [ ] **Clean Install Test**: Test on fresh system
- [ ] **Upgrade Test**: Test upgrading from previous version
- [ ] **Uninstall Test**: Ensure clean uninstall
- [ ] **Multi-Monitor**: Test on multi-monitor setups
- [ ] **Different Resolutions**: Test on various screen sizes

## Priority Levels

### High Priority (Before First Release)
1. ✅ Splash screen (basic version done)
2. [ ] App icons (all platforms)
3. [ ] About dialog with version
4. [ ] Local settings storage
5. [ ] Basic app menu
6. [ ] Error handling improvements

### Medium Priority (Short Term)
1. [ ] Code signing (macOS - required for distribution)
2. [ ] Windows code signing
3. [ ] Installer branding
4. [ ] Preferences window
5. [ ] Enhanced splash screen

### Low Priority (Long Term)
1. [ ] Auto-update mechanism
2. [ ] Advanced menu features
3. [ ] Accessibility features
4. [ ] Crash reporting
5. [ ] User documentation

## Implementation Notes

### Resources Directory Structure
```
resources/
├── phoenix.icns          # macOS icon
├── phoenix.ico           # Windows icon
├── phoenix.png           # Linux icon (256x256)
├── splash.png            # Splash screen image
└── dmg_background.png    # DMG background (optional)
```

### Code Organization
- `phoenix_dashboard/config.py` - Settings management
- `phoenix_dashboard/about.py` - About dialog
- `phoenix_dashboard/preferences.py` - Preferences window
- `phoenix_dashboard/menu.py` - Menu bar implementation

