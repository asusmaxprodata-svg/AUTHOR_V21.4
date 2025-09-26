# 🏥 Troubleshooting Masalah Unhealthy saat Deploy

Dokumentasi lengkap untuk mengatasi masalah "unhealthy" status saat deployment kang_bot.

## 🔍 **Penyebab Umum Masalah Unhealthy**

### 1. **Health Check Terlalu Ketat**
- Health check mengembalikan "unhealthy" untuk kondisi yang masih bisa ditoleransi
- Startup time container belum cukup
- Dependency loading issues

### 2. **Network Connectivity Issues**
- API calls ke exchange timeout
- WebSocket connection gagal
- Firewall atau network restrictions

### 3. **Resource Constraints**
- Memory atau CPU usage tinggi
- Disk space tidak cukup
- Container resource limits

### 4. **Configuration Issues**
- File .env tidak ada atau salah konfigurasi
- Missing config files
- Permission issues

## 🛠️ **Solusi yang Sudah Diimplementasi**

### 1. **Enhanced Health Check System**
```python
# core/health_check.py - Sudah diperbaiki
- Lebih toleran untuk deployment
- Warning-only checks untuk non-critical issues
- Startup phase detection
- Better error handling
```

### 2. **Improved Docker Configuration**
```yaml
# docker-compose.yml - Sudah diperbaiki
healthcheck:
  test: ["CMD", "python", "-c", "..."]
  interval: 90s        # Increased from 60s
  timeout: 15s         # Increased from 10s
  retries: 5           # Increased from 3
  start_period: 180s   # Increased from 120s
```

### 3. **Enhanced Entrypoint Script**
```bash
# entrypoint.sh - Sudah diperbaiki
- Retry mechanism untuk pre-flight checks
- Startup delay untuk container stability
- Better error handling
- Non-failing deployment approach
```

## 🚀 **Cara Menggunakan Script Deployment Baru**

### **Linux/Mac:**
```bash
# Gunakan script deployment yang robust
./scripts/robust_deploy.sh

# Atau untuk troubleshooting
./scripts/comprehensive_health_check.sh
```

### **Windows:**
```powershell
# Gunakan PowerShell script
.\scripts\robust_deploy.ps1

# Atau dengan parameter
.\scripts\robust_deploy.ps1 -MaxRetries 10 -SkipBuild
```

## 📋 **Langkah-langkah Troubleshooting**

### **1. Quick Check**
```bash
# Check container status
docker ps -a

# Check health status
docker inspect --format='{{.State.Health.Status}}' kang_bot_bot_1

# Check logs
docker-compose logs --tail 50
```

### **2. Comprehensive Health Check**
```bash
# Jalankan comprehensive health check
./scripts/comprehensive_health_check.sh
```

### **3. Manual Health Check**
```bash
# Run health check inside container
docker exec kang_bot_bot_1 python -c "
import sys; sys.path.append('.')
from core.health_check import get_health_status
import json
health = get_health_status()
print(json.dumps(health, indent=2))
"
```

### **4. Restart dengan Retry**
```bash
# Restart containers
docker-compose restart

# Atau gunakan robust deployment
./scripts/robust_deploy.sh
```

## 🔧 **Perbaikan Manual**

### **1. Jika Health Check Gagal**
```bash
# Check specific health check
docker exec kang_bot_bot_1 python -c "
from core.health_check import HealthChecker
checker = HealthChecker()
result = checker._check_websocket()
print(result)
"
```

### **2. Jika API Connectivity Issues**
```bash
# Test API connectivity
docker exec kang_bot_bot_1 python -c "
import requests
try:
    response = requests.get('https://api.bybit.com/v5/market/time', timeout=5)
    print(f'Status: {response.status_code}')
except Exception as e:
    print(f'Error: {e}')
"
```

### **3. Jika WebSocket Issues**
```bash
# Test WebSocket connectivity
docker exec kang_bot_bot_1 python -c "
from websocket import create_connection
try:
    ws = create_connection('ws://localhost:8765', timeout=2)
    ws.close()
    print('WebSocket OK')
except Exception as e:
    print(f'WebSocket Error: {e}')
"
```

## 📊 **Monitoring Post-Deployment**

### **1. Real-time Monitoring**
```bash
# Monitor container health
watch -n 5 'docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"'
```

### **2. Log Monitoring**
```bash
# Follow logs in real-time
docker-compose logs -f

# Check specific container logs
docker logs kang_bot_bot_1 -f
```

### **3. Health Check Monitoring**
```bash
# Monitor health check results
watch -n 30 'docker exec kang_bot_bot_1 python -c "
from core.health_check import get_health_status
health = get_health_status()
print(f\"Overall: {health.get(\"overall_status\")}\")
for name, result in health.get(\"checks\", {}).items():
    print(f\"{name}: {result.get(\"status\")}\")
"'
```

## ⚠️ **Troubleshooting Tips**

### **1. Container Startup Issues**
- **Problem**: Container tidak bisa start
- **Solution**: Check logs, verify .env file, check system resources

### **2. Health Check Timeout**
- **Problem**: Health check timeout
- **Solution**: Increase timeout, check network connectivity

### **3. API Connection Issues**
- **Problem**: Cannot connect to exchange API
- **Solution**: Check internet, verify API keys, check firewall

### **4. WebSocket Connection Issues**
- **Problem**: WebSocket server tidak accessible
- **Solution**: Check port availability, verify WebSocket server

### **5. Resource Issues**
- **Problem**: High CPU/Memory usage
- **Solution**: Check system resources, optimize container limits

## 🎯 **Best Practices**

### **1. Deployment**
- Selalu gunakan `./scripts/robust_deploy.sh` untuk deployment
- Monitor deployment process dengan comprehensive health check
- Jangan langsung restart jika ada warning, tunggu beberapa menit

### **2. Monitoring**
- Set up monitoring untuk container health
- Monitor logs secara berkala
- Check system resources secara rutin

### **3. Maintenance**
- Regular cleanup: `docker system prune -f`
- Update dependencies secara berkala
- Backup configuration files

## 📞 **Emergency Recovery**

### **Jika Semua Container Unhealthy:**
```bash
# 1. Stop semua containers
docker-compose down

# 2. Clean up
docker system prune -f

# 3. Rebuild dan restart
docker-compose build --no-cache
docker-compose up -d

# 4. Monitor dengan comprehensive health check
./scripts/comprehensive_health_check.sh
```

### **Jika Health Check Selalu Gagal:**
```bash
# 1. Disable health check sementara
# Edit docker-compose.yml, comment out healthcheck section

# 2. Restart containers
docker-compose restart

# 3. Debug manual
docker exec kang_bot_bot_1 python -c "
from core.health_check import get_health_status
import json
print(json.dumps(get_health_status(), indent=2))
"

# 4. Re-enable health check setelah masalah teratasi
```

## 📚 **Referensi**

- [Docker Health Check Documentation](https://docs.docker.com/engine/reference/builder/#healthcheck)
- [Docker Compose Health Check](https://docs.docker.com/compose/compose-file/compose-file-v3/#healthcheck)
- [kang_bot Health Check System](core/health_check.py)

---

**💡 Tips**: Jika masalah masih berlanjut, gunakan `./scripts/comprehensive_health_check.sh` untuk mendapatkan diagnosis lengkap dan rekomendasi spesifik.
