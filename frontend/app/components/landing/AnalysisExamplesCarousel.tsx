// RSC wrapper — delegates rendering to the client carousel island.
// DEBT-FE-017: Converted to RSC; interactive logic lives in AnalysisExamplesCarouselClient.tsx.
import AnalysisExamplesCarouselClient from './AnalysisExamplesCarouselClient';

export default function AnalysisExamplesCarousel() {
  return <AnalysisExamplesCarouselClient />;
}
