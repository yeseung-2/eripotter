import axios from 'axios';

const instance = axios.create({
  // .env(.env.local)에서 NEXT_PUBLIC_API_URL이 있으면 사용,
  // 없으면 로컬 게이트웨이로 기본값.
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080',
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
});

instance.interceptors.request.use(
  (config) => {
    console.log('API 요청:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('API 요청 에러:', error);
    return Promise.reject(error);
  }
);

instance.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API 응답 에러:', error.response?.status, error.response?.data);
    return Promise.reject(error);
  }
);

export default instance;
