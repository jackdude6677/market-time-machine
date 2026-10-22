build this: JARVIS MASTER BUILD SPECIFICATION

MARKET TIME MACHINE 3.0

Autonomous Trading Intelligence, Strategy Evolution, Survival Grading, Market Relationship Discovery, and Live Control UI

1. MISSION

Jarvis, build a complete, functioning stock-market simulation called Market Time Machine.

This is an implementation task. You must inspect the existing computer and project, implement the system, connect its components, run tests, and leave the project in a working state.

Do not stop after producing a plan, a mockup, empty files, or an explanation of how the project could work.

The objective is to create an autonomous trading research agent that learns from historical markets, discovers its own trading strategies, analyzes financial and nonfinancial information, improves through measured performance, and eventually transitions into live paper trading.

The project consists of two primary agents:

- The Oracle: Controls historical market information and knows the actual outcomes.
- The Trader: Starts in the past, makes independent decisions without future knowledge, and learns to maximize its weekly grade.

The system must also include an independent grading engine, risk manager, adversarial Auditor, strategy research laboratory, market relationship discovery system, and live graphical interface.

Initial starting capital: $1,000 USD.

Initial historical period: January 2020 through December 2025, subject to verified data availability.

Initial trading mode: historical simulation with simulated orders only.

Use a modular, local-first architecture. Prefer free software and locally available resources. Do not introduce paid APIs, subscriptions, cloud infrastructure, or credit-card requirements without explicit authorization.

Inspect the existing environment before choosing dependencies. Preserve working components and avoid unnecessary reinstalls, destructive changes, or modifications to unrelated projects.

---

2. AGENT A: THE ORACLE

The Oracle is the simulation's privileged historical data controller, market environment, and outcome referee.

It has access to the historical record, including:

- Stock prices, trading volume, and market indexes.
- Exchange and sector information.
- Company financial statements and earnings announcements.
- Revenue, profit, guidance, valuation, and analyst estimates where available.
- Product announcements, acquisitions, corporate restructuring, and company-specific events.
- Interest rates, inflation, employment, and central bank decisions.
- Political developments, elections, tariffs, sanctions, legislation, and regulations.
- Commodities, currencies, bonds, and economic indicators.
- Historical news, media, and social sentiment where authentic timestamped data exists.
- Dividends, stock splits, delistings, bankruptcies, and other corporate actions.
- Actual future prices and outcomes for the historical simulation.

The Oracle must:

1. Advance the historical clock.
2. Release only information available at the current simulated timestamp.
3. Provide relevant news and market information to the Trader.
4. Record the Trader's forecasts and orders before outcomes occur.
5. Execute the historical market environment.
6. Calculate actual portfolio results.
7. Provide independent grading and feedback.
8. Maintain a complete audit trail.
9. Investigate significant market events and trading errors.
10. Keep future knowledge private until the appropriate outcome is revealed.

The Oracle must distinguish between facts, estimates, and hypotheses.

For example, if a graphics-card announcement occurs, the Oracle releases the announcement at the appropriate time. It does not tell the Trader whether the stock subsequently rose or fell.

After the outcome is revealed, the Oracle may investigate the result using reliable historical evidence. It must not invent causal explanations simply because an event occurred before a price movement.

The Oracle's private data must never be directly accessible to the Trader.

3. AGENT B: THE TRADER

The Trader is an autonomous trading agent whose objective is to maximize its weekly grade through excellent investment decisions.

It starts in January 2020 with $1,000 in cash and no existing positions.

It may use general financial knowledge, statistical methods, machine learning, historical information already encountered, and any permitted tools. It must not know future stock prices, news, earnings, political events, or eventual investment outcomes.

The Trader must learn to:

- Analyze available market data.
- Recognize price patterns and changing trends.
- Evaluate company fundamentals and valuation where reliable data exists.
- Interpret economic, political, and social developments.
- Identify relationships among companies and markets.
- Estimate potential returns and downside risk.
- Predict outcomes over multiple time horizons.
- Develop its own investment strategies.
- Decide which assets to trade and when.
- Determine position sizes and exit conditions.
- Choose between buying, selling, holding, and remaining in cash.
- Evaluate previous predictions.
- Learn from profitable and unprofitable decisions.
- Improve its models through controlled experiments.
- Protect capital when market conditions deteriorate.

