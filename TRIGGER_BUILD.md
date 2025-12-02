# Trigger Linux Build Now

## Immediate Build Options:

### 1. GitHub Actions (Fastest - ~5-10 minutes)

**Option A: Via Web UI**
1. Go to: https://github.com/YOUR_USERNAME/phoenix/actions
2. Click "Build All Platforms" workflow
3. Click "Run workflow" (top right)
4. Select branch → Click "Run workflow"
5. Wait for build to complete
6. Download `linux-zip` artifact

**Option B: Via Git Tag (Automatic)**
```powershell
git tag v1.0.0-build
git push origin v1.0.0-build
```
This automatically triggers the build workflow.

**Option C: Via GitHub CLI**
```powershell
gh workflow run "Build All Platforms"
gh run watch
gh run download
```

### 2. Docker (If Docker Desktop is Running)

```powershell
# Build the image
docker build -f Dockerfile.linux-build -t phoenix-linux-builder .

# Create container and extract
$cid = docker create phoenix-linux-builder
docker start $cid
Start-Sleep -Seconds 60  # Wait for build
docker cp "${cid}:/app/downloads/linux/." "downloads/linux/"
docker rm -f $cid
```

### 3. Manual WSL Build

```powershell
wsl
cd /mnt/c/Users/agonzalez7/Documents/Gonzalez-CODE/phoenix
chmod +x build_linux_standalone.sh
./build_linux_standalone.sh
exit
```

The build infrastructure is complete and ready. The actual executable needs to be compiled in a Linux environment.


