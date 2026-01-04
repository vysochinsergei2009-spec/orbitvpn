
import React from 'react';
import { Shield, Zap, Globe, Lock, Cpu, Star } from 'lucide-react';
import GlassCard from '../components/GlassCard';
import { Feature, PricingPlan } from '../types';

const Home: React.FC = () => {
  const features: Feature[] = [
    {
      title: "Quantum Encryption",
      description: "State-of-the-art AES-256-GCM encryption keeping your data invisible to trackers and hackers.",
      icon: <Lock className="w-6 h-6 text-yellow-400" />
    },
    {
      title: "Global Orbit",
      description: "Over 6,500 servers across 90+ countries. Access the internet without digital borders.",
      icon: <Globe className="w-6 h-6 text-yellow-400" />
    },
    {
      title: "Hyper-Speed",
      description: "Proprietary OrbitX protocol ensuring zero latency drops even during peak planetary traffic.",
      icon: <Zap className="w-6 h-6 text-yellow-400" />
    },
    {
      title: "No-Log Policy",
      description: "Based in a privacy-first jurisdiction. We don't store what you do. Period.",
      icon: <Shield className="w-6 h-6 text-yellow-400" />
    }
  ];

  const plans: PricingPlan[] = [
    {
      name: "Explorer",
      price: "$0",
      period: "per month",
      features: ["3 Server Locations", "1 Device Connection", "Standard Speed", "Email Support"]
    },
    {
      name: "Voyager",
      price: "$4.99",
      period: "per month",
      recommended: true,
      features: ["All Locations", "10 Device Connections", "Hyper-Speed", "24/7 Priority Support", "Ad Blocker"]
    },
    {
      name: "Galactic",
      price: "$79.99",
      period: "for 2 years",
      features: ["Lifetime Benefits", "Unlimited Devices", "Dedicated IP", "Beta Feature Access", "Stealth Protocol"]
    }
  ];

  return (
    <div className="pt-24 md:pt-32">
      {/* Hero Section */}
      <section className="container mx-auto px-6 py-12 lg:py-24 relative overflow-hidden">
        <div className="absolute top-0 right-0 -z-10 w-[500px] h-[500px] bg-yellow-400/5 rounded-full blur-[120px]"></div>
        <div className="absolute -bottom-20 -left-20 -z-10 w-[400px] h-[400px] bg-white/5 rounded-full blur-[100px]"></div>
        
        <div className="flex flex-col items-center text-center max-w-4xl mx-auto">
          <div className="inline-flex items-center gap-2 bg-white/5 border border-white/10 px-4 py-1.5 rounded-full text-xs font-semibold mb-8 backdrop-blur-sm">
            <span className="w-2 h-2 bg-yellow-400 rounded-full animate-ping"></span>
            OrbitX Protocol 2.0 is now live
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-8 leading-[1.1]">
            Your Privacy, <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-b from-white to-gray-500">In Perfect Orbit.</span>
          </h1>
          
          <p className="text-lg md:text-xl text-gray-400 mb-12 max-w-2xl">
            Experience the internet with the speed of light and the security of deep space. OrbitVPN keeps your data safe wherever you travel.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 mb-20">
            <button className="bg-yellow-400 text-black px-10 py-4 rounded-full text-lg font-bold hover:bg-yellow-300 transition-all shadow-[0_0_20px_rgba(250,204,21,0.2)] active:scale-95">
              Get Started Free
            </button>
            <button className="glass px-10 py-4 rounded-full text-lg font-bold hover:bg-white/10 transition-all active:scale-95">
              How it works
            </button>
          </div>
        </div>

        {/* Visual Element */}
        <div className="relative h-[300px] md:h-[500px] w-full flex items-center justify-center">
            <div className="absolute w-[200px] h-[200px] md:w-[350px] md:h-[350px] rounded-full border border-white/10 flex items-center justify-center">
                <div className="w-[150px] h-[150px] md:w-[250px] md:h-[250px] rounded-full border border-white/20 flex items-center justify-center">
                    <div className="w-[100px] h-[100px] md:w-[150px] md:h-[150px] rounded-full bg-gradient-to-br from-gray-900 to-black border border-white/30 flex items-center justify-center relative shadow-[inset_0_0_50px_rgba(255,255,255,0.05)]">
                        <div className="w-12 h-12 rounded-full bg-yellow-400 shadow-[0_0_30px_rgba(250,204,21,0.5)]"></div>
                        {/* Orbiting particles */}
                        <div className="absolute w-full h-full animate-[spin_10s_linear_infinite]">
                            <div className="absolute -top-2 left-1/2 w-4 h-4 rounded-full bg-white/20 backdrop-blur-sm"></div>
                        </div>
                        <div className="absolute w-[140%] h-[140%] animate-[spin_15s_linear_infinite_reverse]">
                            <div className="absolute top-1/2 -right-3 w-3 h-3 rounded-full bg-yellow-400/40 blur-[2px]"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-6 py-24">
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, idx) => (
            <GlassCard key={idx}>
              <div className="mb-6">{feature.icon}</div>
              <h3 className="text-xl font-bold mb-4">{feature.title}</h3>
              <p className="text-gray-400 text-sm leading-relaxed">{feature.description}</p>
            </GlassCard>
          ))}
        </div>
      </section>

      {/* Pricing Section */}
      <section className="container mx-auto px-6 py-24">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-5xl font-bold mb-4">Pricing Plans</h2>
          <p className="text-gray-400">Choose the orbit that fits your mission.</p>
        </div>
        
        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {plans.map((plan, idx) => (
            <GlassCard key={idx} className={plan.recommended ? 'border-yellow-400/50 relative overflow-hidden' : ''}>
              {plan.recommended && (
                <div className="absolute top-0 right-0 bg-yellow-400 text-black text-[10px] font-black px-3 py-1 rounded-bl-xl uppercase tracking-widest">
                  Recommended
                </div>
              )}
              <h4 className="text-lg font-bold text-gray-400 mb-2">{plan.name}</h4>
              <div className="flex items-baseline gap-2 mb-6">
                <span className="text-4xl font-bold">{plan.price}</span>
                <span className="text-gray-500 text-sm">{plan.period}</span>
              </div>
              <ul className="space-y-4 mb-8">
                {plan.features.map((feature, fIdx) => (
                  <li key={fIdx} className="flex items-center gap-3 text-sm text-gray-300">
                    <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                    {feature}
                  </li>
                ))}
              </ul>
              <button className={`w-full py-3 rounded-full text-sm font-bold transition-all ${plan.recommended ? 'bg-yellow-400 text-black hover:bg-yellow-300' : 'bg-white/5 hover:bg-white/10'}`}>
                Select Plan
              </button>
            </GlassCard>
          ))}
        </div>
      </section>
    </div>
  );
};

export default Home;