Do not hardcode one permanent trading strategy.

The Trader must discover its own approach to making money through experimentation, evidence, and measured results.

It must be able to create, modify, combine, test, promote, and abandon strategies without requiring a developer to manually rewrite the application each time.

The Trader is not required to trade constantly. Remaining in cash is valid when expected returns do not justify the risk and transaction costs.

The Trader's survival motivation must be implemented through explicit simulation rules and consequences. Do not claim that it has genuine human emotions or biological survival needs.

4. STARTING CAPITAL AND PORTFOLIO ACCOUNTING

Set the initial capital to exactly $1,000 USD.

Apply this starting balance consistently throughout historical simulation, grading, strategy experiments, portfolio accounting, shadow comparisons, and dashboard displays.

The Trader starts with:

- Cash: $1,000.
- Holdings: $0.
- Debt: $0.
- Leverage: disabled.

The accounting engine must track:

- Cash balance.
- Holdings and quantities.
- Average acquisition cost.
- Current market value.
- Realized profit and loss.
- Unrealized profit and loss.
- Dividends.
- Transaction costs.
- Commissions and fees.
- Spreads and slippage.
- Portfolio equity.
- Exposure by asset and sector.
- Open orders.
- Historical drawdowns.
- Deposits and withdrawals, if ever explicitly enabled.

Portfolio equity must reconcile with cash, holdings, liabilities, and accrued costs.

Do not allow negative cash, accidental leverage, fictitious profits from stock splits, or unaccounted corporate actions.

Support fractional shares only when the simulated instrument and broker configuration permit them. Otherwise, enforce whole-share quantities.

Use realistic execution assumptions. A signal generated using a completed closing price cannot automatically be filled at that same closing price if it was not available when the order was submitted.

Default risk limits

- Maximum individual position: 5% of portfolio equity.
- Maximum single-sector exposure: 25%.
- Maximum gross exposure: 100%.
- No leverage.
- No short selling in the initial version.
- No orders that exceed available cash.
- No orders using invalid or unavailable prices.
- No orders that breach risk limits.

At $1,000, the default maximum individual position is initially $50.

The Trader must learn to operate effectively with small capital. It must not relax its risk limits to improve its grade.

All limits must be configurable by the developer and enforced by a separate risk manager that the Trader cannot override.

5. HISTORICAL TIME MACHINE

Use January 2020 through December 2025 as the initial target period.

Implement the following real-time conversion:

- One historical calendar month equals one week of real elapsed time.
- One historical calendar day equals approximately 5.6 hours of real elapsed time.
- One historical year equals approximately 12 real weeks.
- Five historical years equal approximately 60 real weeks.

The simulation clock must be configurable and independent of the grading clock.

Support:

- Start.
- Pause.
- Resume.
- Stop.
- Advance one trading day.
- Advance one historical week.
- Accelerated execution.
- Manual stepping.
- Save and restore checkpoints.
- Restart after a crash.
- Inspect the current simulated date.
- Inspect actual elapsed time.
- Change simulation speed.

The market must respect real historical trading calendars, weekends, holidays, and after-hours announcements.

Changing the clock speed must not change prices, orders, forecasts, grading rules, or available information.

The weekly grade is issued every seven days of actual elapsed time. Provide a separate accelerated evaluation mode for testing the grading system during development. Label this mode clearly and do not confuse accelerated test grades with actual seven-day survival periods.

6. STRICT INFORMATION FIREWALL

This is a mandatory architectural requirement.

The Oracle knows the future. The Trader does not.

Implement separate database permissions, service interfaces, and data-access controls.

The Trader may access:

- Historical prices available at the simulated timestamp.
- News published and available by that timestamp.
- Financial statements available at that time.
- Economic data released at that time.
- Its own past decisions and outcomes already revealed.
- Its own strategy and experiment history.
- Current portfolio state.
- Permitted historical research results.

The Trader must not access:

- Future prices.
- Future news.
- Future earnings results.
- Future financial statements.
- Future economic releases.
- Oracle-only causal explanations containing future information.
- Complete future market datasets through hidden database queries.
- Grading information that reveals future outcomes.
- Features calculated using observations from future dates.

Each record should include, wherever applicable:

