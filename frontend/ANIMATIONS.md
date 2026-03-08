# 🎬 Анимации - Документация

## Обзор

В проекте реализована система анимаций для:
- Переходов между страницами
- Интерактивных элементов (кнопки, карточки)
- Состояний (загрузка, воспроизведение, ошибки)
- Списков и элементов интерфейса

## Компоненты

### PageTransition

Обёртка для страниц с анимацией появления:

```jsx
import PageTransition from '../components/PageTransition';

return (
  <PageTransition>
    <div>Контент страницы</div>
  </PageTransition>
);
```

**Параметры:**
- `delay` (опционально) - задержка анимации в мс (по умолчанию 300)

## CSS Классы

### Основные анимации

| Класс | Описание |
|-------|----------|
| `.fade-in` | Плавное появление |
| `.slide-up` | Выезд снизу вверх |
| `.slide-down` | Выезд сверху вниз |
| `.scale-in` | Появление с увеличением |
| `.pulse` | Пульсация |

### Анимации переходов

| Класс | Описание |
|-------|----------|
| `.page-enter` | Начало появления страницы |
| `.page-enter-active` | Активная фаза появления |
| `.page-exit` | Начало исчезновения |
| `.page-exit-active` | Активная фаза исчезновения |

### Анимации для списков

| Класс | Описание |
|-------|----------|
| `.stagger-item` | Поэлементное появление с задержкой |
| `.stagger-item:nth-child(n)` | Задержка для n-го элемента |

### Интерактивные анимации

| Класс | Описание |
|-------|----------|
| `.card-hover` | Подъём карточки при наведении |
| `.button-press` | Эффект нажатия кнопки |
| `.ripple-container` | Контейнер для ripple-эффекта |

### Состояния

| Класс | Описание |
|-------|----------|
| `.skeleton` | Анимация загрузки (shimmer) |
| `.progress-animate` | Плавное изменение прогресс-бара |
| `.equalizer` | Анимация эквалайзера |
| `.shake` | Тряска для ошибок |
| `.bounce` | Прыжок для уведомлений |

## Хуки

### usePageTransition

```jsx
import { usePageTransition } from '../hooks/usePageTransition';

function MyComponent() {
  const isAnimating = usePageTransition(300);
  
  return (
    <div className={isAnimating ? 'animating' : 'visible'}>
      Контент
    </div>
  );
}
```

### useFadeIn

```jsx
import { useFadeIn } from '../hooks/useFadeIn';

function MyComponent() {
  const isVisible = useFadeIn(100);
  
  return (
    <div className={isVisible ? 'visible' : 'hidden'}>
      Контент
    </div>
  );
}
```

## Примеры использования

### Анимация карточки трека

```css
.trackCard {
  composes: card-hover from global;
  transition: transform 200ms ease, box-shadow 200ms ease;
}
```

### Анимация списка треков

```jsx
{tracks.map((track, index) => (
  <div 
    key={track.id} 
    className="stagger-item"
    style={{ animationDelay: `${index * 50}ms` }}
  >
    <TrackCard track={track} />
  </div>
))}
```

### Ripple эффект на кнопке

```jsx
function Button({ children, onClick }) {
  const [ripples, setRipples] = useState([]);

  const handleClick = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const newRipple = { x, y, id: Date.now() };
    setRipples([...ripples, newRipple]);
    
    onClick?.(e);
  };

  return (
    <button className="ripple-container" onClick={handleClick}>
      {ripples.map(ripple => (
        <span 
          key={ripple.id} 
          className="ripple"
          style={{ left: ripple.x, top: ripple.y }}
        />
      ))}
      {children}
    </button>
  );
}
```

## Настройка длительности

В `index.css` можно изменить глобальные переменные:

```css
:root {
  --transition-fast: 0.15s ease;
  --transition-normal: 0.3s ease;
}
```

## Отключение анимаций

Для пользователей с предпочтением reduced-motion:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

## Производительность

Рекомендации:
- Используйте `transform` и `opacity` для анимаций (аппаратное ускорение)
- Избегайте анимации `width`, `height`, `top`, `left`
- Для списков используйте `stagger` с задержкой
- Отключайте анимации в режиме энергосбережения
