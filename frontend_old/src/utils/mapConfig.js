// 高德地图配置
export const AMAP_CONFIG = {
  // 请在高德开放平台申请您的API Key
  key: 'YOUR_AMAP_KEY', // 替换为您的高德地图API Key
  version: '1.4.15',
  plugins: ['AMap.Geolocation', 'AMap.ToolBar', 'AMap.Scale']
};

// 默认地图中心点（北京天安门）
export const DEFAULT_CENTER = [116.397428, 39.90923];

// 地图样式配置
export const MAP_STYLES = {
  normal: 'amap://styles/normal',
  dark: 'amap://styles/dark',
  light: 'amap://styles/light',
  satellite: 'amap://styles/satellite'
};