- Event timestamp.
- Publication timestamp.
- Availability timestamp.
- Source.
- Asset or indicator.
- Data version.
- Provenance.
- Revision history.

Use point-in-time data. Economic indicators and financial statements must reflect what was actually known at the time, not revised information published later.

Before every trading decision, save an immutable snapshot of the Trader's available information.

Lock each prediction and order intent before revealing the associated outcome.

The Auditor must actively test the firewall by attempting to retrieve prohibited future information. Any confirmed leak must block the affected experiment or model promotion.

7. TRADING DECISION ENGINE

At each historical trading session, execute the following sequence.

Step 1: Advance time

The Oracle advances to the next valid market session.

Step 2: Release information

Provide only information available by that simulated timestamp.

Step 3: Analyze the market

The Trader evaluates:

- Price momentum.
- Volume and liquidity.
- Volatility.
- Relative strength.
- Sector behavior.
- Company fundamentals.
- Valuation.
- Earnings and guidance.
- Interest rates and inflation.
- Commodities and currencies.
- Political and regulatory developments.
- News sentiment and novelty.
- Economic expectations.
- Portfolio concentration.
- Correlations.
- Market regime.
- Historical patterns already encountered.

These are available research inputs, not a fixed strategy the Trader must always follow.

Step 4: Generate forecasts

For relevant candidate assets, estimate:

- Probability of a positive return.
- Expected return.
- Expected downside.
- Uncertainty.
- Expected holding period.
- Important catalysts.
- Conditions that would invalidate the hypothesis.
- Estimated transaction costs.
- Expected return after costs.

Support multiple prediction horizons, such as one trading day, five trading days, twenty trading days, and longer periods where appropriate.

Step 5: Select actions

The Trader chooses whether to buy, sell, hold, reduce exposure, or remain in cash.

Record:

- Asset identifier.
- Proposed order type.
- Quantity or allocation.
- Entry conditions.
- Exit conditions.
- Risk limits.
- Forecast probabilities.
- Expected return and downside.
- Reasoning and supporting evidence.
- Decision timestamp.

Step 6: Lock the decision

Make the forecast and order record immutable before revealing the outcome.

Step 7: Execute

Apply realistic prices, fees, spreads, slippage, liquidity, order restrictions, and corporate actions where data permits.

Step 8: Reveal outcomes

The Oracle reveals the relevant actual outcome at the appropriate simulated time.

Step 9: Score and learn

Update the portfolio ledger, evaluate forecasts, calculate performance, and store lessons for future decisions.

Distinguish a correct forecast from a profitable trade. A correct directional prediction may still lose money after costs, and a profitable trade may result from luck rather than skill.

8. SELF-DISCOVERING STRATEGY ENGINE

The Trader must discover its own trading strategies rather than being forced to follow predefined strategies.

Hypothesis generation

The Trader can formulate questions based on observations.

Examples:

- Does a particular earnings surprise contain predictive information?
- Do related companies provide useful signals about one another?
- Are certain market patterns useful only in high-volatility environments?
- Does news sentiment improve predictions beyond price data?
- Do some economic indicators predict changes in particular sectors?
- When does holding cash outperform taking more risk?

These are hypotheses, not assumed truths.

Strategy creation

Represent each strategy as a versioned, testable specification containing:

- Hypothesis.
- Entry conditions.
- Exit conditions.
- Features.
- Forecast horizon.
- Position-sizing method.
- Risk limits.
- Asset selection logic.
- Transaction-cost assumptions.
- Conditions under which the strategy should not operate.

The Trader may create strategies using statistical signals, quantitative models, news analysis, market relationships, combinations of features, or newly discovered approaches.

Experimentation

The Trader may:

- Generate new strategies.
- Modify existing strategies.
- Combine strategies.
- Test parameters.
- Discover new features.
- Retire failing strategies.
- Investigate unexpected results.
- Develop new mathematical or statistical approaches.

Each experiment must record its hypothesis, data cutoff, model version, validation period, results, and decision.

Strategy competition

Allow multiple independently developed strategies to compete using identical information, execution assumptions, and risk constraints.

Compare candidates against:

- The current approved strategy.
- A broad market benchmark.
- A buy-and-hold benchmark.
- A cash or appropriate risk-free benchmark.
- Simple statistical baselines.

