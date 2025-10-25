import * as React from 'react';
import { cn } from '@/lib/utils';

export interface ChatEntryProps extends React.HTMLAttributes<HTMLLIElement> {
  /** The locale to use for the timestamp. */
  locale: string;
  /** The timestamp of the message. */
  timestamp: number;
  /** The message to display. */
  message: string;
  /** The origin of the message. */
  messageOrigin: 'local' | 'remote';
  /** The sender's name. */
  name?: string;
  /** Whether the message has been edited. */
  hasBeenEdited?: boolean;
}

export const ChatEntry = ({
  name,
  locale,
  timestamp,
  message,
  messageOrigin,
  hasBeenEdited = false,
  className,
  ...props
}: ChatEntryProps) => {
  const time = new Date(timestamp);
  const title = time.toLocaleTimeString(locale, { timeStyle: 'full' });

  return (
    <li
      title={title}
      data-lk-message-origin={messageOrigin}
      className={cn('group flex w-full flex-col gap-3 animate-slide-up', className)}
      {...props}
    >
      <div className={cn(
        'flex w-full',
        messageOrigin === 'local' ? 'justify-end' : 'justify-start'
      )}>
        <div className={cn(
          'max-w-3xl relative',
          messageOrigin === 'local' ? 'ml-12' : 'mr-12'
        )}>
          {/* Message Card */}
          <div className={cn(
            'effect-3d rounded-2xl p-4 transition-all duration-300 hover:effect-neon-glow',
            messageOrigin === 'local' 
              ? 'bg-gradient-to-br from-cyan-500/20 to-blue-600/20 border border-cyan-500/30 text-white' 
              : 'effect-glass text-white'
          )}>
            {/* Message Header */}
            <header className={cn(
              'flex items-center gap-2 text-sm mb-2',
              messageOrigin === 'local' ? 'flex-row-reverse' : 'text-left'
            )}>
              {name && (
                <strong className={cn(
                  'font-semibold',
                  messageOrigin === 'local' ? 'text-cyan-300' : 'text-blue-300'
                )}>
                  {name}
                </strong>
              )}
              <span className="font-mono text-xs opacity-60 transition-opacity ease-linear group-hover:opacity-100">
                {hasBeenEdited && '*'}
                {time.toLocaleTimeString(locale, { timeStyle: 'short' })}
              </span>
            </header>
            
            {/* Message Content */}
            <div className="text-sm leading-relaxed">
              {message}
            </div>
            
            {/* Message Status Indicator */}
            {messageOrigin === 'local' && (
              <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-cyan-400 rounded-full animate-pulse"></div>
            )}
          </div>
          
          {/* Avatar */}
          <div className={cn(
            'absolute top-2 w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold',
            messageOrigin === 'local' 
              ? 'right-0 bg-gradient-to-br from-cyan-400 to-blue-600 text-white' 
              : 'left-0 bg-gradient-to-br from-slate-700 to-slate-800 text-cyan-400 border border-cyan-500/30'
          )}>
            {messageOrigin === 'local' ? 'U' : 'AI'}
          </div>
        </div>
      </div>
    </li>
  );
};
