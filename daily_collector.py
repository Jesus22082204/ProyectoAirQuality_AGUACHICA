#!/usr/bin/env python3
"""
daily_collector.py - Script unificado para recolección diaria de datos
Combina:
1. Recolección de datos actuales (cada 24h)
2. Backfill de últimos 5 días (una vez al día)

Este script debe ejecutarse:
- Automáticamente cada 24 horas (configurado en Render Cron Jobs)
- Manualmente cuando sea necesario
"""

import os
import json
import logging
from datetime import datetime, timezone
from data_collector import AirQualityCollector

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

def load_api_key():
    """Cargar API key desde variable de entorno o config.json"""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if api_key:
        return api_key
    
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f).get("openweather_api_key")
    except FileNotFoundError:
        return None

def collect_current_data(collector):
    """Recolectar datos actuales de todas las ubicaciones"""
    logging.info("=" * 60)
    logging.info("INICIANDO RECOLECCIÓN DE DATOS ACTUALES")
    logging.info("=" * 60)
    
    try:
        successful, failed = collector.collect_all_locations()
        
        logging.info(f"✅ Recolección actual completada:")
        logging.info(f"   - Exitosos: {successful}")
        logging.info(f"   - Fallidos: {failed}")
        
        return successful, failed
    except Exception as e:
        logging.error(f"❌ Error en recolección actual: {e}")
        return 0, len(collector.locations)

def collect_historical_data(collector):
    """Recolectar datos históricos (últimos 5 días) de todas las ubicaciones"""
    logging.info("=" * 60)
    logging.info("INICIANDO BACKFILL HISTÓRICO (5 DÍAS)")
    logging.info("=" * 60)
    
    try:
        results = collector.collect_last5days_all_locations()
        
        total_saved = sum(
            (r[1].get("saved", 0) if isinstance(r[1], dict) else 0) 
            for r in results
        )
        
        successful_locations = sum(
            1 for r in results 
            if isinstance(r[1], dict) and r[1].get("success", False)
        )
        
        logging.info(f"✅ Backfill histórico completado:")
        logging.info(f"   - Ubicaciones procesadas: {successful_locations}/{len(results)}")
        logging.info(f"   - Total de filas guardadas: {total_saved}")
        
        return total_saved, len(results)
    except Exception as e:
        logging.error(f"❌ Error en backfill histórico: {e}")
        return 0, 0

def main():
    """Función principal que ejecuta ambas recolecciones"""
    start_time = datetime.now(timezone.utc)
    
    logging.info("🚀 INICIANDO RECOLECCIÓN DIARIA UNIFICADA")
    logging.info(f"📅 Fecha y hora (UTC): {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info("=" * 60)
    
    # Cargar API key
    api_key = load_api_key()
    if not api_key:
        logging.error("❌ OPENWEATHER_API_KEY no configurada")
        logging.error("Configura la variable de entorno o crea config.json")
        return False
    
    # Crear instancia del recolector
    collector = AirQualityCollector(api_key)
    logging.info(f"📍 Ubicaciones configuradas: {len(collector.locations)}")
    
    # 1. Recolectar datos actuales
    current_success, current_failed = collect_current_data(collector)
    
    # 2. Recolectar datos históricos (últimos 5 días)
    historical_saved, historical_total = collect_historical_data(collector)
    
    # Resumen final
    end_time = datetime.now(timezone.utc)
    duration = (end_time - start_time).total_seconds()
    
    logging.info("=" * 60)
    logging.info("📊 RESUMEN FINAL DE RECOLECCIÓN DIARIA")
    logging.info("=" * 60)
    logging.info(f"⏱️  Duración total: {duration:.2f} segundos")
    logging.info(f"📍 Datos actuales:")
    logging.info(f"   ✅ Exitosos: {current_success}")
    logging.info(f"   ❌ Fallidos: {current_failed}")
    logging.info(f"📚 Datos históricos:")
    logging.info(f"   📊 Filas guardadas: {historical_saved}")
    logging.info(f"   📍 Ubicaciones: {historical_total}")
    logging.info(f"🏁 Finalizado: {end_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    logging.info("=" * 60)
    
    # Retornar True si todo salió bien
    return current_success > 0 or historical_saved > 0

if __name__ == "__main__":
    try:
        success = main()
        exit_code = 0 if success else 1
        exit(exit_code)
    except Exception as e:
        logging.error(f"💥 Error crítico: {e}")
        exit(1)