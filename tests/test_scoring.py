"""
tests/test_scoring.py
Unit tests for all three scoring strategies.
"""

import sys, os, uuid
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from models.lead import Lead, LeadType
from strategies.basic_scoring_strategy import BasicScoringStrategy
from strategies.scoring_strategies import PremiumScoringStrategy, RiskBasedScoringStrategy


def make_lead(**kwargs) -> Lead:
    defaults = dict(
        id=str(uuid.uuid4()), lead_type=LeadType.LIFE,
        first_name="X", last_name="Y", email="x@y.com",
        age=35, income=80000, coverage_amount=300000,
        lead_source="REFERRAL", prior_insurance=True,
    )
    defaults.update(kwargs)
    return Lead(**defaults)


def test_basic_scoring_range():
    s = BasicScoringStrategy()
    score = s.score(make_lead())
    assert 0 <= score <= 100


def test_premium_strategy_favours_high_income():
    s = PremiumScoringStrategy()
    high = s.score(make_lead(income=200000, coverage_amount=1_000_000))
    low  = s.score(make_lead(income=20000,  coverage_amount=10000))
    assert high > low


def test_risk_strategy_penalises_old_no_prior():
    s = RiskBasedScoringStrategy()
    young_prior = s.score(make_lead(age=30, prior_insurance=True))
    old_no_prior = s.score(make_lead(age=65, prior_insurance=False))
    assert young_prior > old_no_prior


def test_all_strategies_return_valid_range():
    lead = make_lead()
    for strategy in [BasicScoringStrategy(), PremiumScoringStrategy(), RiskBasedScoringStrategy()]:
        score = strategy.score(lead)
        assert 0 <= score <= 100, f"{strategy.__class__.__name__} returned {score}"
