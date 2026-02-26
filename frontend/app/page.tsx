// Landing Page Institucional - STORY-168 + STORY-173 + STORY-273
// Route: / (root)
import LandingNavbar from './components/landing/LandingNavbar';
import HeroSection from './components/landing/HeroSection';
import OpportunityCost from './components/landing/OpportunityCost';
import BeforeAfter from './components/landing/BeforeAfter';
import DifferentialsGrid from './components/landing/DifferentialsGrid';
import HowItWorks from './components/landing/HowItWorks';
import StatsSection from './components/landing/StatsSection';
import DataSourcesSection from './components/landing/DataSourcesSection';
import SectorsGrid from './components/landing/SectorsGrid';
import FinalCTA from './components/landing/FinalCTA';
import ProofOfValue from './components/landing/ProofOfValue';
import ValuePropSection from './components/ValuePropSection';
import ComparisonTable from './components/ComparisonTable';
import AnalysisExamplesCarousel from './components/landing/AnalysisExamplesCarousel';
import TrustCriteria from './components/landing/TrustCriteria';
import TestimonialSection from '../components/TestimonialSection';
import Footer from './components/Footer';

export default function LandingPage() {
  return (
    <>
      <LandingNavbar />

      <main id="main-content">
        <HeroSection />
        <ProofOfValue />
        <AnalysisExamplesCarousel />
        <ValuePropSection />
        <OpportunityCost />
        <BeforeAfter />

        {/* STORY-273 AC1: Testimonials between BeforeAfter and ComparisonTable */}
        <TestimonialSection />

        <ComparisonTable />
        <DifferentialsGrid />
        <HowItWorks />
        <StatsSection />
        <section id="sobre">
          <DataSourcesSection />
        </section>
        <SectorsGrid />
        <TrustCriteria />

        {/* GTM-COPY-005 AC6: Credibility badge */}
        <div className="text-center py-6 bg-surface-1 border-y border-[var(--border)]">
          <p className="text-sm text-ink-secondary">
            Desenvolvido pela <strong className="text-ink">CONFENGE Avaliações e Inteligência Artificial</strong>{' '}
            <span className="mx-1">·</span>{' '}
            <a href="/sobre" className="text-brand-blue hover:underline">Conheça nossa metodologia</a>
          </p>
        </div>

        {/* STORY-273 AC3: Beta counter near FinalCTA */}
        <div className="text-center py-8 bg-[var(--canvas)]" data-testid="beta-counter">
          <p className="text-lg font-semibold text-[var(--ink)]">
            Mais de <span className="text-[var(--brand-blue)] font-bold">10 empresas</span> já testaram o SmartLic durante o beta
          </p>
          <p className="text-sm text-[var(--ink-muted)] mt-1">
            Setores como uniformes, TI, engenharia, saúde e facilities
          </p>
        </div>

        <section id="suporte">
          <FinalCTA />
        </section>
      </main>

      <Footer />
    </>
  );
}