Evaluate net returns, risk-adjusted performance, drawdown, stability, transaction costs, and out-of-sample results.

Do not automatically promote the candidate with the highest historical return.

Strategy promotion

Maintain:

- Champion: currently approved strategy.
- Challengers: experimental candidates.
- Frozen baseline: a stable reference.
- Historical versions: preserved for comparison and rollback.

A challenger can replace the champion only after passing predefined validation and Auditor checks.

The Trader must not be able to delete losing experiments, rewrite past results, or silently change acceptance criteria.

9. WEEKLY GRADING AND SURVIVAL SYSTEM

Every seven days of actual elapsed time, an independent grading engine assigns the Trader a grade from 0 to 100.

The Trader's sole operational objective is to maximize its sustainable grade. It should continuously strive for 100%, learn from errors, and improve its future decisions.

Use this initial grading formula:

- Net portfolio performance: 35 points.
- Risk-adjusted performance: 20 points.
- Capital preservation and drawdown: 20 points.
- Prediction accuracy and calibration: 10 points.
- Decision and execution discipline: 10 points.
- Demonstrated learning and improvement: 5 points.

Total: 100 points.

Document all calculations and normalization rules.

Use realized and unrealized P&L, transaction costs, portfolio exposure, drawdowns, and appropriate risk metrics.

Use minimum observation requirements for unreliable small samples. A small number of trades must not produce unjustified statistical certainty.

Prediction scoring should include proper scoring rules, such as the Brier score, when appropriate.

Learning points require demonstrated improvement, not merely generating more code or explanations.

Prevent grade manipulation

Do not reward the Trader for:

- Taking extreme risks to generate a large return.
- Avoiding every trade simply to avoid recording a loss.
- Making many tiny trades to inflate win rate.
- Hiding losing positions.
- Deleting unsuccessful forecasts.
- Altering confidence after the outcome.
- Ignoring fees.
- Changing benchmarks to easier alternatives.
- Optimizing against weaknesses in the scoring formula.

The grading engine must independently verify every metric against the authoritative ledger.

Survival states

Use these initial rules:

- Grade 90–100: excellent standing.
- Grade 75–89: satisfactory standing.
- Grade 60–74: warning status.
- Grade below 60: critical status.
- Three consecutive weeks below 60: probation.
- Five consecutive weeks below 60: survival review.

Poor grades can trigger reduced risk limits, strategy reviews, and restrictions on unvalidated models.

A survival failure must not erase memory or destroy historical records.

Provide configurable recovery and reversible simulated termination rules.

Weekly report

Generate a report containing:

- Overall grade and category scores.
- Starting and ending equity.
- Net profit or loss.
- Return percentage.
- Realized and unrealized P&L.
- Fees and slippage.
- Maximum drawdown.
- Volatility and downside risk.
- Number of trades.
- Win rate and average win/loss.
- Largest gain and loss.
- Prediction calibration.
- Benchmark comparison.
- Risk violations.
- Best and worst decisions.
- Missed opportunities.
- Major errors.
- Detected patterns.
- Model and strategy changes.
- Three priorities for the next week.

Require the Trader to create a structured improvement plan.

It must distinguish poor decisions from reasonable decisions with unfavorable outcomes and lucky results from repeatable skill.

10. MARKET REGIME DETECTOR

Build a component that identifies changing market conditions, including:

- Bull and bear markets.
- High and low volatility.
- Rising and falling interest rates.
- Inflation shocks.
- Recession concerns.
- Commodity supply shocks.
- Changes in market breadth.
- Sector rotations.
- Periods of unusual correlation.

Track how each discovered strategy performs under different conditions.

Allow the Trader to change its strategy selection and capital allocation when conditions change.

Do not assume that a regime classification is always correct. Store uncertainty and evaluate whether regime detection improves out-of-sample performance.

11. MARKET RELATIONSHIP DISCOVERY MAP

Build a dynamic relationship graph that allows the Trader to discover connections between companies, industries, assets, and economic factors.

This is a core analytical component, not a decorative visualization.

Nodes

Represent:

- Companies.
- Stocks and ETFs.
- Sectors.
- Suppliers and customers.
- Competitors.
- Commodities.
- Currencies.
- Interest rates.
- Economic indicators.
- Political events.
- Regulatory developments.
- News events.

Relationships

