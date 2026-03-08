import React, { useState, useContext } from 'react';
import { musicAPI } from '../api/musicApi';
import { PlayerContext } from '../contexts/PlayerContext';
import styles from './AIStudio.module.css';

const AI_PROVIDERS = [
  { id: 'suno', name: 'Suno AI', description: 'Генерация полноценных песен', icon: '🎵' },
  { id: 'mubert', name: 'Mubert', description: 'Фоновая музыка', icon: '🎧' },
  { id: 'musicgen', name: 'MusicGen', description: 'Короткие аудио-клипы', icon: '🎼' },
];

const MOODS = [
  { id: 'happy', name: 'Счастливое', emoji: '😊' },
  { id: 'sad', name: 'Грустное', emoji: '😢' },
  { id: 'energetic', name: 'Энергичное', emoji: '⚡' },
  { id: 'chill', name: 'Спокойное', emoji: '😌' },
  { id: 'focus', name: 'Для работы', emoji: '🎯' },
];

const GENRES = [
  'pop', 'rock', 'electronic', 'hip-hop', 'jazz', 
  'classical', 'ambient', 'metal', 'indie', 'r&b'
];

export default function AIStudio() {
  const { playTrack } = useContext(PlayerContext);
  
  // Состояние
  const [selectedProvider, setSelectedProvider] = useState('suno');
  const [prompt, setPrompt] = useState('');
  const [tags, setTags] = useState('');
  const [title, setTitle] = useState('');
  const [selectedMood, setSelectedMood] = useState(null);
  const [selectedGenre, setSelectedGenre] = useState(null);
  const [duration, setDuration] = useState(60);
  
  // Генерация
  const [isGenerating, setIsGenerating] = useState(false);
  const [taskId, setTaskId] = useState(null);
  const [generationStatus, setGenerationStatus] = useState(null);
  const [generatedTracks, setGeneratedTracks] = useState([]);
  
  // Разделение на стемы
  const [stemAudioUrl, setStemAudioUrl] = useState('');
  const [selectedStem, setSelectedStem] = useState('vocals');
  const [isSeparating, setIsSeparating] = useState(false);
  
  // Синтез голоса
  const [voiceText, setVoiceText] = useState('');
  const [selectedVoice, setSelectedVoice] = useState('21m00Tcm4TlvDq8ikWAM');
  const [isGeneratingVoice, setIsGeneratingVoice] = useState(false);

  // Генерация музыки
  const handleGenerate = async () => {
    if (!prompt.trim()) {
      alert('Введите описание музыки');
      return;
    }

    setIsGenerating(true);
    setGenerationStatus('preparing');

    try {
      const options = {
        tags: tags || (selectedGenre ? selectedGenre : undefined),
        title: title || undefined,
        duration: selectedProvider === 'mubert' ? duration : undefined,
        mood: selectedProvider === 'mubert' ? selectedMood : undefined,
        genre: selectedProvider === 'mubert' ? selectedGenre : undefined,
      };

      const result = await musicAPI.generateMusic(selectedProvider, prompt, options);
      setTaskId(result.task_id);
      setGenerationStatus('pending');

      // Ожидание завершения
      pollGenerationStatus(result.task_id);
    } catch (error) {
      console.error('Generation error:', error);
      setGenerationStatus('failed');
      setIsGenerating(false);
    }
  };

  // Опрос статуса
  const pollGenerationStatus = async (id) => {
    const interval = setInterval(async () => {
      try {
        const status = await musicAPI.getGenerationStatus(id, selectedProvider);
        setGenerationStatus(status.status);

        if (status.status === 'completed') {
          clearInterval(interval);
          setIsGenerating(false);
          
          // Добавление трека в список
          if (status.audio_url || status.audio_base64) {
            const newTrack = {
              id: `ai-${Date.now()}`,
              title: status.title || 'AI Generated Track',
              artist: 'AI',
              source: 'ai',
              stream_url: status.audio_url || `data:audio/mp3;base64,${status.audio_base64}`,
              duration: status.duration || 180,
              cover: 'https://picsum.photos/seed/ai/300/300',
            };
            setGeneratedTracks(prev => [newTrack, ...prev]);
          }
        } else if (status.status === 'failed') {
          clearInterval(interval);
          setIsGenerating(false);
        }
      } catch (error) {
        console.error('Status poll error:', error);
      }
    }, 3000);
  };

  // Разделение на стемы
  const handleSeparateStems = async () => {
    if (!stemAudioUrl.trim()) {
      alert('Введите URL аудио');
      return;
    }

    setIsSeparating(true);
    try {
      const result = await musicAPI.separateStems(stemAudioUrl, selectedStem);
      alert(`Задача на разделение создана: ${result.task_id}`);
    } catch (error) {
      console.error('Stem separation error:', error);
      alert('Ошибка разделения: ' + error.message);
    } finally {
      setIsSeparating(false);
    }
  };

  // Синтез голоса
  const handleGenerateVoice = async () => {
    if (!voiceText.trim()) {
      alert('Введите текст');
      return;
    }

    setIsGeneratingVoice(true);
    try {
      const result = await musicAPI.generateVoice(voiceText, selectedVoice);
      
      if (result.audio_base64) {
        const track = {
          id: `voice-${Date.now()}`,
          title: 'Voice Synthesis',
          artist: 'ElevenLabs',
          source: 'ai',
          stream_url: `data:audio/mp3;base64,${result.audio_base64}`,
          duration: 30,
          cover: 'https://picsum.photos/seed/voice/300/300',
        };
        playTrack(track);
      }
    } catch (error) {
      console.error('Voice generation error:', error);
      alert('Ошибка: ' + error.message);
    } finally {
      setIsGeneratingVoice(false);
    }
  };

  return (
    <div className={styles.aiStudio}>
      <header className={styles.header}>
        <h1>🤖 AI Студия</h1>
        <p>Генерация музыки и обработка аудио с помощью искусственного интеллекта</p>
      </header>

      <div className={styles.tabs}>
        <button 
          className={styles.tab}
          onClick={() => document.getElementById('generate').scrollIntoView({ behavior: 'smooth' })}
        >
          🎵 Генерация
        </button>
        <button 
          className={styles.tab}
          onClick={() => document.getElementById('stems').scrollIntoView({ behavior: 'smooth' })}
        >
          🎚️ Разделение
        </button>
        <button 
          className={styles.tab}
          onClick={() => document.getElementById('voice').scrollIntoView({ behavior: 'smooth' })}
        >
          🎤 Голос
        </button>
      </div>

      {/* Генерация музыки */}
      <section id="generate" className={styles.section}>
        <h2>Генерация музыки</h2>
        
        {/* Выбор провайдера */}
        <div className={styles.providers}>
          {AI_PROVIDERS.map(provider => (
            <div
              key={provider.id}
              className={`${styles.provider} ${selectedProvider === provider.id ? styles.selected : ''}`}
              onClick={() => setSelectedProvider(provider.id)}
            >
              <span className={styles.providerIcon}>{provider.icon}</span>
              <span className={styles.providerName}>{provider.name}</span>
              <span className={styles.providerDesc}>{provider.description}</span>
            </div>
          ))}
        </div>

        {/* Ввод промпта */}
        <div className={styles.inputGroup}>
          <label>Описание музыки</label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Например: весёлая поп-песня о лете с гитарой и барабанами"
            rows={4}
          />
        </div>

        {/* Дополнительные параметры */}
        <div className={styles.row}>
          <div className={styles.inputGroup}>
            <label>Название (опционально)</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="My AI Song"
            />
          </div>
          <div className={styles.inputGroup}>
            <label>Теги/Жанр</label>
            <input
              type="text"
              value={tags}
              onChange={(e) => setTags(e.target.value)}
              placeholder="pop, summer, guitar"
            />
          </div>
        </div>

        {/* Настроение и жанр для Mubert */}
        {selectedProvider === 'mubert' && (
          <>
            <div className={styles.inputGroup}>
              <label>Настроение</label>
              <div className={styles.moods}>
                {MOODS.map(mood => (
                  <button
                    key={mood.id}
                    className={`${styles.mood} ${selectedMood === mood.id ? styles.selected : ''}`}
                    onClick={() => setSelectedMood(mood.id)}
                  >
                    {mood.emoji} {mood.name}
                  </button>
                ))}
              </div>
            </div>

            <div className={styles.inputGroup}>
              <label>Жанр</label>
              <div className={styles.genres}>
                {GENRES.map(genre => (
                  <button
                    key={genre}
                    className={`${styles.genre} ${selectedGenre === genre ? styles.selected : ''}`}
                    onClick={() => setSelectedGenre(genre)}
                  >
                    {genre}
                  </button>
                ))}
              </div>
            </div>

            <div className={styles.inputGroup}>
              <label>Длительность: {duration} сек</label>
              <input
                type="range"
                min="30"
                max="300"
                value={duration}
                onChange={(e) => setDuration(Number(e.target.value))}
              />
            </div>
          </>
        )}

        <button 
          className={styles.generateButton}
          onClick={handleGenerate}
          disabled={isGenerating || !prompt.trim()}
        >
          {isGenerating ? '⏳ Генерация...' : '🚀 Сгенерировать'}
        </button>

        {/* Статус генерации */}
        {generationStatus && (
          <div className={styles.status}>
            Статус: <strong>{generationStatus}</strong>
          </div>
        )}

        {/* Сгенерированные треки */}
        {generatedTracks.length > 0 && (
          <div className={styles.generatedTracks}>
            <h3>Сгенерированные треки</h3>
            {generatedTracks.map((track, index) => (
              <div key={index} className={styles.trackCard}>
                <img src={track.cover} alt={track.title} className={styles.trackCover} />
                <div className={styles.trackInfo}>
                  <div className={styles.trackTitle}>{track.title}</div>
                  <div className={styles.trackArtist}>{track.artist}</div>
                </div>
                <button 
                  className={styles.playButton}
                  onClick={() => playTrack(track)}
                >
                  ▶️
                </button>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Разделение на стемы */}
      <section id="stems" className={styles.section}>
        <h2>🎚️ Разделение на стемы</h2>
        <p>Выделите вокал, бас, ударные или другие инструменты из трека</p>

        <div className={styles.inputGroup}>
          <label>URL аудио файла</label>
          <input
            type="text"
            value={stemAudioUrl}
            onChange={(e) => setStemAudioUrl(e.target.value)}
            placeholder="https://example.com/track.mp3"
          />
        </div>

        <div className={styles.stemTypes}>
          {['vocals', 'instrumental', 'drums', 'bass', 'guitar', 'piano'].map(stem => (
            <button
              key={stem}
              className={`${styles.stemButton} ${selectedStem === stem ? styles.selected : ''}`}
              onClick={() => setSelectedStem(stem)}
            >
              {stem === 'vocals' && '🎤 '}
              {stem === 'instrumental' && '🎹 '}
              {stem === 'drums' && '🥁 '}
              {stem}
            </button>
          ))}
        </div>

        <button 
          className={styles.separateButton}
          onClick={handleSeparateStems}
          disabled={isSeparating || !stemAudioUrl.trim()}
        >
          {isSeparating ? '⏳ Разделение...' : '✂️ Разделить'}
        </button>
      </section>

      {/* Синтез голоса */}
      <section id="voice" className={styles.section}>
        <h2>🎤 Синтез голоса</h2>
        <p>Преобразуйте текст в речь с помощью ElevenLabs</p>

        <div className={styles.inputGroup}>
          <label>Текст</label>
          <textarea
            value={voiceText}
            onChange={(e) => setVoiceText(e.target.value)}
            placeholder="Введите текст для озвучки..."
            rows={4}
          />
        </div>

        <button 
          className={styles.voiceButton}
          onClick={handleGenerateVoice}
          disabled={isGeneratingVoice || !voiceText.trim()}
        >
          {isGeneratingVoice ? '⏳ Генерация...' : '🔊 Озвучить'}
        </button>
      </section>
    </div>
  );
}
