# Railway Deployment Disconnection

This project is **NOT** configured for Railway deployment. The marketing site is deployed on Netlify only.

## How to Disconnect Railway (if connected)

If Railway is currently deploying this repository, follow these steps to disconnect:

### Option 1: Via Railway Dashboard
1. Go to [https://railway.app](https://railway.app)
2. Log in to your account
3. Find the project/service that's deploying this repository
4. Click on the project
5. Go to **Settings**
6. Scroll down to **Danger Zone**
7. Click **Delete Project** or **Disconnect Repository**

### Option 2: Via GitHub Integration
1. Go to [https://railway.app](https://railway.app)
2. Navigate to your project
3. Go to **Settings** → **GitHub**
4. Click **Disconnect** or **Unlink Repository**

### Option 3: Remove Service Only
1. In your Railway project dashboard
2. Find the service that's auto-deploying
3. Click the three dots menu (⋯) on the service
4. Select **Delete Service**

## Current Deployment Strategy

- **Marketing Site**: Deployed on Netlify (`index.html` and `releases.html`)
- **Backend Service**: Can be deployed on Render.com (see `render.yaml`)
- **Railway**: Not used for this project

## Notes

- Railway might have auto-detected this repository if it was connected to your GitHub account
- Removing the Railway project/service will stop all automatic deployments
- Your Netlify deployment will continue to work independently

