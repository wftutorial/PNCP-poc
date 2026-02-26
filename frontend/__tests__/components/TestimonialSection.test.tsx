/**
 * STORY-273: TestimonialSection Component Tests
 *
 * Tests:
 * - Renders with default testimonials (5)
 * - Renders with 0 testimonials (returns null)
 * - Renders with 3 testimonials
 * - Renders with 6 testimonials
 * - Displays quote, name, role, company, sector badge
 * - Star rating renders correctly
 * - Custom heading
 */

import { render, screen } from '@testing-library/react';
import TestimonialSection, {
  TESTIMONIALS,
  type Testimonial,
} from '@/components/TestimonialSection';

describe('TestimonialSection Component', () => {
  describe('Rendering with different testimonial counts', () => {
    it('should render with default testimonials', () => {
      render(<TestimonialSection />);

      const section = screen.getByTestId('testimonial-section');
      expect(section).toBeInTheDocument();

      // Default heading
      expect(
        screen.getByText('O que dizem nossos primeiros usuários')
      ).toBeInTheDocument();

      // Should render all default testimonials
      TESTIMONIALS.forEach((t) => {
        expect(screen.getByText(t.name)).toBeInTheDocument();
      });
    });

    it('should return null with 0 testimonials', () => {
      const { container } = render(<TestimonialSection testimonials={[]} />);

      expect(
        screen.queryByTestId('testimonial-section')
      ).not.toBeInTheDocument();
      expect(container.innerHTML).toBe('');
    });

    it('should render with 3 testimonials', () => {
      const threeTestimonials = TESTIMONIALS.slice(0, 3);
      render(<TestimonialSection testimonials={threeTestimonials} />);

      expect(screen.getByTestId('testimonial-section')).toBeInTheDocument();
      threeTestimonials.forEach((t) => {
        expect(screen.getByText(t.name)).toBeInTheDocument();
      });

      // Should NOT render the 4th testimonial
      expect(screen.queryByText(TESTIMONIALS[3].name)).not.toBeInTheDocument();
    });

    it('should render with 6 testimonials', () => {
      const sixTestimonials: Testimonial[] = [
        ...TESTIMONIALS,
        {
          quote: 'Sexto depoimento de teste.',
          name: 'Teste S.',
          role: 'Analista',
          company: 'Empresa Teste',
          sector: 'Software e Sistemas',
          rating: 4,
        },
      ];

      render(<TestimonialSection testimonials={sixTestimonials} />);

      expect(screen.getByTestId('testimonial-section')).toBeInTheDocument();
      sixTestimonials.forEach((t) => {
        expect(screen.getByText(t.name)).toBeInTheDocument();
      });
    });
  });

  describe('Testimonial card content', () => {
    it('should display quote text', () => {
      render(<TestimonialSection />);

      // Check first testimonial quote (partial match)
      expect(
        screen.getByText(/Antes eu gastava 2 dias por semana/)
      ).toBeInTheDocument();
    });

    it('should display name, role, and company', () => {
      render(<TestimonialSection />);

      const firstTestimonial = TESTIMONIALS[0];
      expect(screen.getByText(firstTestimonial.name)).toBeInTheDocument();
      expect(
        screen.getByText(
          `${firstTestimonial.role} — ${firstTestimonial.company}`
        )
      ).toBeInTheDocument();
    });

    it('should display sector badge', () => {
      render(<TestimonialSection />);

      TESTIMONIALS.forEach((t) => {
        expect(screen.getByText(t.sector)).toBeInTheDocument();
      });
    });

    it('should render star ratings when provided', () => {
      const { container } = render(<TestimonialSection />);

      // Each testimonial with a rating should have star SVGs
      const starRatings = container.querySelectorAll(
        '[aria-label*="estrelas"]'
      );
      // All default testimonials have ratings
      expect(starRatings.length).toBe(TESTIMONIALS.length);
    });

    it('should not render rating when not provided', () => {
      const noRatingTestimonials: Testimonial[] = [
        {
          quote: 'Sem rating.',
          name: 'Sem R.',
          role: 'Cargo',
          company: 'Empresa',
          sector: 'Saúde',
        },
      ];

      const { container } = render(
        <TestimonialSection testimonials={noRatingTestimonials} />
      );

      expect(
        container.querySelector('[aria-label*="estrelas"]')
      ).not.toBeInTheDocument();
    });
  });

  describe('Custom heading', () => {
    it('should render custom heading', () => {
      render(
        <TestimonialSection heading="Empresas que já usam SmartLic" />
      );

      expect(
        screen.getByText('Empresas que já usam SmartLic')
      ).toBeInTheDocument();
    });
  });

  describe('Custom className', () => {
    it('should apply custom className', () => {
      render(<TestimonialSection className="custom-test-class" />);

      const section = screen.getByTestId('testimonial-section');
      expect(section).toHaveClass('custom-test-class');
    });
  });

  describe('Exported constants', () => {
    it('should export TESTIMONIALS with at least 3 items', () => {
      expect(TESTIMONIALS.length).toBeGreaterThanOrEqual(3);
    });

    it('each testimonial should have required fields', () => {
      TESTIMONIALS.forEach((t) => {
        expect(t.quote).toBeTruthy();
        expect(t.name).toBeTruthy();
        expect(t.role).toBeTruthy();
        expect(t.company).toBeTruthy();
        expect(t.sector).toBeTruthy();
      });
    });
  });
});
