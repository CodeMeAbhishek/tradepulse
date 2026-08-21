import { describe, test, expect } from 'vitest';
import { MOCK_QUEUE_CASES } from '@/lib/mock/queue';
import { getCaseWorkbenchDetail } from '@/lib/mock/case-detail';
import { MOCK_REGWATCH_EVENTS } from '@/lib/mock/regwatch';
import { getChecklistForProfile } from '@/lib/mock/profiles';

describe('Mock Data Type Conformance and Safety Rules', () => {
  test('Queue fixtures enforce SYNTHETIC_DEMO source', () => {
    MOCK_QUEUE_CASES.forEach(c => {
      expect(c.dataSourceLabel).toBe('SYNTHETIC_DEMO');
    });
  });

  test('Case detail maintains strict VLEI fixture labeling', () => {
    MOCK_QUEUE_CASES.forEach(c => {
      const detail = getCaseWorkbenchDetail(c.id);
      if (detail) {
        detail.identities.forEach(party => {
          if (party.vleiStatus === 'VERIFIED_FIXTURE') {
            expect(party.vleiLabel).toContain('fixture');
            expect(party.vleiLabel).toContain('SYNTHETIC_DEMO');
          }
        });
      }
    });
  });

  test('RegWatch events maintain proposal vs active state rules', () => {
    const proposed = MOCK_REGWATCH_EVENTS.find(e => e.approvalState === 'PROPOSED');
    expect(proposed?.replayAllowed).toBe(false);

    const approved = MOCK_REGWATCH_EVENTS.find(e => e.approvalState === 'APPROVED');
    expect(approved?.replayAllowed).toBe(true);
  });

  test('Profiles enforce Commercial Invoice as blocker', () => {
    const checklist = getChecklistForProfile('INVOICE_ONLY_PRE_REVIEW');
    const invoiceReq = checklist.find(i => i.documentType === 'COMMERCIAL_INVOICE');
    expect(invoiceReq?.state).toBe('REQUIRED');
    expect(invoiceReq?.blocker).toBe(true);
  });
});
