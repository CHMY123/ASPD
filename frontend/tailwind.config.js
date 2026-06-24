/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // 主色调 - 薄荷绿系
        'brand-mint': '#4ECDC4',
        'brand-dark': '#2A7E76',
        'brand-light': '#A8E6CF',
        
        // 辅助色
        'accent-orange': '#FF9F43',
        'accent-coral': '#FF6B6B',
        'accent-lavender': '#A29BFE',
        'accent-sky': '#74B9FF',
        
        // 功能色
        'success': '#00B894',
        'warning': '#FDCB6E',
        'error': '#E17055',
        'info': '#0984E3',
        
        // 中性色
        'text-primary': '#2D3436',
        'text-secondary': '#636E72',
        'text-light': '#B2BEC3',
        'border': '#E8ECF0',
        'background-primary': '#FFFFFF',
        'background-secondary': '#F8FAFC',
        'background-dark': '#F1F5F9',
      },
      fontFamily: {
        'sans': ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        'mono': ['JetBrains Mono', 'Consolas', 'Monaco', 'monospace'],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
      borderRadius: {
        'xl': '12px',
      },
      boxShadow: {
        'soft': '0 2px 8px rgba(0,0,0,0.06)',
        'medium': '0 4px 16px rgba(0,0,0,0.1)',
      },
      animation: {
        'slide-in': 'slideIn 0.3s ease-out',
        'fade-in': 'fadeIn 0.2s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
      },
      keyframes: {
        slideIn: {
          'from': { opacity: '0', transform: 'translateY(10px)' },
          'to': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: {
          'from': { opacity: '0' },
          'to': { opacity: '1' },
        },
        scaleIn: {
          'from': { opacity: '0', transform: 'scale(0.95)' },
          'to': { opacity: '1', transform: 'scale(1)' },
        },
      },
    },
  },
  plugins: [],
}