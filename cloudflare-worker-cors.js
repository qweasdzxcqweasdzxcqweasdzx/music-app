// Cloudflare Worker для CORS proxy
// Размещаем на workers.cloudflare.com

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  // Получаем URL из пути
  const url = new URL(request.url)
  
  // Извлекаем целевой URL из пути после /proxy/
  const targetPath = url.pathname.replace('/proxy/', '')
  const targetUrl = `http://192.168.31.97:8000/${targetPath}`
  
  // Создаём новый запрос к бэкенду
  const backendRequest = new Request(targetUrl, {
    method: request.method,
    headers: request.headers,
    body: request.body
  })
  
  // Получаем ответ от бэкенда
  const response = await fetch(backendRequest)
  
  // Добавляем CORS заголовки
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Allow-Credentials': 'true'
  }
  
  // Для OPTIONS запросов (preflight)
  if (request.method === 'OPTIONS') {
    return new Response(null, {
      headers: corsHeaders
    })
  }
  
  // Клонируем ответ с CORS заголовками
  const newResponse = new Response(response.body, response)
  
  // Добавляем CORS заголовки
  Object.entries(corsHeaders).forEach(([key, value]) => {
    newResponse.headers.set(key, value)
  })
  
  return newResponse
}
