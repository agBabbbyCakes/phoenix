# Quick Build Linux - Choose Your Method

## 🚀 Fastest Option: GitHub Actions (Recommended)

**Just trigger the workflow:**

1. Go to your GitHub repository
2. Click on **"Actions"** tab
3. Click **"Build All Platforms"** workflow
4. Click **"Run workflow"** button (top right)
5. Select your branch and click **"Run workflow"**
6. Wait ~5-10 minutes for the build
7. Download the `linux-zip` artifact

**OR push a tag to trigger automatically:**
```bash
git tag v1.0.0
git push origin v1.0.0
```

## 🐳 Option 2: Docker (If you have Docker Desktop)

```powershell
# In PowerShell
docker build -f Dockerfile.linux-build -t phoenix-linux-builder .
docker create --name phoenix-builder phoenix-linux-builder
New-Item -ItemType Directory -Force -Path "downloads\linux"
docker cp phoenix-builder:/app/downloads/linux/. downloads/linux/
docker rm phoenix-builder
```

## 🐧 Option 3: WSL (If you have WSL installed)

```powershell
wsl bash build_linux_standalone.sh
```

## 📋 Option 4: Use the PowerShell Helper

```powershell
.\build_linux_now.ps1
```

This will guide you through the available options.

---

**The built file will be:** `downloads/linux/PhoenixDashboard-Linux-x86_64.zip`

