import React, { useState, useEffect, useRef } from 'react';
import './Equalizer.css';

const Equalizer = ({ audioElement }) => {
  const [isEnabled, setIsEnabled] = useState(false);
  const [preset, setPreset] = useState('flat');
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const sourceRef = useRef(null);
  const filtersRef = useRef([]);
  const canvasRef = useRef(null);
  const animationRef = useRef(null);

  const presets = {
    flat: [0, 0, 0, 0, 0, 0, 0, 0, 0],
    bass: [6, 5, 4, 2, 0, 0, 0, 1, 2],
    treble: [0, 0, 0, 1, 2, 3, 4, 5, 6],
    vocal: [-2, -1, 0, 2, 4, 4, 2, 0, -1],
    jazz: [3, 2, 1, 2, 3, 3, 2, 3, 4],
    rock: [4, 3, 2, 1, -1, -1, 2, 3, 4],
    electronic: [5, 4, 3, 2, 0, 1, 2, 3, 4],
    classical: [4, 3, 2, 1, 2, 3, 3, 4, 5],
    pop: [2, 3, 4, 3, 1, 0, 1, 2, 3],
    hiphop: [5, 4, 3, 1, 0, 0, 2, 3, 4],
  };

  const frequencies = [60, 170, 310, 600, 1000, 3000, 6000, 12000, 14000];

  useEffect(() => {
    if (!audioElement || !isEnabled) return;

    // Инициализация Audio Context
    if (!audioContextRef.current) {
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
      analyserRef.current = audioContextRef.current.createAnalyser();
      analyserRef.current.fftSize = 256;

      // Создаём фильтры для каждой полосы
      filtersRef.current = frequencies.map((freq, index) => {
        const filter = audioContextRef.current.createBiquadFilter();
        filter.type = index === 0 ? 'lowshelf' : index === frequencies.length - 1 ? 'highshelf' : 'peaking';
        filter.frequency.value = freq;
        filter.Q.value = 1;
        filter.gain.value = presets[preset][index];
        return filter;
      });

      // Подключаем источник
      sourceRef.current = audioContextRef.current.createMediaElementSource(audioElement);
      
      // Цепочка подключения: source -> filters -> analyser -> destination
      let lastNode = sourceRef.current;
      filtersRef.current.forEach(filter => {
        lastNode.connect(filter);
        lastNode = filter;
      });
      lastNode.connect(analyserRef.current);
      analyserRef.current.connect(audioContextRef.current.destination);
    }

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [audioElement, isEnabled]);

  useEffect(() => {
    if (!filtersRef.current.length) return;

    filtersRef.current.forEach((filter, index) => {
      filter.gain.value = presets[preset][index];
    });
  }, [preset]);

  const toggleEqualizer = () => {
    if (audioContextRef.current) {
      if (isEnabled) {
        audioContextRef.current.suspend();
      } else {
        audioContextRef.current.resume();
      }
      setIsEnabled(!isEnabled);
    }
  };

  const drawVisualizer = () => {
    if (!analyserRef.current || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const analyser = analyserRef.current;
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const draw = () => {
      animationRef.current = requestAnimationFrame(draw);
      analyser.getByteFrequencyData(dataArray);

      ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      const barWidth = (canvas.width / bufferLength) * 2.5;
      let x = 0;

      for (let i = 0; i < bufferLength; i++) {
        const barHeight = (dataArray[i] / 255) * canvas.height;
        
        const gradient = ctx.createLinearGradient(0, canvas.height - barHeight, 0, canvas.height);
        gradient.addColorStop(0, '#1ed760');
        gradient.addColorStop(1, '#0d73ec');
        
        ctx.fillStyle = gradient;
        ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
        
        x += barWidth + 1;
      }
    };

    draw();
  };

  useEffect(() => {
    if (isEnabled) {
      drawVisualizer();
    }
  }, [isEnabled]);

  return (
    <div className="equalizer">
      <div className="equalizer-header">
        <h3>Эквалайзер</h3>
        <button className={`toggle-btn ${isEnabled ? 'active' : ''}`} onClick={toggleEqualizer}>
          {isEnabled ? 'ВКЛ' : 'ВЫКЛ'}
        </button>
      </div>

      {isEnabled && (
        <>
          <canvas ref={canvasRef} width="300" height="80" className="visualizer" />
          
          <div className="presets">
            <span className="preset-label">Пресеты:</span>
            <div className="preset-buttons">
              {Object.keys(presets).map(p => (
                <button
                  key={p}
                  className={`preset-btn ${preset === p ? 'active' : ''}`}
                  onClick={() => setPreset(p)}
                >
                  {p.charAt(0).toUpperCase() + p.slice(1)}
                </button>
              ))}
            </div>
          </div>

          <div className="frequency-bands">
            {frequencies.map((freq, index) => (
              <div key={freq} className="frequency-band">
                <span className="frequency-label">{freq >= 1000 ? `${freq/1000}k` : freq}</span>
                <input
                  type="range"
                  min="-12"
                  max="12"
                  value={presets[preset][index]}
                  onChange={(e) => {
                    const newPreset = [...presets[preset]];
                    newPreset[index] = parseInt(e.target.value);
                    setPreset({ ...presets, [preset]: newPreset }[preset]);
                  }}
                  className="band-slider"
                  style={{ '--value': presets[preset][index] }}
                />
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
};

export default Equalizer;
