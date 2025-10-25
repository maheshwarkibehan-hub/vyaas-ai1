'use client';

import React, { useState } from 'react';
import { motion } from 'motion/react';
import type { AppConfig } from '@/app-config';
import { ChatTranscript } from '@/components/app/chat-transcript';
import { PreConnectMessage } from '@/components/app/preconnect-message';
import { TileLayout } from '@/components/app/tile-layout';
import {
  AgentControlBar,
  type ControlBarControls,
} from '@/components/livekit/agent-control-bar/agent-control-bar';
import { useChatMessages } from '@/hooks/useChatMessages';
import { useConnectionTimeout } from '@/hooks/useConnectionTimout';
import { useDebugMode } from '@/hooks/useDebug';
import { cn } from '@/lib/utils';
import { ScrollArea } from '../livekit/scroll-area/scroll-area';

const MotionBottom = motion.create('div');

const IN_DEVELOPMENT = process.env.NODE_ENV !== 'production';
const BOTTOM_VIEW_MOTION_PROPS = {
  variants: {
    visible: {
      opacity: 1,
      translateY: '0%',
    },
    hidden: {
      opacity: 0,
      translateY: '100%',
    },
  },
  initial: 'hidden',
  animate: 'visible',
  exit: 'hidden',
  transition: {
    duration: 0.3,
    delay: 0.5,
    ease: 'easeOut',
  },
};

interface FadeProps {
  top?: boolean;
  bottom?: boolean;
  className?: string;
}

export function Fade({ top = false, bottom = false, className }: FadeProps) {
  return (
    <div
      className={cn(
        'from-background pointer-events-none h-4 bg-linear-to-b to-transparent',
        top && 'bg-linear-to-b',
        bottom && 'bg-linear-to-t',
        className
      )}
    />
  );
}
interface SessionViewProps {
  appConfig: AppConfig;
}

export const SessionView = ({
  appConfig,
  ...props
}: React.ComponentProps<'section'> & SessionViewProps) => {
  useConnectionTimeout(200_000);
  useDebugMode({ enabled: IN_DEVELOPMENT });

  const messages = useChatMessages();
  const [chatOpen, setChatOpen] = useState(false);

  const controls: ControlBarControls = {
    leave: true,
    microphone: true,
    chat: appConfig.supportsChatInput,
    camera: appConfig.supportsVideoInput,
    screenShare: appConfig.supportsVideoInput,
  };

  return (
    <section className="relative z-10 h-full w-full overflow-hidden" {...props}>
      {/* Minimal Chat Interface */}
      <div className="h-full flex flex-col">
        {/* Main Chat Area - Full Width */}
        <div className="flex-1 flex flex-col">
          {/* Chat Messages */}
          <div className="flex-1 overflow-hidden">
            <div
              className={cn(
                'h-full grid grid-cols-1 grid-rows-1',
                !chatOpen && 'pointer-events-none'
              )}
            >
              <ScrollArea className="px-4 pt-16 pb-[200px] md:px-6 md:pb-[250px]">
                <ChatTranscript
                  hidden={!chatOpen}
                  messages={messages}
                  className="mx-auto max-w-4xl space-y-4 transition-opacity duration-300 ease-out"
                />
              </ScrollArea>
            </div>
          </div>

          {/* Enhanced Control Bar - Fixed Position */}
          <div className="fixed bottom-0 left-0 right-0 z-50 p-4 border-t border-white/10 bg-black/10 backdrop-blur-md">
            {appConfig.isPreConnectBufferEnabled && (
              <PreConnectMessage messages={messages} className="pb-4" />
            )}
            <div className="mx-auto max-w-4xl">
              <Fade bottom className="absolute inset-x-0 top-0 h-4 -translate-y-full" />
              <AgentControlBar controls={controls} onChatOpenChange={setChatOpen} />
            </div>
          </div>
        </div>
      </div>

      {/* Tile Layout (for video calls) */}
      <TileLayout chatOpen={chatOpen} />
    </section>
  );
};