Support relationships such as:

- Supplier and customer.
- Competitor or substitute.
- Shared industry exposure.
- Shared economic exposure.
- Statistical correlation.
- Possible causal influence.
- Indirect multi-step exposure.
- Historical predictive relationship.

For each relationship, record:

- Relationship type.
- Evidence and sources.
- First-known timestamp.
- Last-updated timestamp.
- Estimated strength.
- Confidence and uncertainty.
- Applicable market conditions.
- Historical predictive performance.

Distinguish verified business relationships from statistical correlations and unverified causal hypotheses.

Discovery and learning

Allow the Trader to discover relationships through available historical data.

For example, a commodity price change might affect a supplier's costs, which affects a manufacturer's margins and potentially the competitive position of other companies.

The Trader should identify these possible chains, generate forecasts, and test whether they provide useful information.

Do not reveal relationships before the information supporting them was available in historical time.

Do not assume that correlations imply causation.

Predictive validation

For every potentially useful relationship, record:

- Hypothesis.
- Evidence.
- Identification date.
- Affected assets.
- Forecast direction and horizon.
- Actual outcome.
- Net predictive value where relevant.
- Performance relative to existing models.
- Stability across later periods.

Retire relationships that fail to generalize.

Strategy integration

Allow the Trader to use the relationship graph when creating and testing its own strategies.

It may develop strategies using related-company movements, supplier exposures, sector relationships, economic transmission mechanisms, and combinations of discovered signals.

The graph must influence actual research and predictions. It must not be merely a visual network with no connection to the learning engine.

12. COUNTERFACTUAL INVESTIGATOR

Build an investigator that examines major losses, poor weekly grades, and significant forecast errors.

It should investigate:

- Whether a different position size would have improved the result.
- Whether another asset offered a better risk-adjusted opportunity.
- Whether holding cash would have been preferable.
- Whether entry or exit timing contributed to the loss.
- Whether the loss came from forecasting, execution, exposure, or unexpected events.
- Whether the original decision was reasonable given the available information.

Distinguish decision quality from realized outcome.

Counterfactual outcomes must be labeled as alternative scenarios. They must never be inserted into the Trader's historical knowledge as if the Trader had actually observed them.

Use findings to generate testable hypotheses, not automatic strategy changes.

13. PREDICTION CALIBRATION

Record every forecast before its outcome.

Track:

- Directional accuracy.
- Brier scores where appropriate.
- Probability calibration.
- Forecast error by time horizon.
- Performance by market regime.
- Confidence versus actual success rate.
- Accuracy of expected return estimates.

Identify overconfidence, underconfidence, and situations in which predictions become unreliable.

Do not reward the Trader for making confident predictions without evidence.

14. ADVERSARIAL AUDITOR

Build an independent Auditor that attempts to find flaws in the system.

It must investigate:

- Future information leaks.
- Incorrect timestamps.
- Accounting errors.
- Survivorship bias.
- Missing transaction costs.
- Overfitting.
- Invalid benchmark comparisons.
- Grade manipulation.
- Data corruption.
- Unsupported causal explanations.
- Unreliable market relationships.
- Strategy changes that fail validation.

The Auditor must be able to run tests using deliberately injected faults.

It may block a strategy promotion when a mandatory test fails.

It must not alter historical truth, award grades, or secretly change the Trader's forecasts.

Display all findings in the dashboard.

15. HISTORICAL EVENT MEMORY

Create a searchable database of historical market events.

Store, where available:

- Event type.
- Publication timestamp.
- Relevant companies and sectors.
- Economic context.
- Market conditions.
- Available prior expectations.
- Actual subsequent outcomes.
- Source reliability.
- Historical data limitations.

When the Trader encounters a similar event, allow it to retrieve relevant examples from its available past.

The Trader must compare contexts and uncertainty rather than blindly copying previous outcomes.

Never fabricate historical news or present synthetic examples as authentic.

16. CAUSAL RESEARCH ENGINE

Build a research component that investigates competing explanations for price movements.

For example, when a stock falls after earnings, investigate whether the move coincided with:

- Weak guidance.
- Disappointing revenue.
- A broad market selloff.
- Rising bond yields.
- Analyst estimate revisions.
- Expectations already reflected in the price.

Label results as established facts, supported hypotheses, or unverified possibilities.

