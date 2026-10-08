import {useEffect, useMemo, useState} from "react";
import "./styles.css";

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

type PreferenceItem = {
  id: string;
  label: string;
  material: string;
  tone: string;
};

const fallbackItems: PreferenceItem[] = [
  {id: "chair-ash", label: "Ash Lounge Chair", material: "Oiled ash", tone: "calm"},
  {id: "sofa-clay", label: "Clay Modular Sofa", material: "Boucle", tone: "warm"},
  {id: "lamp-brass", label: "Brass Arc Lamp", material: "Brushed brass", tone: "glow"},
  {id: "table-stone", label: "Stone Coffee Table", material: "Travertine", tone: "solid"},
  {id: "rug-moss", label: "Moss Wool Rug", material: "Hand-tufted wool", tone: "soft"},
];

function mapRoundToItems(round: unknown[]): PreferenceItem[] {
  return round.map((item, index) => {
    const id = typeof item === "object" && item !== null && "id" in item ? String(item.id) : `option-${index + 1}`;

    return {
      id,
      label: id
        .split(/[-_]/)
        .filter(Boolean)
        .map((part) => part[0]?.toUpperCase() + part.slice(1))
        .join(" "),
      material: ["Oak", "Linen", "Steel", "Wool", "Ceramic"][index % 5],
      tone: ["calm", "warm", "glow", "solid", "soft"][index % 5],
    };
  });
}

export function App() {
  const [round, setRound] = useState<PreferenceItem[]>(fallbackItems);
  const [status, setStatus] = useState("Ready to tune your room style");
  const [selectedId, setSelectedId] = useState(fallbackItems[0].id);
  const [liked, setLiked] = useState<Set<string>>(() => new Set());

  async function start() {
    setStatus("Curating a new preference round");

    try {
      const response = await fetch(`${API}/preferences/rounds`, {method: "POST"});
      if (!response.ok) {
        throw new Error("Preference service failed");
      }

      const payload = (await response.json()) as {round?: unknown[]};
      const items = mapRoundToItems(payload.round ?? []);
      setRound(items.length > 0 ? items : fallbackItems);
      setSelectedId((items[0] ?? fallbackItems[0]).id);
      setStatus("Choose the pieces that feel closest to your room");
    } catch {
      setRound(fallbackItems);
      setSelectedId(fallbackItems[0].id);
      setStatus("Showing an offline preview until the API is available");
    }
  }

  useEffect(() => {
    void start();
  }, []);

  const selected = useMemo(() => round.find((item) => item.id === selectedId) ?? round[0], [round, selectedId]);

  function toggleLike(id: string) {
    setLiked((current) => {
      const next = new Set(current);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }

  return (
    <main className="studio-shell">
      <nav className="topbar" aria-label="Primary">
        <a className="brand" href="/">
          <span className="brand-mark" aria-hidden="true" />
          <span>
            <strong>ACIT4040 Studio</strong>
            <small>AI interior design</small>
          </span>
        </a>
        <div className="nav-links" aria-label="Sections">
          <a href="#preferences">Preference Lab</a>
          <a href="#preview">Design Preview</a>
          <a href="#insights">Insights</a>
        </div>
      </nav>

      <section className="hero-panel" aria-labelledby="studio-title">
        <div>
          <p className="eyebrow">Adaptive room planning</p>
          <h1 id="studio-title">Shape a room that understands your taste.</h1>
          <p className="hero-copy">
            Compare furniture candidates, tune material direction, and preview a calmer layout in one focused
            workspace.
          </p>
        </div>
        <div className="hero-actions">
          <button className="primary-action" onClick={start} type="button">
            New Preference Round
          </button>
          <span className="status-pill" role="status">
            {status}
          </span>
        </div>
      </section>

      <section className="workspace-grid" aria-label="Interior design workspace">
        <aside className="workflow-panel" aria-labelledby="workflow-title">
          <p className="panel-kicker">Workflow</p>
          <h2 id="workflow-title">Room Brief</h2>
          <dl className="brief-list">
            <div>
              <dt>Room</dt>
              <dd>Living room</dd>
            </div>
            <div>
              <dt>Goal</dt>
              <dd>Quiet social space</dd>
            </div>
            <div>
              <dt>Constraints</dt>
              <dd>Clear walkways, balanced lighting</dd>
            </div>
          </dl>
          <div className="metric-row">
            <span>
              <strong>{liked.size}</strong>
              liked
            </span>
            <span>
              <strong>{round.length}</strong>
              options
            </span>
          </div>
        </aside>

        <section className="preference-lab" id="preferences" aria-labelledby="preference-title">
          <div className="section-heading">
            <div>
              <p className="panel-kicker">Preference Lab</p>
              <h2 id="preference-title">Material Harmony</h2>
            </div>
            <p>Pick the pieces that match the room mood. Your choices guide the next layout pass.</p>
          </div>

          <div className="preference-grid">
            {round.map((item) => {
              const isSelected = item.id === selectedId;
              const isLiked = liked.has(item.id);

              return (
                <article className={`preference-card tone-${item.tone}`} key={item.id}>
                  <button
                    aria-pressed={isSelected}
                    className="card-preview"
                    onClick={() => setSelectedId(item.id)}
                    type="button"
                  >
                    <span className="furniture-shape" aria-hidden="true" />
                    <span className="card-id">{item.id}</span>
                  </button>
                  <div className="card-body">
                    <div>
                      <h3>{item.label}</h3>
                      <p>{item.material}</p>
                    </div>
                    <div className="card-actions">
                      <button className={isLiked ? "choice-button active" : "choice-button"} onClick={() => toggleLike(item.id)} type="button">
                        Like
                      </button>
                      <button className="choice-button quiet" onClick={() => setSelectedId(item.id)} type="button">
                        Inspect
                      </button>
                    </div>
                  </div>
                </article>
              );
            })}
          </div>
        </section>

        <aside className="preview-panel" id="preview" aria-labelledby="preview-title">
          <div className="section-heading compact">
            <div>
              <p className="panel-kicker">Design Preview</p>
              <h2 id="preview-title">{selected?.label ?? "Selected Piece"}</h2>
            </div>
          </div>
          <div className="room-canvas" role="img" aria-label="Stylized room preview">
            <span className="canvas-window" />
            <span className="canvas-sofa" />
            <span className="canvas-table" />
            <span className="canvas-rug" />
            <span className="canvas-lamp" />
          </div>
          <div className="insight-list" id="insights">
            <div>
              <span>Palette Fit</span>
              <strong>92%</strong>
            </div>
            <div>
              <span>Walkway Clearance</span>
              <strong>Good</strong>
            </div>
            <div>
              <span>Next Suggestion</span>
              <strong>{selected?.material ?? "Material"}</strong>
            </div>
          </div>
        </aside>
      </section>
    </main>
  );
}
