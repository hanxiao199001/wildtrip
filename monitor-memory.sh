#!/bin/bash
# 内存监控脚本 - 防止SEO批量生成占用过多内存

LOG_FILE="/root/clawd/wildtrip/logs/memory-monitor.log"
ALERT_THRESHOLD=85  # 内存使用超过85%时暂停SEO

while true; do
    # 获取内存使用百分比
    MEM_USED=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100}')
    
    # 记录日志
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 内存使用: ${MEM_USED}%" >> "$LOG_FILE"
    
    # 检查是否超过阈值
    if [ "$MEM_USED" -gt "$ALERT_THRESHOLD" ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️ 内存使用过高: ${MEM_USED}%，暂停SEO脚本" >> "$LOG_FILE"
        
        # 暂停SEO脚本
        pkill -STOP -f "seo-batch-generate.js"
        
        # 等待内存降低
        sleep 30
        
        # 检查内存是否降低
        MEM_AFTER=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100}')
        if [ "$MEM_AFTER" -lt 70 ]; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 内存降至 ${MEM_AFTER}%，恢复SEO脚本" >> "$LOG_FILE"
            pkill -CONT -f "seo-batch-generate.js"
        fi
    fi
    
    # 每30秒检查一次
    sleep 30
done
