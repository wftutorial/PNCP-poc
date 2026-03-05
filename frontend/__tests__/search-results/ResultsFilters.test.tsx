/**
 * TD-007 AC6: ResultsFilters sub-component tests.
 * Tests UF count chip, "27 UFs (todo o Brasil)" text,
 * "Licitações abertas" chip, sector name chip (setor mode),
 * and absence of sector chip in termos mode.
 */

import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";

import { ResultsFilters } from "../../app/buscar/components/search-results/ResultsFilters";

describe("ResultsFilters", () => {
  // --- UF count chip ---

  it("shows UF count chip with correct count", () => {
    render(
      <ResultsFilters
        ufsSelecionadas={new Set(["SP", "RJ", "MG"])}
        searchMode="setor"
        sectorName="Informática"
      />
    );
    expect(screen.getByText("3 UFs")).toBeInTheDocument();
  });

  it("shows singular 'UF' for single selection", () => {
    render(
      <ResultsFilters
        ufsSelecionadas={new Set(["SP"])}
        searchMode="setor"
        sectorName="Informática"
      />
    );
    expect(screen.getByText("1 UF")).toBeInTheDocument();
  });

  it("shows '27 UFs (todo o Brasil)' when all 27 UFs are selected", () => {
    const allUfs = new Set([
      "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO",
      "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR",
      "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO",
    ]);
    render(
      <ResultsFilters
        ufsSelecionadas={allUfs}
        searchMode="setor"
        sectorName="Informática"
      />
    );
    expect(screen.getByText("27 UFs (todo o Brasil)")).toBeInTheDocument();
  });

  // --- "Licitações abertas" chip ---

  it("always shows 'Licitações abertas' chip", () => {
    render(
      <ResultsFilters
        ufsSelecionadas={new Set(["SP"])}
        searchMode="setor"
        sectorName="Informática"
      />
    );
    expect(screen.getByText("Licitações abertas")).toBeInTheDocument();
  });

  it("shows 'Licitações abertas' chip in termos mode too", () => {
    render(
      <ResultsFilters
        ufsSelecionadas={new Set(["RJ"])}
        searchMode="termos"
        sectorName=""
      />
    );
    expect(screen.getByText("Licitações abertas")).toBeInTheDocument();
  });

  // --- Sector chip in setor mode ---

  it("shows sector name chip in setor mode", () => {
    render(
      <ResultsFilters
        ufsSelecionadas={new Set(["SP"])}
        searchMode="setor"
        sectorName="Construção Civil"
      />
    );
    expect(screen.getByText("Construção Civil")).toBeInTheDocument();
  });

  it("does not show sector chip in termos mode", () => {
    render(
      <ResultsFilters
        ufsSelecionadas={new Set(["SP"])}
        searchMode="termos"
        sectorName="Informática"
      />
    );
    // In termos mode the sector name chip should not appear
    expect(screen.queryByText("Informática")).not.toBeInTheDocument();
  });

  // --- "Filtros ativos" label ---

  it("always shows 'Filtros ativos:' label", () => {
    render(
      <ResultsFilters
        ufsSelecionadas={new Set(["SP"])}
        searchMode="setor"
        sectorName="Saúde"
      />
    );
    expect(screen.getByText("Filtros ativos:")).toBeInTheDocument();
  });

  // --- Various UF counts ---

  it("shows correct count for 10 UFs", () => {
    const tenUfs = new Set(["SP", "RJ", "MG", "RS", "SC", "PR", "BA", "PE", "CE", "GO"]);
    render(
      <ResultsFilters
        ufsSelecionadas={tenUfs}
        searchMode="termos"
        sectorName=""
      />
    );
    expect(screen.getByText("10 UFs")).toBeInTheDocument();
  });

  it("shows correct chip text for different sector names", () => {
    render(
      <ResultsFilters
        ufsSelecionadas={new Set(["SP", "RJ"])}
        searchMode="setor"
        sectorName="Saneamento e Meio Ambiente"
      />
    );
    expect(screen.getByText("Saneamento e Meio Ambiente")).toBeInTheDocument();
  });
});