Where practical, test whether an event provides predictive information beyond ordinary market movements and existing features.

Do not treat temporal correlation as proof of causation.

17. CONTROLLED STRATEGY EVOLUTION

Allow the Trader to improve its own strategies, features, parameters, and models through a controlled research pipeline.

Each week, it should:

1. Diagnose the largest sources of poor performance.
2. Formulate testable hypotheses.
3. Select experiments worth the computational cost.
4. Train candidate models using permitted data.
5. Validate candidates on chronologically later data.
6. Include transaction costs and risk metrics.
7. Compare candidates with the champion and baseline.
8. Submit promising candidates for Auditor review.
9. Promote or reject candidates based on predefined rules.
10. Preserve previous versions for rollback.

The Trader may propose code changes, but must not directly modify its grading engine, information firewall, risk manager, permissions, or acceptance criteria.

Never train on the final test period and then claim that period proves generalization.

18. INNOVATION AND COMPUTATIONAL BUDGET

Give the Trader a configurable weekly computational budget for research.

It must decide which experiments are worth running.

Track:

- Compute time.
- Experiments completed.
- Experiments abandoned.
- Data usage.
- Model complexity.
- Improvement per unit of compute.
- Cost of external services, if any.

Prefer experiments with clear hypotheses and measurable outcomes.

Prevent unlimited generation of redundant strategies and untested code.

The Trader should learn to allocate its research effort efficiently while remaining within developer-defined resource limits.

19. SHADOW TRADER AND CHAMPION SYSTEM

Run a shadow copy of the Trader alongside the currently approved version.

The champion is the approved strategy or strategy-selection system.

The challenger independently evaluates the same permitted information and generates its own predictions and simulated orders.

Compare them using identical execution assumptions.

Measure:

- Net return.
- Drawdown.
- Risk-adjusted performance.
- Calibration.
- Stability.
- Turnover.
- Transaction costs.
- Performance across market regimes.
- Out-of-sample results.

Do not automatically replace the champion with a challenger that achieved a higher historical return.

Require predefined acceptance tests and Auditor approval.

Preserve all historical versions and rollback capability.

20. LIVE PAPER-TRADING TRANSITION

After historical validation, support a separate live paper-trading mode.

The live system must receive current prices and news as they become available.

It must not receive future historical outcomes or Oracle-only data.

Record predictions before outcomes occur. Use simulated orders and realistic execution assumptions.

Keep historical simulation and live paper trading isolated.

Do not connect real brokerage credentials or execute real-money orders.

The transition must require explicit developer authorization after the historical simulator, accounting, information firewall, and Auditor have passed their mandatory tests.

21. LIVE CONTROL UI — REQUIRED

Build a functioning graphical interface connected to the actual simulation backend.

Prefer a lightweight local web dashboard accessible through a browser on Windows.

The interface must display live updates without requiring manual page refreshes.

The simulation backend must continue running if the browser closes or reconnects.

A. Main dashboard

Display:

- Current historical date.
- Actual date and time.
- Simulation speed.
- Running, paused, stopped, or recovering state.
- Current weekly grade.
- Survival status.
- Starting capital of $1,000.
- Current equity and cash.
- Net return.
- Current drawdown.
- Open positions.
- Recent trades.
- Latest information released to the Trader.
- Current model version.
- Current strategy status.
- Next grading event.

Use actual calculated data, never fabricated placeholder values.

B. Simulation controls

Provide working controls for:

- Start.
- Pause.
- Resume.
- Stop.
- Restart from checkpoint.
- Advance one historical trading day.
- Advance one historical week.
- Change simulation speed.
- Change historical date range.
- Save checkpoint.
- Export reports.
- Enable accelerated evaluation mode.
- Stop all new simulated orders.

Require confirmation before destructive resets.

C. Trader intelligence screen

Show:

- Current forecasts.
- Probability estimates.
- Candidate assets.
- Expected returns and downside.
- Supporting and opposing evidence.
- Decision reasoning.
- Available information at the decision timestamp.
- Open positions and proposed orders.
- Detected patterns.
- Market regimes.
- Historical examples used in research.

D. Strategy laboratory

Show every discovered strategy and experiment.

Display:

