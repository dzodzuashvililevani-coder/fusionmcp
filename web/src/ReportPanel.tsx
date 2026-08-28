import type { CheckModel, Report } from "./api";

type ReportPanelProps = {
  report: Report | null;
  showFailureBanner: boolean;
};

export default function ReportPanel({ report, showFailureBanner }: ReportPanelProps) {
  if (!report) {
    return <div className="report-empty">Waiting for report data.</div>;
  }

  const counts = countChecks(report.checks);

  return (
    <div className="report-panel">
      <div className="headline-grid">
        {report.headline.map((item) => (
          <div className="headline-stat" key={item.label}>
            <span>{item.label}</span>
            <strong>
              {item.value}
              {item.unit ? <small>{item.unit}</small> : null}
            </strong>
          </div>
        ))}
      </div>

      {showFailureBanner && counts.fail > 0 ? (
        <div className="notice notice-fail">
          <strong>FAIL</strong>
          <span>Design does not validate and measurement was saved.</span>
        </div>
      ) : null}

      <div className="check-list">
        {report.checks.map((check) => (
          <article className="check-row" key={`${check.name}-${check.detail}`}>
            <span className="check-tag" data-status={check.status}>
              {check.status}
            </span>
            <div>
              <h3>{check.name}</h3>
              <p>{check.detail}</p>
            </div>
          </article>
        ))}
      </div>

      <div className="tally-row">
        <span className="ok-text">{counts.ok} passed</span>
        <span className="warn-text">{counts.warn} warnings</span>
        <span className="fail-text">{counts.fail} failures</span>
      </div>
    </div>
  );
}

function countChecks(checks: CheckModel[]) {
  return checks.reduce(
    (counts, check) => {
      counts[check.status] += 1;
      return counts;
    },
    { ok: 0, warn: 0, fail: 0 }
  );
}
