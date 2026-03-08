import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

// Инициализация Telegram WebApp SDK
const initTelegramApp = () => {
  if (window.Telegram?.WebApp) {
    const tg = window.Telegram.WebApp
    
    // Сообщаем Telegram что приложение готово
    tg.ready()
    
    // Разворачиваем на весь экран
    tg.expand()
    
    // Настраиваем цвета хедера
    tg.setHeaderColor('#121212')
    tg.setBackgroundColor('#121212')
    
    // Включаем подтверждение жестов
    tg.enableClosingConfirmation()
    
    console.log('Telegram WebApp initialized:', {
      platform: tg.platform,
      version: tg.version,
      colorScheme: tg.colorScheme,
      themeParams: tg.themeParams
    })
  }
}

initTelegramApp()

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
