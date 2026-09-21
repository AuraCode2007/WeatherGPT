#!/usr/bin/env python
"""
WeatherGPT Setup Script

This script helps you get started with WeatherGPT by:
1. Checking if required API keys are configured
2. Providing setup instructions for missing keys
3. Testing basic connectivity
"""

import os
import requests
import json
from pathlib import Path

def check_env_file():
    """Check if .env file exists and has required keys"""
    env_path = Path(".env")
    
    if not env_path.exists():
        print("❌ .env file not found")
        return False
    
    with open(env_path, 'r') as f:
        content = f.read()
    
    required_keys = ["OPENWEATHERMAP_API_KEY", "GEMINI_API_KEY"]
    missing_keys = []
    
    for key in required_keys:
        if f"{key}=" not in content or f"{key}=your_" in content:
            missing_keys.append(key)
    
    if missing_keys:
        print(f"❌ Missing or placeholder API keys: {', '.join(missing_keys)}")
        print("\nTo set up your API keys:")
        print("1. Get OPENWEATHERMAP_API_KEY from: https://openweathermap.org/api")
        print("2. Get GEMINI_API_KEY from: https://aistudio.google.com/")
        print("3. Create/update .env file with your keys")
        return False
    
    print("✅ API keys are configured")
    return True

def test_backend_health():
    """Test if backend health endpoint is working"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend health check passed")
            return True
        else:
            print(f"❌ Backend health check failed: HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Is it running?")
        print("   Run: python -m uvicorn backend.main:app --reload --port 8000")
        return False
    except Exception as e:
        print(f"❌ Backend health check error: {e}")
        return False

def get_setup_instructions():
    """Print setup instructions"""
    print("\n" + "="*60)
    print("WEATHERGPT SETUP GUIDE")
    print("="*60)
    
    print("\n1. Get API Keys:")
    print("   • OpenWeatherMap API Key:")
    print("     - Sign up at https://openweathermap.org/api")
    print("     - Choose a paid plan (starts at ~$10/month)")
    print("     - API key is available in your dashboard")
    print("   • Gemini API Key:")
    print("     - Visit https://aistudio.google.com/")
    print("     - Create account and get API key")
    
    print("\n2. Create .env file:")
    print("   Copy the following to your project root as .env:")
    print("""
OPENWEATHERMAP_API_KEY=your_openweathermap_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=postgresql://user:password@localhost/weather_gpt
REDIS_URL=redis://localhost:6379
APP_ENV=development
BACKEND_URL=http://localhost:8000
GEMINI_MODEL=gemini-3.5-flash-lite
""")
    
    print("\n3. Install Python dependencies:")
    print("   pip install -r frontend/requirements.txt")
    print("   pip install uvicorn streamlit")
    
    print("\n4. Run the application:")
    print("   Terminal 1: python -m uvicorn backend.main:app --reload --port 8000")
    print("   Terminal 2: streamlit run frontend/weather_gpt_frontend.py --server.port 8501")
    
    print("\n5. Frontend URLs:")
    print("   • Backend API: http://localhost:8000")
    print("   • API Documentation: http://localhost:8000/docs")
    print("   • Frontend UI: http://localhost:8501")

if __name__ == "__main__":
    print("🌦️  WeatherGPT Setup Checker")
    print("="*60)
    
    env_ok = check_env_file()
    backend_ok = test_backend_health()
    
    if env_ok and backend_ok:
        print("\n✅ All checks passed!")
        print("WeatherGPT is ready to use.")
    else:
        print("\n⚠️  Setup incomplete")
        get_setup_instructions()