- Name and version.
- Hypothesis.
- Creation date.
- Training and validation periods.
- Returns after costs.
- Drawdown.
- Risk-adjusted performance.
- Calibration.
- Trading frequency.
- Applicable market regimes.
- Experimental, approved, retired, or rejected status.
- Promotion or rejection reasons.

Allow the developer to inspect, compare, pause, and retire strategies.

Do not allow silent bypass of validation requirements.

E. Market relationship map screen

Build an interactive graph visualization.

Allow the developer to:

- Search for companies, stocks, sectors, commodities, and economic indicators.
- Select a node and inspect its connections.
- Filter by relationship type.
- Filter by historical date.
- View relationship strength and uncertainty.
- Inspect the supporting evidence and sources.
- View the date a relationship first became known.
- Compare historical correlations.
- See which relationships contributed to a forecast.
- Inspect the predictive performance of a relationship.
- Distinguish verified business connections from statistical hypotheses.
- View multi-step chains of potential economic impact.

Use different visual encodings for relationship types and confidence, with a clear legend.

The visualization must be connected to the actual relationship database. It must not invent edges or expose future relationships to the Trader.

F. Grade and survival screen

Show:

- Current grade.
- Historical grade chart.
- Each scoring category.
- Grade changes and causes.
- Consecutive warning weeks.
- Current survival status.
- Benchmark comparisons.
- Weekly reviews.
- Improvement priorities.

Grades must come from the independent scoring engine.

G. Oracle and historical replay screen

Provide a developer-only view of the Oracle's complete historical knowledge.

Allow comparisons of:

- What the Trader knew.
- What it predicted.
- What actually happened.
- How the result was scored.
- Whether information-barrier violations occurred.

The Oracle's future information must never be accessible through Trader-facing API responses, frontend state, browser storage, or Trader-accessible logs.

H. Learning and experiment screen

Show:

- Model versions.
- Training history.
- Experiment results.
- Accepted and rejected hypotheses.
- Champion and shadow comparisons.
- Out-of-sample performance.
- Rollbacks.
- Known weaknesses.
- Auditor findings.
- Data quality.

I. Event timeline

Display timestamped news and market events.

Allow filtering by date, asset, sector, event type, and source.

Clearly distinguish information already available to the Trader from future outcomes that remain private.

J. Audit and system health screen

Display:

- Data-source status.
- Last successful update.
- Missing-data warnings.
- Simulation errors.
- Failed tests.
- Information-barrier violations.
- Accounting checks.
- Model promotion history.
- CPU and memory usage.
- Checkpoint status.
- System logs.

Make it easy to determine whether the system is actually running or displaying stale information.

K. UI engineering requirements

Implement:

- A persistent backend independent of the browser.
- A documented interface between dashboard and simulation engine.
- Live updates using WebSockets, server-sent events, or an appropriate equivalent.
- Safe localhost-only access or suitable authentication.
- Input validation and permission checks.
- Responsive layouts for desktop and mobile.
- Persistent configuration and simulation state.
- Automated tests for controls.
- Clear error messages and recovery behavior.

The UI must never modify historical truth, erase grade history, or bypass the information firewall.

22. DATA SOURCES AND STORAGE

Prefer a local-first architecture using:

- Python for simulation and quantitative research.
- DuckDB and Parquet for analytical historical data.
- SQLite or an equivalent transactional store for orders, portfolio state, grades, and experiments.
- Established machine-learning libraries for quantitative models.
- A lightweight dashboard framework.
- A local language model for news interpretation when hardware permits.

Inspect installed hardware and software before choosing specific models.

Use replaceable data-provider adapters.

Do not require paid APIs or credit cards to run the core system.

Respect data licenses and provider restrictions.

Maintain a data inventory that documents:

- Historical years covered.
- Asset universe.
- Delisted-stock coverage.
- Point-in-time financial data.
- Historical news availability.
- Publication timestamp quality.
- Corporate-action handling.
- Missing fields.
- Data provenance.
- Usage restrictions.

Do not claim to have complete market data unless verified.

23. TESTING AND ACCEPTANCE CRITERIA

Before declaring the project complete, verify all of the following:

