// config.js - Configuración de API para el proyecto
(function() {
  // Detectar si estamos en desarrollo o producción
  const isLocal = window.location.hostname === 'localhost' || 
                  window.location.hostname === '127.0.0.1';
  
  // URL de tu backend en Render
  const PRODUCTION_API = "https://proyectoairquality-aguachica.onrender.com";
  
  // URLs según el entorno
  const API_URLS = {
    development: "http://127.0.0.1:5000",
    production: PRODUCTION_API
  };
  
  // Configuración global de la aplicación
  window.APP_CONFIG = {
    // URL base de la API
    API_BASE: isLocal ? API_URLS.development : API_URLS.production,
    
    // API Key de OpenWeather
    OPENWEATHER_API_KEY: "0fceb022e90eecf2c580132f9ccd74ce",
    
    // Entorno actual
    ENVIRONMENT: isLocal ? 'development' : 'production',
    
    // Helper para construir URLs completas de API
    getApiUrl: function(endpoint) {
      // Asegurar que endpoint empiece con /
      if (!endpoint.startsWith('/')) {
        endpoint = '/' + endpoint;
      }
      return this.API_BASE + endpoint;
    },
    
    // Helper para verificar conexión con el backend
    checkConnection: async function() {
      try {
        const url = this.getApiUrl('/api/status');
        console.log('🔍 Verificando conexión con:', url);
        
        const response = await fetch(url, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json'
          }
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
          console.log('✅ API conectada correctamente');
          console.log('📊 Estado:', data.data);
          return true;
        }
        
        console.warn('⚠️ API respondió pero con error:', data);
        return false;
      } catch (error) {
        console.error('❌ Error conectando con API:', error);
        console.error('URL intentada:', this.getApiUrl('/api/status'));
        return false;
      }
    },
    
    // Log de configuración actual
    logConfig: function() {
      console.log('═══════════════════════════════════════');
      console.log('🔧 CONFIGURACIÓN DE LA APLICACIÓN');
      console.log('═══════════════════════════════════════');
      console.log('Entorno:', this.ENVIRONMENT);
      console.log('API Base:', this.API_BASE);
      console.log('═══════════════════════════════════════');
    }
  };
  
  // Mostrar configuración siempre
  window.APP_CONFIG.logConfig();
})();