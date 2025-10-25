import { Button } from '@/components/livekit/button';

function WelcomeImage() {
  return (
    <div className="relative mb-8">
      {/* Cute Cloud-like graphic */}
      <div className="w-24 h-16 mx-auto mb-6 relative animate-bounce-gentle">
        <div className="absolute inset-0 bg-gradient-to-r from-pink-500/20 to-purple-500/20 rounded-full blur-sm"></div>
        <div className="absolute inset-2 bg-gradient-to-r from-pink-400/30 to-purple-400/30 rounded-full blur-sm"></div>
        <div className="absolute inset-4 bg-gradient-to-r from-pink-300/40 to-purple-300/40 rounded-full blur-sm"></div>
      </div>
      
      {/* Announcement Button */}
      <div className="flex justify-center mb-8">
        <button className="px-4 py-2 effect-glass-ios border border-white/20 rounded-2xl text-white text-sm hover:effect-glass-ios-strong transition-all duration-300 flex items-center space-x-2 animate-pop-in effect-cute-hover">
          <span className="text-bbh text-glass-bg">Introducing VYAAS AI Cloud</span>
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7"/>
          </svg>
        </button>
      </div>
    </div>
  );
}

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
}

export const WelcomeView = ({
  startButtonText,
  onStartCall,
  ref,
}: React.ComponentProps<'div'> & WelcomeViewProps) => {
  return (
    <div ref={ref} className="min-h-screen flex items-center justify-center px-4">
      <section className="max-w-4xl mx-auto text-center animate-fade-in">
        <WelcomeImage />

        {/* Main Heading - Centered Vyaas AI */}
        <div className="mb-12">
          <h1 className="text-8xl md:text-9xl font-bold text-white mb-8 text-bbh animate-pop-in">
            <span className="bg-gradient-to-r from-pink-400 via-purple-400 to-blue-400 bg-clip-text text-transparent">
              Vyaas AI
            </span>
          </h1>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-6 justify-center items-center">
          <Button 
            variant="primary" 
            size="lg" 
            onClick={onStartCall} 
            className="px-12 py-4 text-xl font-semibold bg-gradient-to-r from-pink-500 to-purple-600 hover:from-pink-400 hover:to-purple-500 text-white rounded-2xl effect-cute-hover transition-all duration-300 hover:scale-105 hover:shadow-2xl hover:shadow-pink-500/25 min-w-[200px] animate-pop-in text-bbh"
          >
            {startButtonText}
          </Button>
          
          <button className="px-12 py-4 text-xl font-semibold effect-glass-ios-strong text-white rounded-2xl effect-cute-hover transition-all duration-300 hover:scale-105 hover:shadow-lg hover:shadow-pink-500/25 min-w-[200px] animate-pop-in text-bbh">
            Learn More
          </button>
        </div>
      </section>
    </div>
  );
};
