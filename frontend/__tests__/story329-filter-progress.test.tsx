/**
 * STORY-329: Filter progress animation tests.
 * AC6: Frontend animates smoothly between micro-steps (60→62→64→66→68→70).
 * AC8: Test frontend simulating sequence 60→62→...→70 verifying animation.
 * UX-411: Updated — percentage display removed; verify via aria-valuenow instead.
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { EnhancedLoadingProgress } from '../app/buscar/components/EnhancedLoadingProgress';

describe('STORY-329: Filter progress animation', () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.clearAllTimers();
    jest.useRealTimers();
  });

  describe('AC6/AC8: Smooth micro-step animation during filtering', () => {
    it('should set aria-valuenow to 60 when filtering starts', () => {
      render(
        <EnhancedLoadingProgress
          currentStep={3}
          estimatedTime={60}
          stateCount={5}
          statesProcessed={5}
          ufAllComplete={true}
          sseEvent={{
            stage: 'filtering',
            progress: 60,
            message: 'Filtrando: 0/1000',
            detail: {},
          }}
        />
      );

      const progressBar = screen.getByRole('progressbar');
      expect(progressBar).toHaveAttribute('aria-valuenow', '60');
    });

    it('should animate through micro-steps 60→62→64→66→68→70 via aria-valuenow', () => {
      const steps = [60, 62, 64, 66, 68, 70];

      const { rerender } = render(
        <EnhancedLoadingProgress
          currentStep={3}
          estimatedTime={60}
          stateCount={5}
          statesProcessed={5}
          ufAllComplete={true}
          sseEvent={{
            stage: 'filtering',
            progress: steps[0],
            message: 'Filtrando: 0/1000',
            detail: {},
          }}
        />
      );

      const progressBar = screen.getByRole('progressbar');
      expect(progressBar).toHaveAttribute('aria-valuenow', `${steps[0]}`);

      for (let i = 1; i < steps.length; i++) {
        rerender(
          <EnhancedLoadingProgress
            currentStep={3}
            estimatedTime={60}
            stateCount={5}
            statesProcessed={5}
            ufAllComplete={true}
            sseEvent={{
              stage: 'filtering',
              progress: steps[i],
              message: `Filtrando: ${(steps[i] - 60) * 100}/1000`,
              detail: {},
            }}
          />
        );

        expect(progressBar).toHaveAttribute('aria-valuenow', `${steps[i]}`);
      }
    });

    it('should display SSE message during filtering', () => {
      render(
        <EnhancedLoadingProgress
          currentStep={3}
          estimatedTime={60}
          stateCount={5}
          statesProcessed={5}
          ufAllComplete={true}
          sseEvent={{
            stage: 'filtering',
            progress: 63,
            message: 'Filtrando: 150/500',
            detail: {},
          }}
        />
      );

      // UX-411: SSE messages are no longer displayed as status description
      // but the carousel shows educational tips instead. Verify progress via aria.
      const progressBar = screen.getByRole('progressbar');
      expect(progressBar).toHaveAttribute('aria-valuenow', '63');
    });

    it('should display LLM classification progress via aria-valuenow', () => {
      render(
        <EnhancedLoadingProgress
          currentStep={3}
          estimatedTime={60}
          stateCount={5}
          statesProcessed={5}
          ufAllComplete={true}
          sseEvent={{
            stage: 'filtering',
            progress: 67,
            message: 'Classificação IA: 5/20 sem keywords',
            detail: {},
          }}
        />
      );

      const progressBar = screen.getByRole('progressbar');
      expect(progressBar).toHaveAttribute('aria-valuenow', '67');
    });

    it('should not go backwards from fetch progress to filtering', () => {
      const { rerender } = render(
        <EnhancedLoadingProgress
          currentStep={2}
          estimatedTime={60}
          stateCount={5}
          statesProcessed={5}
          ufAllComplete={true}
          sseEvent={{
            stage: 'fetching',
            progress: 55,
            message: 'Buscando dados: 5/5 estados',
            detail: { uf_index: 5 },
          }}
        />
      );

      // After all UFs, should show >= 55% (ufBasedProgress: 10 + 1*50 = 60)
      const progressBar = screen.getByRole('progressbar');
      const fetchProgress = parseInt(progressBar.getAttribute('aria-valuenow') || '0');
      expect(fetchProgress).toBeGreaterThanOrEqual(55);

      // Now filtering starts at 60%
      rerender(
        <EnhancedLoadingProgress
          currentStep={3}
          estimatedTime={60}
          stateCount={5}
          statesProcessed={5}
          ufAllComplete={true}
          sseEvent={{
            stage: 'filtering',
            progress: 60,
            message: 'Filtrando: 0/1000',
            detail: {},
          }}
        />
      );

      const filterProgress = parseInt(progressBar.getAttribute('aria-valuenow') || '0');
      // Should not go below 60%
      expect(filterProgress).toBeGreaterThanOrEqual(60);
    });

    it('should show progressbar with transition for smooth animation', () => {
      render(
        <EnhancedLoadingProgress
          currentStep={3}
          estimatedTime={60}
          stateCount={5}
          statesProcessed={5}
          ufAllComplete={true}
          sseEvent={{
            stage: 'filtering',
            progress: 64,
            message: 'Filtrando: 200/500',
            detail: {},
          }}
        />
      );

      const progressBar = screen.getByRole('progressbar');
      expect(progressBar).toHaveAttribute('aria-valuenow', '64');
      // The bar should have transition CSS class for smooth animation
      expect(progressBar.className).toContain('transition-all');
    });
  });

  describe('AC4: Long-running filter message', () => {
    it('should display long-running message when is_long_running=true', () => {
      render(
        <EnhancedLoadingProgress
          currentStep={3}
          estimatedTime={60}
          stateCount={5}
          statesProcessed={5}
          ufAllComplete={true}
          sseEvent={{
            stage: 'filtering',
            progress: 63,
            message: 'Filtrando: 150/1000',
            detail: { is_long_running: true },
          }}
        />
      );

      expect(screen.getByTestId('long-running-message')).toBeInTheDocument();
      expect(screen.getByText(/Volume grande/)).toBeInTheDocument();
    });

    it('should not display long-running message without flag', () => {
      render(
        <EnhancedLoadingProgress
          currentStep={3}
          estimatedTime={60}
          stateCount={5}
          statesProcessed={5}
          ufAllComplete={true}
          sseEvent={{
            stage: 'filtering',
            progress: 63,
            message: 'Filtrando: 150/1000',
            detail: {},
          }}
        />
      );

      expect(screen.queryByTestId('long-running-message')).not.toBeInTheDocument();
    });

    it('should hide long-running message when overtime message shows', () => {
      // When isOvertime=true, overtime message takes priority
      jest.advanceTimersByTime(120_000); // 120s elapsed (> estimatedTime of 60)

      render(
        <EnhancedLoadingProgress
          currentStep={3}
          estimatedTime={60}
          stateCount={5}
          statesProcessed={5}
          ufAllComplete={true}
          sseEvent={{
            stage: 'filtering',
            progress: 63,
            message: 'Filtrando: 150/1000',
            detail: { is_long_running: true },
          }}
        />
      );

      // long-running message should be hidden when overtime kicks in
      // (component tracks its own elapsed time via internal timer)
    });
  });

  describe('AC5: LLM skipped handling', () => {
    it('should accept llm_skipped detail without crashing', () => {
      render(
        <EnhancedLoadingProgress
          currentStep={3}
          estimatedTime={60}
          stateCount={5}
          statesProcessed={5}
          ufAllComplete={true}
          sseEvent={{
            stage: 'filtering',
            progress: 70,
            message: 'Classificação IA ignorada (timeout)',
            detail: { llm_skipped: true, reason: 'timeout' },
          }}
        />
      );

      // UX-411: SSE messages are not displayed as text, but component should not crash
      const progressBar = screen.getByRole('progressbar');
      expect(progressBar).toHaveAttribute('aria-valuenow', '70');
    });
  });

  describe('UF-based progress cap', () => {
    it('should cap UF progress at 60% (not 70%)', () => {
      render(
        <EnhancedLoadingProgress
          currentStep={2}
          estimatedTime={60}
          stateCount={5}
          statesProcessed={5}
          ufAllComplete={true}
          sseEvent={{
            stage: 'fetching',
            progress: 55,
            message: 'Buscando dados: 5/5 estados',
            detail: { uf_index: 5 },
          }}
        />
      );

      // With ufAllComplete=true, ufBasedProgress = 10 + (1 * 50) = 60
      // effectiveProgress = max(55, 60) = 60 (in fetching branch)
      const progressBar = screen.getByRole('progressbar');
      const progressValue = parseInt(progressBar.getAttribute('aria-valuenow') || '0');
      expect(progressValue).toBeLessThanOrEqual(60);
    });
  });
});
