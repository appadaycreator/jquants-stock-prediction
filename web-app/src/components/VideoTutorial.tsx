"use client";

import React, { useState, useRef, useEffect } from "react";
import { 
  Play, 
  Pause, 
  Volume2, 
  VolumeX, 
  Maximize, 
  Minimize,
  RotateCcw,
  Settings,
  Download,
  Share2,
  X,
} from "lucide-react";

interface VideoTutorialProps {
  src: string;
  title: string;
  description?: string;
  duration?: number;
  thumbnail?: string;
  onClose?: () => void;
  className?: string;
}

const VideoTutorial: React.FC<VideoTutorialProps> = ({
  src,
  title,
  description,
  duration,
  thumbnail,
  onClose,
  className = "",
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [volume, setVolume] = useState(1);
  const [showControls, setShowControls] = useState(true);
  const [playbackRate, setPlaybackRate] = useState(1);
  const [showSettings, setShowSettings] = useState(false);

  const videoRef = useRef<HTMLVideoElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const progressRef = useRef<HTMLDivElement>(null);

  const playbackRates = [0.5, 0.75, 1, 1.25, 1.5, 2];

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const handleTimeUpdate = () => setCurrentTime(video.currentTime);
    const handleLoadedMetadata = () => {
      // 動画のメタデータが読み込まれた時の処理
      // durationは読み取り専用プロパティのため、直接設定はできません
    };

    video.addEventListener("timeupdate", handleTimeUpdate);
    video.addEventListener("loadedmetadata", handleLoadedMetadata);

    return () => {
      video.removeEventListener("timeupdate", handleTimeUpdate);
      video.removeEventListener("loadedmetadata", handleLoadedMetadata);
    };
  }, [duration]);

  const togglePlay = () => {
    const video = videoRef.current;
    if (!video) return;

    if (isPlaying) {
      video.pause();
    } else {
      video.play();
    }
    setIsPlaying(!isPlaying);
  };

  const toggleMute = () => {
    const video = videoRef.current;
    if (!video) return;

    video.muted = !isMuted;
    setIsMuted(!isMuted);
  };

  const handleVolumeChange = (newVolume: number) => {
    const video = videoRef.current;
    if (!video) return;

    video.volume = newVolume;
    setVolume(newVolume);
    setIsMuted(newVolume === 0);
  };

  const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const video = videoRef.current;
    const progress = progressRef.current;
    if (!video || !progress) return;

    const rect = progress.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const newTime = (clickX / rect.width) * video.duration;
    video.currentTime = newTime;
    setCurrentTime(newTime);
  };

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      containerRef.current?.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  const handlePlaybackRateChange = (rate: number) => {
    const video = videoRef.current;
    if (!video) return;

    video.playbackRate = rate;
    setPlaybackRate(rate);
  };

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, "0")}`;
  };

  const progress = duration ? (currentTime / duration) * 100 : 0;

  return (
    <div
      ref={containerRef}
      className={`relative bg-themed-background rounded-lg overflow-hidden ${className}`}
      onMouseEnter={() => setShowControls(true)}
      onMouseLeave={() => setShowControls(false)}
    >
      {/* ビデオ要素 */}
      <video
        ref={videoRef}
        src={src}
        poster={thumbnail}
        className="w-full h-full object-cover"
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
        onEnded={() => setIsPlaying(false)}
      />

      {/* オーバーレイ */}
      <div className="absolute inset-0 bg-black bg-opacity-20" />

      {/* コントロール */}
      {showControls && (
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black to-transparent p-4">
          {/* プログレスバー */}
          <div
            ref={progressRef}
            className="w-full h-1 bg-themed-background-secondary rounded-full cursor-pointer mb-4"
            onClick={handleProgressClick}
          >
            <div
              className="h-full bg-themed-primary rounded-full transition-all duration-200"
              style={{ width: `${progress}%` }}
            />
          </div>

          {/* コントロールボタン */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={togglePlay}
                className="text-themed-text-inverse hover:text-themed-primary transition-colors"
              >
                {isPlaying ? <Pause className="h-6 w-6" /> : <Play className="h-6 w-6" />}
              </button>

              <button
                onClick={toggleMute}
                className="text-themed-text-inverse hover:text-themed-primary transition-colors"
              >
                {isMuted ? <VolumeX className="h-5 w-5" /> : <Volume2 className="h-5 w-5" />}
              </button>

              <div className="flex items-center space-x-2">
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={volume}
                  onChange={(e) => handleVolumeChange(parseFloat(e.target.value))}
                  className="w-20 h-1 bg-themed-background-secondary rounded-full appearance-none cursor-pointer"
                />
                <span className="text-themed-text-inverse text-sm">
                  {Math.round(volume * 100)}%
                </span>
              </div>

              <span className="text-themed-text-inverse text-sm">
                {formatTime(currentTime)} / {duration ? formatTime(duration) : "--:--"}
              </span>
            </div>

            <div className="flex items-center space-x-2">
              <div className="relative">
                <button
                  onClick={() => setShowSettings(!showSettings)}
                  className="text-themed-text-inverse hover:text-themed-primary transition-colors"
                >
                  <Settings className="h-5 w-5" />
                </button>

                {showSettings && (
                  <div className="absolute bottom-8 right-0 bg-themed-surface border border-themed-border rounded-lg shadow-lg p-2 min-w-32">
                    <div className="text-themed-text-primary text-sm font-medium mb-2">再生速度</div>
                    <div className="space-y-1">
                      {playbackRates.map((rate) => (
                        <button
                          key={rate}
                          onClick={() => handlePlaybackRateChange(rate)}
                          className={`w-full text-left px-2 py-1 text-sm rounded hover:bg-themed-background-secondary ${
                            playbackRate === rate ? "bg-themed-primary-light text-themed-primary" : "text-themed-text-secondary"
                          }`}
                        >
                          {rate}x
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <button
                onClick={toggleFullscreen}
                className="text-themed-text-inverse hover:text-themed-primary transition-colors"
              >
                {isFullscreen ? <Minimize className="h-5 w-5" /> : <Maximize className="h-5 w-5" />}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* タイトルと説明 */}
      <div className="absolute top-4 left-4 right-4">
        <h3 className="text-themed-text-inverse font-semibold text-lg mb-1">{title}</h3>
        {description && (
          <p className="text-themed-text-inverse text-sm opacity-90">{description}</p>
        )}
      </div>

      {/* 閉じるボタン */}
      {onClose && (
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-themed-text-inverse hover:text-themed-primary transition-colors"
        >
          <X className="h-6 w-6" />
        </button>
      )}
    </div>
  );
};

export default VideoTutorial;
