'use client';

import { RoomAudioRenderer, StartAudio } from '@livekit/components-react';
import type { AppConfig } from '@/app-config';
import { SessionProvider } from '@/components/app/session-provider';
import { ViewController } from '@/components/app/view-controller';
import { Toaster } from '@/components/livekit/toaster';

interface AppProps {
  appConfig: AppConfig;
}

export function App({ appConfig }: AppProps) {
  return (
    <SessionProvider appConfig={appConfig}>
      {/* Cute iOS-style Navbar */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-black/5 backdrop-blur-sm border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* VYAAS AI Logo */}
            <div className="flex items-center space-x-3 animate-pop-in">
              <div className="w-10 h-10 bg-gradient-to-br from-pink-400 to-purple-500 rounded-2xl flex items-center justify-center effect-soft-glow animate-bounce-gentle">
                <span className="text-white font-bold text-lg text-bbh">V</span>
              </div>
              <h1 className="text-2xl font-bold text-white text-bbh">
                <span className="text-glass-bg">VYAAS AI</span>
              </h1>
            </div>
            
            {/* Login Button */}
            <button className="px-6 py-2 effect-glass-ios text-white font-semibold rounded-2xl effect-cute-hover transition-all duration-300 animate-pop-in text-bbh">
              <span className="text-glass-bg">Login</span>
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content with Lovable Background */}
      <main className="min-h-screen bg-gradient-to-b from-indigo-900 via-purple-900 to-pink-900 pt-16">
        {/* Animated Background Elements */}
        <div className="fixed inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-pink-500/10 rounded-full blur-3xl animate-float"></div>
          <div className="absolute top-3/4 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-float" style={{animationDelay: '1s'}}></div>
          <div className="absolute bottom-1/4 left-1/3 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl animate-float" style={{animationDelay: '2s'}}></div>
        </div>
        
        <div className="relative z-10">
          <ViewController />
        </div>
      </main>
      
      <StartAudio label="Start Audio" />
      <RoomAudioRenderer />
      <Toaster />
    </SessionProvider>
  );
}
