# 🚀 Deployment Guide - Render

This guide will help you deploy your E-commerce API on Render for free!

## 📋 Prerequisites

- [Render Account](https://render.com) (free)
- GitHub repository connected
- Basic understanding of environment variables

## 🎯 Quick Deployment Steps

### 1. **Create Render Account**
- Go to [render.com](https://render.com)
- Sign up with your GitHub account
- Connect your E-commerce API repository

### 2. **Create PostgreSQL Database**
- Click **"New +"** → **"PostgreSQL"**
- **Name**: `ecommerce-api-db`
- **Database**: `ecommerce`
- **User**: `ecommerce_user`
- **Region**: Choose closest to you
- **Plan**: Free
- Click **"Create Database"**

### 3. **Create Web Service**
- Click **"New +"** → **"Web Service"**
- **Connect** your GitHub repository
- **Name**: `ecommerce-api`
- **Environment**: `Python 3`
- **Region**: Same as database
- **Branch**: `master`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Click **"Create Web Service"**

### 4. **Configure Environment Variables**
In your web service, add these environment variables:

```env
DATABASE_URL=postgresql://ecommerce_user:YOUR_PASSWORD@YOUR_HOST:5432/ecommerce
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=false
APP_NAME=E-commerce API
ALLOWED_ORIGINS=*
```

**Note**: `DATABASE_URL` will be automatically filled from your database connection.

### 5. **Run Database Migrations**
After deployment, run migrations:

```bash
# Get your service URL from Render dashboard
# Then run migrations via Render shell or redeploy
```

## 🔧 Manual Configuration (Alternative)

If you prefer manual setup:

### **Database Setup**
1. Create PostgreSQL service
2. Copy connection string
3. Note database name, user, and password

### **Web Service Setup**
1. Create web service
2. Set build and start commands
3. Configure environment variables
4. Deploy

## 📊 Environment Variables Reference

| Variable | Value | Description |
|----------|-------|-------------|
| `DATABASE_URL` | Auto-filled | PostgreSQL connection string |
| `SECRET_KEY` | Generated | JWT secret key |
| `ALGORITHM` | HS256 | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 30 | Token expiration time |
| `DEBUG` | false | Production mode |
| `APP_NAME` | E-commerce API | Application name |
| `ALLOWED_ORIGINS` | * | CORS origins |

## 🚨 Important Notes

### **Free Tier Limitations**
- **Web Service**: 750 hours/month
- **Database**: 90 days trial, then $7/month
- **Bandwidth**: 100GB/month

### **Production Considerations**
- **HTTPS**: Automatically provided
- **Custom Domain**: Available on paid plans
- **Scaling**: Manual scaling on free tier

## 🔍 Troubleshooting

### **Common Issues**

1. **Build Fails**
   - Check Python version compatibility
   - Verify requirements.txt syntax
   - Check build logs

2. **Database Connection Fails**
   - Verify DATABASE_URL format
   - Check database status
   - Verify network access

3. **App Won't Start**
   - Check start command
   - Verify PORT environment variable
   - Check application logs

### **Useful Commands**

```bash
# Check service logs
# Use Render dashboard → Logs

# Check database status
# Use Render dashboard → Database → Status

# Restart service
# Use Render dashboard → Manual Deploy
```

## 🌐 After Deployment

### **Your API Will Be Available At:**
- **Base URL**: `https://your-service-name.onrender.com`
- **Documentation**: `https://your-service-name.onrender.com/docs`
- **ReDoc**: `https://your-service-name.onrender.com/redoc`
- **Health Check**: `https://your-service-name.onrender.com/health`

### **Update README.md**
Replace placeholder URLs with your actual Render URLs:

```markdown
## 🚀 Live Demo

- **API Base URL**: https://your-service-name.onrender.com
- **Swagger Docs**: https://your-service-name.onrender.com/docs
- **ReDoc**: https://your-service-name.onrender.com/redoc
- **Health Check**: https://your-service-name.onrender.com/health
```

## 🎉 Success!

Once deployed, you'll have:
- ✅ **Live API** accessible worldwide
- ✅ **Professional hosting** for your portfolio
- ✅ **HTTPS security** automatically configured
- ✅ **Database management** handled by Render
- ✅ **Easy scaling** when needed

Your E-commerce API will be live and ready to impress recruiters and hiring managers! 🚀✨