1. The Trader cannot access future data.
2. News appears only after its availability timestamp.
3. Forecasts are locked before outcomes are revealed.
4. Portfolio accounting reconciles.
5. Dividends and splits are handled correctly.
6. Transaction costs are included.
7. The Trader can create and test new strategies.
8. Failed experiments do not replace approved models automatically.
9. Grades are independently calculated.
10. The Trader cannot modify grades or delete failed predictions.
11. The Auditor detects deliberately injected information leaks.
12. Identical deterministic runs produce reproducible results.
13. Changing simulation speed does not change trading results.
14. The UI reflects the actual backend state.
15. Closing the dashboard does not corrupt or stop the simulation.
16. Checkpoint recovery works.
17. Historical and live modes remain isolated.
18. Missing data is reported honestly.
19. A complete small-scale historical simulation runs successfully.
20. The market relationship map reflects actual stored relationships.
21. The Trader can use relationship features in research.
22. Relationship discovery does not leak future information.
23. Relationship hypotheses are tested out of sample.
24. Starting capital is exactly $1,000.
25. The risk manager prevents orders that breach configured limits.
26. Weekly grading uses actual elapsed time outside accelerated evaluation mode.
27. The dashboard's grade matches the authoritative scoring engine.
28. Champion and shadow comparisons use equivalent assumptions.
29. Model promotion is blocked when required tests fail.
30. All critical errors are logged and recoverable.

Run a short smoke test before the full historical replay.

Do not declare the system ready merely because it starts successfully. Verify its accounting, information boundaries, learning behavior, grading, and UI integration.

24. DEVELOPMENT ORDER

Build in the following order:

1. Inspect the existing project, operating system, hardware, dependencies, and available storage.
2. Preserve existing working components.
3. Establish the project structure, configuration, logs, and checkpoints.
4. Implement the historical clock and data interfaces.
5. Implement the Oracle and information firewall.
6. Implement portfolio accounting, risk controls, and simulated execution.
7. Implement the Trader's forecasting and decision interface.
8. Implement the weekly grading and survival engine.
9. Implement strategy creation, experimentation, and evaluation.
10. Implement model versioning and champion/shadow comparisons.
11. Implement the market regime detector and prediction calibration.
12. Implement the market relationship discovery graph.
13. Connect discovered relationships to strategy research.
14. Implement historical event memory and causal research.
15. Implement counterfactual investigation.
16. Implement the adversarial Auditor.
17. Implement controlled strategy evolution and the computational budget.
18. Build the complete live control dashboard.
19. Connect the UI to the actual backend and test all controls.
20. Add historical news and social analysis as reliable data permits.
21. Run automated acceptance tests.
22. Complete a small historical replay.
23. Fix defects and produce an actual test report.
24. Expand the historical universe and data coverage.
25. Add live paper trading only after historical validation succeeds.

Do not build every advanced AI component simultaneously. Use modular interfaces so components can be developed and tested independently.

25. FINAL DELIVERABLES

Provide:

- Actual source files.
- Project directory.
- Working launch command.
- Installation and dependency instructions.
- Working live-control UI.
- Starting capital configuration set to $1,000.
- Data sources and documented limitations.
- Grading formula and survival rules.
- Strategy research and promotion workflow.
- Market relationship map.
- Auditor test results.
- Acceptance-test results.
- Sample weekly report from an actual test.
- Demonstration of strategy creation and validation.
- Demonstration of the information firewall.
- Demonstration of dashboard controls.
- Backup and recovery instructions.
- Known bugs and incomplete components.
- External dependencies or costs, if any.
- Recommended next steps.

Do not claim that the Trader predicts markets accurately simply because the software runs.

Do not connect a real brokerage account or place real-money trades.

Do not claim a feature is complete unless it has been implemented and tested.

If a feature cannot be completed with the available hardware, permissions, data, or free services, explain the limitation and implement the best working alternative.

FINAL DIRECTIVE

Start by inspecting the current environment and producing a concise implementation checklist. Then begin building the actual project.

The final system must be a functioning, locally controllable market simulator in which an autonomous Trader starts with $1,000, discovers its own trading strategies, learns from historical outcomes without future information, receives independent weekly grades, investigates market relationships, evolves through controlled experiments, and can eventually operate in live paper-trading mode.

The Oracle, grading engine, risk manager, Auditor, and developer-controlled UI must remain independent safeguards around the Trader.

Build the system incrementally, verify each critical component, and report actual results rather than simulated claims of success.