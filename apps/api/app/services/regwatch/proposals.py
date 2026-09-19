"""RegWatch rule-pack proposals. LLM/system may propose only; humans activate."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from app.services.audit.hash_chain import AppendOnlyAuditLog
from app.utils.datetime import utc_now


class ProposalStatus(StrEnum):
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


@dataclass
class RulePackProposal:
    proposal_id: str
    rule_pack_id: str
    proposed_version: str
    summary: str
    source_id: str | None
    status: ProposalStatus = ProposalStatus.PROPOSED
    created_at: datetime = field(default_factory=utc_now)
    decided_at: datetime | None = None
    decided_by: str | None = None


@dataclass
class ActiveRulePack:
    rule_pack_id: str
    version: str
    activated_at: datetime
    activated_by: str
    proposal_id: str


class RegWatchService:
    """Proposal-only RegWatch. Unapproved packs are never active."""

    def __init__(self, *, audit: AppendOnlyAuditLog | None = None) -> None:
        self._audit = audit or AppendOnlyAuditLog()
        self._proposals: dict[str, RulePackProposal] = {}
        self._active: dict[str, ActiveRulePack] = {}

    @property
    def audit(self) -> AppendOnlyAuditLog:
        return self._audit

    def propose(
        self,
        *,
        rule_pack_id: str,
        proposed_version: str,
        summary: str,
        actor: str = "regwatch-agent",
        source_id: str | None = None,
    ) -> RulePackProposal:
        proposal = RulePackProposal(
            proposal_id=str(uuid.uuid4()),
            rule_pack_id=rule_pack_id,
            proposed_version=proposed_version,
            summary=summary,
            source_id=source_id,
        )
        self._proposals[proposal.proposal_id] = proposal
        self._audit.append(
            event_type="REGWATCH_PROPOSAL_CREATED",
            actor=actor,
            actor_role="system",
            payload={
                "proposal_id": proposal.proposal_id,
                "rule_pack_id": rule_pack_id,
                "proposed_version": proposed_version,
                "summary": summary,
                "status": proposal.status.value,
            },
            rule_pack_version=proposed_version,
        )
        return proposal

    def approve(self, proposal_id: str, *, actor: str) -> ActiveRulePack:
        proposal = self._require(proposal_id)
        if proposal.status is not ProposalStatus.PROPOSED:
            raise ValueError(f"Proposal {proposal_id} is {proposal.status}, not PROPOSED")
        proposal.status = ProposalStatus.APPROVED
        proposal.decided_at = utc_now()
        proposal.decided_by = actor
        active = ActiveRulePack(
            rule_pack_id=proposal.rule_pack_id,
            version=proposal.proposed_version,
            activated_at=proposal.decided_at,
            activated_by=actor,
            proposal_id=proposal.proposal_id,
        )
        self._active[proposal.rule_pack_id] = active
        self._audit.append(
            event_type="REGWATCH_PROPOSAL_APPROVED",
            actor=actor,
            actor_role="human",
            payload={
                "proposal_id": proposal.proposal_id,
                "rule_pack_id": proposal.rule_pack_id,
                "active_version": proposal.proposed_version,
            },
            rule_pack_version=proposal.proposed_version,
        )
        return active

    def reject(self, proposal_id: str, *, actor: str, reason: str | None = None) -> RulePackProposal:
        proposal = self._require(proposal_id)
        if proposal.status is not ProposalStatus.PROPOSED:
            raise ValueError(f"Proposal {proposal_id} is {proposal.status}, not PROPOSED")
        proposal.status = ProposalStatus.REJECTED
        proposal.decided_at = utc_now()
        proposal.decided_by = actor
        self._audit.append(
            event_type="REGWATCH_PROPOSAL_REJECTED",
            actor=actor,
            actor_role="human",
            payload={
                "proposal_id": proposal.proposal_id,
                "rule_pack_id": proposal.rule_pack_id,
                "reason": reason,
            },
            rule_pack_version=proposal.proposed_version,
        )
        return proposal

    def is_active(self, rule_pack_id: str, version: str) -> bool:
        active = self._active.get(rule_pack_id)
        return active is not None and active.version == version

    def get_active(self, rule_pack_id: str) -> ActiveRulePack | None:
        return self._active.get(rule_pack_id)

    def get_proposal(self, proposal_id: str) -> RulePackProposal | None:
        return self._proposals.get(proposal_id)

    def _require(self, proposal_id: str) -> RulePackProposal:
        proposal = self._proposals.get(proposal_id)
        if proposal is None:
            raise KeyError(f"Unknown proposal {proposal_id}")
        return proposal
