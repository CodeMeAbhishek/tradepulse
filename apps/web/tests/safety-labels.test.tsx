import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, test, expect } from 'vitest';
import { StatusRouteChip } from '@/components/queue/StatusRouteChip';
import { PrototypeBanner } from '@/components/PrototypeBanner';
import { IdentityEvidenceDrawer } from '@/components/case/IdentityEvidenceDrawer';

describe('Safety Label Rendering', () => {
  test('StatusRouteChip renders explicit text for route and status (not just color)', () => {
    render(<StatusRouteChip status="DOCUMENT_PACK_INCOMPLETE" readinessRoute="DOCUMENT_PACK_INCOMPLETE" />);
    // Should display human readable label
    expect(screen.getByText(/Document pack incomplete/i)).toBeInTheDocument();
    // Should display raw status code
    expect(screen.getByText(/Status code: DOCUMENT_PACK_INCOMPLETE/i)).toBeInTheDocument();
  });

  test('PrototypeBanner renders demo data disclaimers', () => {
    render(<PrototypeBanner />);
    // The banner must name the data as demo in words, not by colour alone.
    expect(screen.getByText(/DEMO DATA/i)).toBeInTheDocument();
    expect(screen.getByText(/Decision support only — not a Customs portal/i)).toBeInTheDocument();
  });

  test('IdentityEvidenceDrawer renders correct label for fixture VLEI and explicit outcome', () => {
    const mockParties = [{
      role: "SELLER" as const,
      name: "Acme Corp",
      rawName: "Acme Corp",
      normalizedName: "ACME CORP",
      lei: null,
      leiStatus: "NONE",
      gleifCandidates: [],
      identityOutcome: "IDENTITY_SUPPORTED_BY_VLEI" as const,
      vleiStatus: "VERIFIED_FIXTURE" as const,
      vleiLabel: "VLEI fixture verified · SYNTHETIC_DEMO_CREDENTIAL",
      similarityNote: "Exact match",
      isExactDocumentMatch: true,
      // Provenance is required, not optional. The drawer renders these as the
      // "Source / snapshot" line, so a party without them exercises the one
      // state this component should never be in: evidence with no stated
      // origin. Values match the equivalent fixture in lib/mock/case-detail.ts.
      source: "VLEI_FIXTURE_ADAPTER",
      retrievedAt: "2026-08-21T13:00:00Z",
      snapshotId: "vlei-fix-demo-01"
    }];
    render(<IdentityEvidenceDrawer parties={mockParties} />);
    
    // Outcome label
    expect(screen.getByText(/Identity supported by VLEI/i)).toBeInTheDocument();
    // Specific fixture label
    expect(screen.getByText(/VLEI fixture verified/i)).toBeInTheDocument();
    expect(screen.getByText(/SYNTHETIC_DEMO_CREDENTIAL/i)).toBeInTheDocument();
  });
});
